"""Prepare WebQSP / CWQ from the RoG release (per-question Freebase subgraphs)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq

MAX_HOPS = 3
BEAM = 300


def _iter_rows(parquet_paths: Iterable[str]) -> Iterable[dict[str, Any]]:
    for path in parquet_paths:
        table = pq.read_table(path)
        for row in table.to_pylist():
            yield row


def _best_chain(
    graph: list[list[str]],
    topic: str,
    answers: set[str],
) -> tuple[list[str], float] | None:
    """Beam search for the relation chain that best reproduces the gold answers."""
    forward: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for triple in graph:
        if len(triple) != 3:
            continue
        head, relation, tail = triple
        forward[head].append((relation, tail))
    if topic not in forward:
        return None

    level: list[tuple[tuple[str, ...], frozenset[str]]] = [((), frozenset({topic}))]
    best: tuple[list[str], float] | None = None
    for _ in range(MAX_HOPS):
        expanded: dict[tuple[str, ...], set[str]] = {}
        for chain, frontier in level:
            by_relation: dict[str, set[str]] = defaultdict(set)
            for entity in frontier:
                for relation, tail in forward.get(entity, []):
                    by_relation[relation].add(tail)
            for relation, tails in by_relation.items():
                if len(tails) > 2000:
                    continue
                expanded[chain + (relation,)] = tails
        if not expanded:
            break
        scored = []
        for chain, frontier in expanded.items():
            overlap = len(frontier & answers)
            if overlap:
                precision = overlap / len(frontier)
                recall = overlap / len(answers)
                f1 = 2 * precision * recall / (precision + recall)
                if best is None or f1 > best[1]:
                    best = (list(chain), f1)
            scored.append((overlap, -len(frontier), chain, frontier))
        if best is not None and best[1] >= 0.999:
            break
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        level = [(chain, frozenset(frontier)) for _, _, chain, frontier in scored[:BEAM]]
    return best


def prepare_rog_split(
    parquet_paths: list[str],
    subgraph_dir: str,
    output_path: str,
    dataset: str,
    limit: int | None = None,
    min_chain_f1: float = 0.5,
    max_answers: int = 20,
) -> dict[str, int]:
    subgraphs = Path(subgraph_dir)
    subgraphs.mkdir(parents=True, exist_ok=True)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    total = written = skipped_no_chain = skipped_weak = 0
    with out.open("w", encoding="utf-8") as handle:
        for row in _iter_rows(parquet_paths):
            if limit is not None and written >= limit:
                break
            total += 1
            topics = row.get("q_entity") or []
            answers = {a for a in (row.get("a_entity") or row.get("answer") or []) if a}
            graph = row.get("graph") or []
            if not topics or not answers or not graph:
                skipped_no_chain += 1
                continue
            found = None
            for topic in topics[:2]:
                candidate = _best_chain(graph, topic, answers)
                if candidate and (found is None or candidate[1] > found[1][1]):
                    found = (topic, candidate)
            if found is None:
                skipped_no_chain += 1
                continue
            topic, (chain, chain_f1) = found
            if chain_f1 < min_chain_f1:
                skipped_weak += 1
                continue

            kb_path = subgraphs / f"{row['id']}.tsv"
            with kb_path.open("w", encoding="utf-8") as kb:
                seen: set[tuple[str, str, str]] = set()
                for triple in graph:
                    if len(triple) != 3:
                        continue
                    key = tuple(triple)
                    if key in seen:
                        continue
                    seen.add(key)
                    kb.write("\t".join(triple) + "\n")

            record = {
                "query_id": row["id"],
                "question": row["question"],
                "topic_entity": topic,
                "relation_chain": chain,
                "answers": sorted(answers),
                "metadata": {
                    "dataset": dataset,
                    "kb_path": str(kb_path),
                    "chain_f1": round(chain_f1, 4),
                    "subgraph_size": len(seen),
                    "max_answers": max_answers,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
            written += 1
    return {
        "total_seen": total,
        "written": written,
        "skipped_no_chain": skipped_no_chain,
        "skipped_weak_chain": skipped_weak,
    }
