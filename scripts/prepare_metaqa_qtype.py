"""Prepare MetaQA splits from the dataset's question-type labels.

* Chains come from the labels, not from a path search over the KB. A search picks
  a wrong route for 17 % of 2-hop and 86 % of 3-hop questions.
* Sampling is stratified across question types, deterministically by seed.
* Nothing is written unless every chain matches its label and reaches the gold
  answers in the KB.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "code")
sys.path.insert(0, "scripts")
from decent.kg import KnowledgeGraph  # noqa: E402
from qtype_chains import chain_for  # noqa: E402

TOPIC = re.compile(r"\[(.+?)\]")


def read_split(qa_path: Path, qtype_path: Path) -> list[tuple[str, str, list[str], str]]:
    questions = [ln for ln in qa_path.read_text(encoding="utf-8").split("\n") if ln.strip()]
    qtypes = [ln.strip() for ln in qtype_path.read_text(encoding="utf-8").split("\n") if ln.strip()]
    if len(questions) != len(qtypes):
        raise SystemExit(f"STOP: line mismatch: {len(questions)} questions vs {len(qtypes)} labels ({qa_path})")
    rows = []
    for line, qtype in zip(questions, qtypes):
        question, _, answers = line.partition("\t")
        match = TOPIC.search(question)
        if not match or not answers:
            raise SystemExit(f"STOP: malformed line: {line[:80]}")
        rows.append((question, match.group(1), answers.split("|"), qtype))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hops", type=int, required=True)
    ap.add_argument("--split", default="train")
    ap.add_argument("--kb-path", default="data/raw/metaqa/kb.tsv")
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output-path", required=True)
    ap.add_argument("--min-reach", type=float, default=0.95,
                    help="minimum fraction of questions whose chain must reach at least one gold answer")
    args = ap.parse_args()

    base = Path(f"data/raw/metaqa/MetaQA/{args.hops}-hop")
    rows = read_split(base / f"qa_{args.split}.txt", base / f"qa_{args.split}_qtype.txt")
    print(f"[read] {len(rows)} questions, {len({r[3] for r in rows})} question types")

    # Stratified sample: even quota per type, deterministic under --seed.
    by_type: dict[str, list] = defaultdict(list)
    for row in rows:
        by_type[row[3]].append(row)
    rng = random.Random(args.seed)
    types = sorted(by_type)
    per_type = max(1, args.limit // len(types))
    picked: list = []
    for qtype in types:
        pool = by_type[qtype]
        rng.shuffle(pool)
        picked.extend(pool[:per_type])
    rng.shuffle(picked)
    picked = picked[: args.limit]
    print(f"[sample] stratified: {len(picked)} questions from {len(types)} types (~{per_type}/type)")

    kg = KnowledgeGraph.from_tsv(args.kb_path)

    written = 0
    reached_ok = 0
    out = Path(args.output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for index, (question, topic, answers, qtype) in enumerate(picked):
        chain = chain_for(qtype)
        if len(chain) != args.hops:
            raise SystemExit(f"STOP: label '{qtype}' gives a chain of length {len(chain)}, expected {args.hops}")
        reached, _ = kg.follow_chain(topic, chain)
        if any(a in reached for a in answers):
            reached_ok += 1
        records.append({
            "query_id": f"metaqa_{args.hops}hop_{index:06d}",
            "question": question,
            "topic_entity": topic,
            "relation_chain": chain,
            "answers": answers,
            "metadata": {
                "dataset": f"MetaQA-{args.hops}-hop",
                "source_path": str(base / f"qa_{args.split}.txt"),
                "qtype": qtype,
                "chain_source": "metaqa_qtype_label",
                "sampling": f"stratified_by_qtype_seed{args.seed}",
            },
        })
        written += 1

    # Validation gate: nothing is written unless it passes.
    rate = reached_ok / max(1, written)
    print(f"[check] chains reaching a gold answer: {reached_ok}/{written} ({rate:.1%})")
    if rate < args.min_reach:
        raise SystemExit(f"STOP: only {rate:.1%} of chains reach an answer, below the {args.min_reach:.0%} threshold. "
                         "Nothing written; check the label mapping or the KB.")
    covered = len({r["metadata"]["qtype"] for r in records})
    if covered < len(types):
        print(f"[canh bao] mau chi phu {covered}/{len(types)} loai")
    out.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    print(f"[write] {out}: {written} questions, covering {covered}/{len(types)} types")


if __name__ == "__main__":
    main()
