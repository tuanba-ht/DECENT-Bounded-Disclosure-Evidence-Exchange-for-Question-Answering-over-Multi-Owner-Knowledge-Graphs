from __future__ import annotations

import json
import random
import re
from pathlib import Path

from decent.kg import KnowledgeGraph
from decent.partition import hash_partition, relation_family_partition
from decent.types import Triple
from decent.types import QueryExample


def load_prepared_queries(path: str, limit: int | None = None) -> list[QueryExample]:
    examples: list[QueryExample] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            examples.append(
                QueryExample(
                    query_id=record["query_id"],
                    question=record["question"],
                    topic_entity=record["topic_entity"],
                    relation_chain=record["relation_chain"],
                    answers=set(record["answers"]),
                    metadata=record.get("metadata", {}),
                )
            )
            if limit is not None and len(examples) >= limit:
                break
    return examples


def synthesize_path_queries(
    kb_path: str,
    output_path: str,
    num_queries: int = 200,
    max_hops: int = 3,
    seed: int = 13,
    partition_method: str | None = None,
    num_owners: int = 0,
    min_owners_spanned: int = 1,
) -> None:
    rng = random.Random(seed)
    kg = KnowledgeGraph.from_tsv(kb_path)
    entities = sorted({triple.head for triple in kg.triples})
    relation_choices = sorted(kg.by_relation)
    triple_to_owner = _build_triple_owner_map(kg, partition_method, num_owners)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with output.open("w", encoding="utf-8") as handle:
        attempts = 0
        while written < num_queries and attempts < num_queries * 50:
            attempts += 1
            topic = rng.choice(entities)
            hops = rng.randint(1, max_hops)
            chain: list[str] = []
            frontier = {topic}
            evidence = []
            for _ in range(hops):
                relation = rng.choice(relation_choices)
                chain.append(relation)
                frontier, step_evidence = kg.follow_chain(next(iter(frontier)), [relation]) if len(frontier) == 1 else _follow_set(kg, frontier, relation)
                evidence.extend(step_evidence)
                if not frontier:
                    break
            if not frontier:
                continue
            owners_spanned = sorted(
                {
                    triple_to_owner[triple.as_tuple()]
                    for triple in evidence
                    if triple.as_tuple() in triple_to_owner
                }
            )
            if len(owners_spanned) < min_owners_spanned:
                continue
            record = {
                "query_id": f"metaqa_synth_{written:05d}",
                "question": f"Synthetic MetaQA query from {topic} via {' -> '.join(chain)}",
                "topic_entity": topic,
                "relation_chain": chain,
                "answers": sorted(frontier),
                "metadata": {
                    "dataset": "MetaQA-synthetic",
                    "evidence_size": len(evidence),
                    "owners_spanned": owners_spanned,
                    "seed": seed,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
            written += 1


def convert_metaqa_kb(raw_kb_path: str, output_tsv_path: str, add_inverse: bool = True) -> None:
    output = Path(output_tsv_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_kb_path, "r", encoding="utf-8") as src, output.open("w", encoding="utf-8") as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            subject, relation, obj = line.split("|")
            dst.write(f"{subject}\t{relation}\t{obj}\n")
            if add_inverse:
                dst.write(f"{obj}\t{relation}__inv\t{subject}\n")


def prepare_metaqa_split(
    kb_path: str,
    qa_path: str,
    output_path: str,
    hops: int,
    limit: int | None = None,
) -> dict[str, int]:
    kg = KnowledgeGraph.from_tsv(kb_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    written = 0
    skipped = 0
    with open(qa_path, "r", encoding="utf-8") as src, output.open("w", encoding="utf-8") as dst:
        for line_index, line in enumerate(src):
            if limit is not None and written >= limit:
                break
            line = line.strip()
            if not line:
                continue
            total += 1
            question, answers_raw = line.split("\t")
            topic_entity = _extract_topic_entity(question)
            answers = answers_raw.split("|")
            chain = _infer_consensus_chain(kg, topic_entity, answers, hops=hops)
            if chain is None:
                skipped += 1
                continue
            record = {
                "query_id": f"metaqa_{hops}hop_{line_index:06d}",
                "question": question,
                "topic_entity": topic_entity,
                "relation_chain": chain,
                "answers": answers,
                "metadata": {
                    "dataset": f"MetaQA-{hops}-hop",
                    "source_path": qa_path,
                },
            }
            dst.write(json.dumps(record, ensure_ascii=True) + "\n")
            written += 1
    return {"total": total, "written": written, "skipped": skipped}


def _follow_set(kg: KnowledgeGraph, frontier: set[str], relation: str) -> tuple[set[str], list[object]]:
    next_frontier: set[str] = set()
    evidence = []
    for entity in frontier:
        tails, step_evidence = kg.follow_chain(entity, [relation])
        next_frontier.update(tails)
        evidence.extend(step_evidence)
    return next_frontier, evidence


def _extract_topic_entity(question: str) -> str:
    match = re.search(r"\[(.*?)\]", question)
    if not match:
        raise ValueError(f"Could not extract topic entity from question: {question}")
    return match.group(1)


def _infer_consensus_chain(kg: KnowledgeGraph, topic_entity: str, answers: list[str], hops: int) -> list[str] | None:
    chain_counts: dict[tuple[str, ...], int] = {}
    for answer in answers:
        chains = kg.relation_chains_between(topic_entity, answer, hops=hops, limit=50)
        for chain in chains:
            key = tuple(chain)
            chain_counts[key] = chain_counts.get(key, 0) + 1
    if not chain_counts:
        return None
    best_chain, _ = max(chain_counts.items(), key=lambda item: (item[1], item[0]))
    reached, _ = kg.follow_chain(topic_entity, list(best_chain))
    if not any(answer in reached for answer in answers):
        return None
    return list(best_chain)


def _build_triple_owner_map(
    kg: KnowledgeGraph,
    partition_method: str | None,
    num_owners: int,
) -> dict[tuple[str, str, str], str]:
    if not partition_method or num_owners <= 0:
        return {}
    if partition_method == "relation_family":
        partitions = relation_family_partition(kg, num_owners)
    elif partition_method == "hash":
        partitions = hash_partition(kg, num_owners)
    else:
        raise ValueError(f"Unsupported partition method: {partition_method}")

    triple_to_owner: dict[tuple[str, str, str], str] = {}
    for owner, triples in partitions.items():
        for triple in triples:
            triple_to_owner[triple.as_tuple()] = owner
    return triple_to_owner
