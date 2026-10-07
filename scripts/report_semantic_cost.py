"""Semantic cost: oracle relation chains versus LLM-parsed chains.

Reports macro-F1 in both modes and the gap between them.
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

ORACLE, LLM = Path("experiments/runs"), Path("experiments/runs_llm")
DATASETS = ("webqsp", "cwq", "metaqa1hop", "metaqa2hop", "metaqa3hop")
PARTS = ("hash", "relation_family", "community")
ARM = "decent_hash_Binf"


def collect(root: Path, dataset: str, part: str) -> list[float]:
    out = []
    for seed in (1, 2, 3):
        f = root / f"{dataset}_{part}_n5_s{seed}" / "summary.json"
        if f.exists():
            m = json.loads(f.read_text())["methods"]
            if ARM in m:
                out.append(m[ARM]["avg_f1_new"])
    return out


def main() -> None:
    lines = ["# Semantic cost: oracle relation chains vs LLM-parsed chains", "",
             f"Arm: {ARM}. Each row is the mean over 3 seeds.", "",
             "| dataset | partition | oracle F1 | parser F1 | delta | retained |",
             "|---|---|---|---|---|---|"]
    rows = []
    for ds in DATASETS:
        for part in PARTS:
            o, l = collect(ORACLE, ds, part), collect(LLM, ds, part)
            if not (o and l):
                continue
            mo, ml = st.mean(o), st.mean(l)
            rows.append((ds, part, mo, ml))
            lines.append(f"| {ds} | {part} | {mo:.3f} | {ml:.3f} | {ml - mo:+.3f} | {ml / mo:.1%} |")

    by_ds = {}
    for ds, _, mo, ml in rows:
        by_ds.setdefault(ds, []).append((mo, ml))
    lines += ["", "## By dataset", ""]
    for ds, vals in by_ds.items():
        mo = st.mean(v[0] for v in vals)
        ml = st.mean(v[1] for v in vals)
        lines.append(f"- **{ds}**: {mo:.3f} -> {ml:.3f} ({ml - mo:+.3f}, retained {ml / mo:.0%})")

    out = Path("results/semantic_cost.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-8:]))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
