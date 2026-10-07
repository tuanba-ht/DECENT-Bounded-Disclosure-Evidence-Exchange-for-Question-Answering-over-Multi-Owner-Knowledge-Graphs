from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from decent.adversary import ShardReconstructionAdversary
from decent.baselines import run_method
from decent.checkpoint import JsonlCheckpoint
from decent.datasets.metaqa import load_prepared_queries
from decent.kg import KnowledgeGraph
from decent.partition import community_partition, hash_partition, relation_family_partition
from decent.protocols import OwnerAgent
from decent.types import QueryExample, Triple


def build_owners(kb_path: str, partition_method: str, num_owners: int, seed: int = 0) -> list[OwnerAgent]:
    kg = KnowledgeGraph.from_tsv(kb_path)
    if partition_method == "relation_family":
        partitions = relation_family_partition(kg, num_owners, seed=seed)
    elif partition_method == "hash":
        partitions = hash_partition(kg, num_owners, seed=seed)
    elif partition_method == "community":
        partitions = community_partition(kg, num_owners, seed=seed)
    else:
        raise ValueError(f"Unsupported partition method: {partition_method}")
    return [OwnerAgent(name=owner, triples=triples) for owner, triples in sorted(partitions.items())]


def _normalise_methods(methods: list[Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for entry in methods:
        if isinstance(entry, str):
            specs.append({"name": entry, "label": entry, "params": {}})
        else:
            name = entry["name"]
            params = entry.get("params", {})
            label = entry.get("label") or name
            specs.append({"name": name, "label": label, "params": params})
    return specs


def _witness(union: KnowledgeGraph, query: QueryExample) -> list[Triple]:
    _, evidence = union.follow_chain(query.topic_entity, query.relation_chain)
    return evidence


def run_experiment(config_path: str) -> dict[str, object]:
    with open(config_path, "r", encoding="utf-8") as handle:
        config = json.load(handle)

    specs = _normalise_methods(config["methods"])
    queries = load_prepared_queries(config["query_path"], limit=config.get("limit"))
    partition_seed = int(config.get("partition_seed", 0))
    owner_cache: dict[str, list[OwnerAgent]] = {}
    union_cache: dict[str, KnowledgeGraph] = {}
    owner_of: dict[str, dict[tuple[str, str, str], str]] = {}

    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {"methods": {}, "config": config}

    for spec in specs:
        label = spec["label"]
        result_path = output_dir / f"{label}.jsonl"
        checkpoint = JsonlCheckpoint(str(result_path))
        completed = checkpoint.completed_ids()
        adversary = ShardReconstructionAdversary()
        relevant: set[tuple[str, str, str]] = set()
        scores: list[float] = []
        disclosures: list[int] = []
        started = time.time()

        for query in queries:
            kb_path = str(query.metadata.get("kb_path", config["kb_path"]))
            if kb_path not in owner_cache:
                owner_cache[kb_path] = build_owners(
                    kb_path=kb_path,
                    partition_method=config["partition_method"],
                    num_owners=config["num_owners"],
                    seed=partition_seed,
                )
                union_cache[kb_path] = KnowledgeGraph(
                    [t for owner in owner_cache[kb_path] for t in owner.kg.triples]
                )
                owner_of[kb_path] = {
                    t.as_tuple(): owner.name
                    for owner in owner_cache[kb_path]
                    for t in owner.kg.triples
                }
            owners = owner_cache[kb_path]
            witness = _witness(union_cache[kb_path], query)
            relevant.update(t.as_tuple() for t in witness)
            if query.query_id in completed:
                continue
            result = run_method(
                method=spec["name"],
                query=query,
                owners=owners,
                params=spec["params"],
                witness_triples=witness,
            )
            record = result.to_record()
            record["label"] = label
            record["owners_spanned"] = len(
                {owner_of[kb_path][t.as_tuple()] for t in witness if t.as_tuple() in owner_of[kb_path]}
            )
            checkpoint.append(record)
            adversary.observe(result.transcript)
            scores.append(result.answer_f1)
            disclosures.append(result.disclosed_triples)

        true_shards = {
            owner.name: {t.as_tuple() for t in owner.kg.triples}
            for owners in owner_cache.values()
            for owner in owners
        }
        entry: dict[str, Any] = {
            "result_path": str(result_path),
            "method": spec["name"],
            "params": spec["params"],
            "new_queries_executed": len(scores),
            "avg_f1_new": (sum(scores) / len(scores)) if scores else 0.0,
            "avg_disclosed_triples_new": (sum(disclosures) / len(disclosures)) if disclosures else 0.0,
            "wall_seconds": round(time.time() - started, 2),
        }
        if scores:
            entry["adversary"] = adversary.report(true_shards, relevant=relevant)
            entry["adversary"].pop("per_owner", None)
        summary["methods"][label] = entry

    summary_path = output_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)
    return summary
