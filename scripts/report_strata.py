"""Stratified report by owners spanned, with cluster-bootstrap confidence intervals.

Questions are grouped by the minimum number of owners a gold witness spans. Seeds
are not independent observations of a question, so the bootstrap resamples query
ids and carries every seed of a resampled question with it.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "code")
from decent.stats import holm, paired_bootstrap_delta  # noqa: E402

RUNS = Path("experiments/runs")


def load(dataset: str, partition: str, seeds: list[int], arms: list[str], metric: str):
    """-> {arm: {query_id: [value per seed]}}, {query_id: owners_spanned}"""
    values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    spanned: dict[str, int] = {}
    for seed in seeds:
        cell = RUNS / f"{dataset}_{partition}_n5_s{seed}"
        for arm in arms:
            f = cell / f"{arm}.jsonl"
            if not f.exists():
                continue
            for line in f.open():
                r = json.loads(line)
                values[arm][r["query_id"]].append(r[metric])
                if r.get("owners_spanned") is not None:
                    spanned.setdefault(r["query_id"], r["owners_spanned"])
    return values, spanned


def mean_of(per_query: dict[str, list[float]], ids: list[str]) -> list[float]:
    return [sum(per_query[q]) / len(per_query[q]) for q in ids if q in per_query and per_query[q]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--partition", default="hash")
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    ap.add_argument("--metric", default="answer_f1")
    ap.add_argument("--arms", nargs="+", required=True, help="first arm is the reference for deltas")
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    values, spanned = load(args.dataset, args.partition, args.seeds, args.arms, args.metric)
    if not values:
        print("no data found", file=sys.stderr)
        raise SystemExit(1)

    strata: dict[object, list[str]] = defaultdict(list)
    for qid, k in spanned.items():
        strata[k].append(qid)
        strata["ALL"].append(qid)

    reference = args.arms[0]
    rows = []
    print(f"\n{args.dataset} / {args.partition} / seeds {args.seeds} / {args.metric}")
    print(f"reference = {reference}; 95% cluster-bootstrap CI over query_id, {args.replicates} replicates\n")
    for key in sorted(strata, key=lambda k: (k == "ALL", k)):
        ids = sorted(set(strata[key]))
        label = f"{key} owner(s) spanned" if key != "ALL" else "ALL (pooled)"
        print(f"  {label}  (n = {len(ids)} questions)")
        pvals = {}
        for arm in args.arms:
            vals = mean_of(values[arm], ids)
            if not vals:
                continue
            if arm == reference:
                from decent.stats import bootstrap_mean

                ci = bootstrap_mean(vals, replicates=args.replicates, seed=7)
                print(f"      {arm:22s} {ci}")
                rows.append([args.dataset, args.partition, label, len(ids), arm, ci.point, ci.low, ci.high, "", ""])
            else:
                ref = mean_of(values[reference], ids)
                d, p = paired_bootstrap_delta(vals, ref, replicates=args.replicates, seed=7)
                pvals[arm] = p
                print(f"      {arm:22s} delta {d}  p={p:.4f}")
                rows.append([args.dataset, args.partition, label, len(ids), arm,
                             sum(vals) / len(vals), "", "", f"{d}", p])
        if pvals:
            adj = holm(pvals)
            flags = ", ".join(f"{a}: p_holm={adj[a][0]:.4f}{' *' if adj[a][1] else ''}" for a in pvals)
            print(f"      Holm: {flags}")
        print()

    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["dataset", "partition", "stratum", "n", "arm", "mean", "ci_low", "ci_high", "delta_vs_ref", "p"])
            w.writerows(rows)
        print(f"wrote {args.csv}")


if __name__ == "__main__":
    main()
