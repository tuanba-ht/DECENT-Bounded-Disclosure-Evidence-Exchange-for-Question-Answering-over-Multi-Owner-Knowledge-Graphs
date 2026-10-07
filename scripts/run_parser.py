"""Run the LLM parser agent over a prepared query file and save predicted chains."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "code")
from decent.agents import parse_chains  # noqa: E402
from decent.datasets.metaqa import load_prepared_queries  # noqa: E402
from decent.kg import KnowledgeGraph  # noqa: E402
from decent.llm import DEFAULT_MODEL, LLMConfig, LocalLLM  # noqa: E402


def build_vocab(queries, default_kb: str | None) -> dict[str, list[str]]:
    vocab: dict[str, list[str]] = {}
    cache: dict[str, list[str]] = {}
    for query in queries:
        kb_path = query.metadata.get("kb_path", default_kb)
        if kb_path is None:
            continue
        if kb_path not in cache:
            cache[kb_path] = sorted(KnowledgeGraph.from_tsv(kb_path).by_relation)
        vocab[query.query_id] = cache[kb_path]
    if default_kb and default_kb in cache:
        vocab["__global__"] = cache[default_kb]
    return vocab


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query-path", required=True)
    ap.add_argument("--kb-path")
    ap.add_argument("--output-path", required=True)
    ap.add_argument("--model", default=None, help="defaults to DECENT_MODEL_DIR/qwen3-8b")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--no-4bit", action="store_true")
    ap.add_argument("--no-hops-hint", action="store_true")
    args = ap.parse_args()

    queries = load_prepared_queries(args.query_path, limit=args.limit)
    vocab = build_vocab(queries, args.kb_path)
    model_path = args.model or DEFAULT_MODEL
    llm = LocalLLM(LLMConfig(model_path=model_path, load_in_4bit=not args.no_4bit, batch_size=args.batch_size))

    started = time.time()
    records = parse_chains(llm, queries, vocab, hops_hint=not args.no_hops_hint)
    elapsed = time.time() - started

    out = Path(args.output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    exact = sum(1 for r in records if r["exact_chain_match"]) / len(records)
    empty = sum(1 for r in records if not r["predicted_chain"]) / len(records)
    print(json.dumps({
        "model": model_path,
        "n": len(records),
        "exact_chain_accuracy": round(exact, 4),
        "empty_rate": round(empty, 4),
        "seconds": round(elapsed, 1),
        "sec_per_query": round(elapsed / len(records), 2),
    }, indent=2))


if __name__ == "__main__":
    main()
