"""Export the main results table at the default cell, with a per-stratum breakdown.

Reports accuracy (Hits@1, macro-F1), disclosure (triples, entities, relations,
bytes, owner entropy) and rounds, stratified by the number of owners a gold
witness spans. Comparison arms and ceilings are written as separate blocks.
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

RUNS, BASE = Path("experiments/runs"), Path("experiments/runs_baselines")
PARTS = ("hash", "relation_family", "community")
SEEDS = (1, 2, 3)

COMPARISON = [
    ("single_broker", "Single-Broker", RUNS),
    ("broadcast_all", "Broadcast-all", RUNS),
    ("star_coordinator", "Star coordinator", RUNS),
    ("random_gossip", "Random gossip", RUNS),
    ("oracle_semijoin", "Distributed semijoin", RUNS),
    ("splitrag_adapted", "Neighbourhood retrieval (SPLIT-RAG-style)", BASE),
    ("clause_adapted", "Budgeted 3-agent (CLAUSE-style)", BASE),
    ("asksafely_suppress", "Value suppression (AskSafely-style)", BASE),
    ("decent_hash_B4", "DECENT (B=4)", RUNS),
    ("decent_hash_Binf", "DECENT (unbudgeted)", RUNS),
    ("decent_raw_inf", "DECENT, raw certificates", RUNS),
]
CEILINGS = [
    ("single_union", "Single-Union", RUNS),
    ("centralised_join", "Exact centralised join", BASE),
]
FIELDS = ["answer_f1", "hits_at_1", "disclosed_triples", "disclosed_relations",
          "disclosed_entities", "disclosed_bytes", "owner_entropy", "rounds"]


def gather(root: Path, dataset: str, arm: str):
    """Per-question records for an arm, pooled over partitions and seeds."""
    recs = []
    for part in PARTS:
        for seed in SEEDS:
            f = root / f"{dataset}_{part}_n5_s{seed}" / f"{arm}.jsonl"
            if f.exists():
                recs.extend(json.loads(x) for x in f.open())
    return recs


def block(dataset: str, arms, stratum=None) -> list[str]:
    out = []
    for arm, label, root in arms:
        recs = gather(root, dataset, arm)
        if stratum is not None:
            recs = [r for r in recs if r.get("owners_spanned") == stratum]
        if not recs:
            out.append(f"| {label} | - | - | - | - | - | - | - | - |")
            continue
        m = {f: st.mean(r.get(f, 0) for r in recs) for f in FIELDS}
        out.append(f"| {label} | {m['answer_f1']:.3f} | {m['hits_at_1']:.3f} | "
                   f"{m['disclosed_triples']:.2f} | {m['disclosed_relations']:.2f} | "
                   f"{m['disclosed_entities']:.2f} | {m['disclosed_bytes']:.0f} | "
                   f"{m['owner_entropy']:.3f} | {m['rounds']:.2f} |")
    return out


def main() -> None:
    head = ("| Arm | macro-F1 | Hits@1 | disc triples | disc relations | disc entities | "
            "disc bytes | owner entropy | rounds |\n|---|---|---|---|---|---|---|---|---|")
    lines = ["# Main results at the default cell (n=5 owners, pooled over 3 partitions x 3 seeds)", ""]
    for dataset in ("webqsp", "cwq", "metaqa1hop", "metaqa2hop", "metaqa3hop"):
        if not (RUNS / f"{dataset}_hash_n5_s1" / "summary.json").exists():
            continue
        lines += [f"## {dataset}", "", "### Comparison arms (under the ownership constraint)", "", head]
        lines += block(dataset, COMPARISON)
        lines += ["", "### Ceilings (reference only; these break the ownership constraint)", "", head]
        lines += block(dataset, CEILINGS)

        spans = sorted({r.get("owners_spanned") for r in gather(RUNS, dataset, "decent_hash_Binf")
                        if r.get("owners_spanned")})
        lines += ["", "### Stratified by owners spanned (comparison arms)", ""]
        for stratum in spans:
            n = len([r for r in gather(RUNS, dataset, "decent_hash_Binf")
                     if r.get("owners_spanned") == stratum])
            lines += [f"**{stratum} owner(s) spanned, {n} question-runs**", "", head]
            lines += block(dataset, COMPARISON, stratum=stratum)
            lines.append("")
        lines.append("")
    out = Path("results/main_results.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
