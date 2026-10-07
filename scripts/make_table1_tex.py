"""Emit the main results table as LaTeX for a two-column page.

Keeps macro-F1 and disclosed triples per dataset; the per-stratum breakdown stays
in the Markdown export.
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

RUNS, BASE = Path("experiments/runs"), Path("experiments/runs_baselines")
DS = [("webqsp", "WebQSP"), ("cwq", "CWQ"), ("metaqa1hop", "MetaQA-1"),
      ("metaqa2hop", "MetaQA-2"), ("metaqa3hop", "MetaQA-3")]
COMPARISON = [
    ("single_broker", "Single-Broker", RUNS),
    ("star_coordinator", "Star coordinator", RUNS),
    ("random_gossip", "Random gossip", RUNS),
    ("oracle_semijoin", "Distributed semijoin", RUNS),
    ("splitrag_adapted", "Neighbourhood retrieval", BASE),
    ("clause_adapted", "Budgeted 3-agent", BASE),
    ("asksafely_suppress", "Value suppression", BASE),
    ("broadcast_all", "Broadcast-all", RUNS),
    ("decent_hash_B4", "\\textsc{Decent} ($B{=}4$)", RUNS),
    ("decent_hash_Binf", "\\textsc{Decent}", RUNS),
]
CEIL = [("single_union", "Single-Union", RUNS), ("centralised_join", "Centralised join", BASE)]


def stat(root, ds, arm, field):
    v = []
    for p in ("hash", "relation_family", "community"):
        for s in (1, 2, 3):
            f = root / f"{ds}_{p}_n5_s{s}" / "summary.json"
            if f.exists():
                m = json.loads(f.read_text())["methods"]
                if arm in m:
                    v.append(m[arm][field])
    return st.mean(v) if v else None


def row(arm, label, root, bold=False):
    cells = []
    for ds, _ in DS:
        f1 = stat(root, ds, arm, "avg_f1_new")
        d = stat(root, ds, arm, "avg_disclosed_triples_new")
        if f1 is None:
            cells += ["--", "--"]
        else:
            f1s = f"{f1:.3f}"
            ds_ = f"{d:.2f}" if d < 100 else f"{d:.0f}"
            cells += [f"\\textbf{{{f1s}}}" if bold else f1s,
                      f"\\textbf{{{ds_}}}" if bold else ds_]
    name = f"\\textbf{{{label}}}" if bold else label
    return f"{name} & " + " & ".join(cells) + " \\\\"


def main() -> None:
    L = [r"\begin{table*}[t]", r"\centering",
         r"\caption{Main results at the default cell ($n{=}5$ owners), pooled over three "
         r"partition treatments and three seeds. \emph{F} is macro-F1; \emph{D} is disclosed "
         r"triples per question. Ceilings break the ownership constraint and are reported for "
         r"reference only. Per-stratum breakdowns are in the appendix.}",
         r"\label{tab:main}", r"\small",
         r"\begin{tabular}{l" + "rr" * len(DS) + "}", r"\toprule",
         " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{n}}}" for _, n in DS) + r" \\",
         " ".join(f"\\cmidrule(lr){{{2+2*i}-{3+2*i}}}" for i in range(len(DS))),
         "Arm & " + " & ".join(["F & D"] * len(DS)) + r" \\", r"\midrule",
         r"\multicolumn{" + str(1 + 2 * len(DS)) + r"}{l}{\emph{Comparison arms --- under the ownership constraint}}\\"]
    for arm, label, root in COMPARISON:
        L.append(row(arm, label, root, bold=(arm == "decent_hash_Binf")))
    L += [r"\midrule",
          r"\multicolumn{" + str(1 + 2 * len(DS)) + r"}{l}{\emph{Ceilings --- reference only, these break the constraint}}\\"]
    for arm, label, root in CEIL:
        L.append(row(arm, label, root))
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    out = Path("results/main_results.tex")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(L)} lines)")
    print("\n".join(L[9:22]))


if __name__ == "__main__":
    main()
