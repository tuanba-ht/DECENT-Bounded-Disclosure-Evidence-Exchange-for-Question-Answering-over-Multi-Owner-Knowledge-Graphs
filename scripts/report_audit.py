"""Audit reports over finished cells.

1. No-union-view audit: per arm, how often any party saw a complete gold witness
   and how often any party held the union view.
2. Reconstruction adversary: precision and recall of what can be rebuilt from the
   transcript alone.
3. Risk-coverage for abstention.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

RUNS = Path("experiments/runs")

# Only sweep cells; smoke-test directories are skipped.
CELL_RE = re.compile(r"^(webqsp|cwq|metaqa2hop|metaqa3hop)_(hash|relation_family)_n\d+_s\d+$")


def cells(dataset: str | None = None):
    for summary in sorted(RUNS.glob("*/summary.json")):
        name = summary.parent.name
        if not CELL_RE.match(name):
            continue
        if dataset and not name.startswith(dataset + "_"):
            continue
        yield summary.parent


DATASETS = ["webqsp", "cwq", "metaqa2hop", "metaqa3hop"]


def collect(dataset):
    audit = defaultdict(lambda: {"n": 0, "union": 0, "witness": 0})
    adv = defaultdict(lambda: {"n": 0, "prec": 0.0, "rec": 0.0, "recon": 0.0})
    risk = defaultdict(lambda: {"n": 0, "abstained": 0, "f1_answered": 0.0, "answered": 0})

    for cell in cells(dataset):
        for path in sorted(cell.glob("*.jsonl")):
            arm = path.stem
            for line in path.open():
                r = json.loads(line)
                a = audit[arm]
                a["n"] += 1
                a["union"] += int(bool(r["audit_summary"].get("union_violation")))
                a["witness"] += int(bool(r["audit_summary"].get("witness_violation")))
                k = risk[arm]
                k["n"] += 1
                if r["abstained"]:
                    k["abstained"] += 1
                else:
                    k["answered"] += 1
                    k["f1_answered"] += r["answer_f1"]
        s = json.loads((cell / "summary.json").read_text())
        for arm, entry in s["methods"].items():
            rep = entry.get("adversary")
            if not rep:
                continue
            d = adv[arm]
            d["n"] += 1
            d["prec"] += rep.get("disc_I_precision", 0.0)
            d["rec"] += rep.get("disc_I_recall_relevant", 0.0)
            d["recon"] += rep.get("reconstructed_triples", 0)

    return audit, adv, risk


def render(dataset, audit, adv, risk) -> None:
    print()
    print("#" * 78)
    print(f"###  DATASET: {dataset}")
    print("#" * 78)
    print("=" * 78)
    print("1. NO-UNION-VIEW AUDIT")
    print("=" * 78)
    print(f"{'arm':24s} {'records':>9s} {'union violations':>17s} {'witness exposed':>17s}")
    for arm in sorted(audit):
        a = audit[arm]
        flag = "  <-- ceiling, expected" if arm == "single_union" else ("  <-- exposure" if a["witness"] or a["union"] else "")
        print(f"{arm:24s} {a['n']:9d} {a['union']:17d} {a['witness']:17d}{flag}")

    print()
    print("=" * 78)
    print("2. RECONSTRUCTION ADVERSARY (disc_I)")
    print("=" * 78)
    print(f"{'arm':24s} {'precision':>13s} {'recall':>12s} {'recovered':>17s}")
    for arm in sorted(adv):
        d = adv[arm]
        if not d["n"]:
            continue
        print(f"{arm:24s} {d['prec']/d['n']:13.4f} {d['rec']/d['n']:12.4f} {d['recon']/d['n']:17.1f}")

    print()
    print("=" * 78)
    print("3. RISK-COVERAGE UNDER ABSTENTION")
    print("=" * 78)
    print(f"{'arm':24s} {'coverage':>12s} {'F1 on answered':>24s}")
    for arm in sorted(risk):
        k = risk[arm]
        cov = k["answered"] / k["n"] if k["n"] else 0.0
        f1 = k["f1_answered"] / k["answered"] if k["answered"] else float("nan")
        print(f"{arm:24s} {cov:12.4f} {f1:24.4f}")
    print()
    print("Coverage is the fraction of questions the arm did not refuse.")


def main() -> None:
    for dataset in DATASETS:
        audit, adv, risk = collect(dataset)
        if audit:
            render(dataset, audit, adv, risk)


if __name__ == "__main__":
    main()
