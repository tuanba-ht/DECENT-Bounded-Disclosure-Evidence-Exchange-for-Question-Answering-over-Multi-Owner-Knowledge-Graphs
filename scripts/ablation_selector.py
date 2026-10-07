"""Owner-selector ablation.

Compares coverage-greedy owner selection with three alternatives (lowest marginal
disclosure, lowest latency, random) across budgets.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "code")
from decent.baselines import run_method  # noqa: E402
from decent.datasets.metaqa import load_prepared_queries  # noqa: E402
from decent.runner import build_owners  # noqa: E402
from decent.stats import holm, paired_bootstrap_delta  # noqa: E402

SELECTORS = ["coverage", "marginal_disclosure", "latency", "random"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--query-path", required=True)
    ap.add_argument("--kb-path", default=None)
    ap.add_argument("--partition", default="hash")
    ap.add_argument("--owners", type=int, default=5)
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    ap.add_argument("--budgets", nargs="+", type=int, default=[2, 4, 8, 12])
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--out", default="results/ablation/selector.json")
    args = ap.parse_args()

    queries = load_prepared_queries(args.query_path, limit=args.limit)
    results: dict[str, dict[str, list[float]]] = {}

    shared = None
    if args.kb_path:
        # One KB for the whole dataset: build the shards once instead of per question.
        shared = {seed: build_owners(args.kb_path, args.partition, args.owners, seed=seed) for seed in args.seeds}

    for budget in args.budgets:
        for selector in SELECTORS:
            key = f"B{budget}_{selector}"
            per_query: dict[str, list[float]] = {}
            disclosed: list[float] = []
            for seed in args.seeds:
                owners_cache = shared[seed] if shared else None
                for query in queries:
                    owners = owners_cache or build_owners(
                        query.metadata["kb_path"], args.partition, args.owners, seed=seed
                    )
                    r = run_method(
                        "decent", query, owners,
                        {"certificate_mode": "hash", "challenge_rate": 0.1, "selector": selector, "budget": budget},
                    )
                    per_query.setdefault(query.query_id, []).append(r.answer_f1)
                    disclosed.append(r.disclosed_triples)
            results[key] = {
                "f1_by_query": {q: sum(v) / len(v) for q, v in per_query.items()},
                "disclosed_mean": sum(disclosed) / len(disclosed),
            }
            print(f"  {key:34s} F1={sum(sum(v) / len(v) for v in per_query.values()) / len(per_query):.4f} "
                  f"disclosed={results[key]['disclosed_mean']:.3f}", flush=True)

    # Compare every alternative against marginal_disclosure.
    print(f"\n  Compared with 'marginal_disclosure' (paired bootstrap, {len(queries)} queries):")
    report = {}
    for budget in args.budgets:
        ref = results[f"B{budget}_marginal_disclosure"]["f1_by_query"]
        ids = sorted(ref)
        pvals = {}
        for selector in SELECTORS:
            if selector == "marginal_disclosure":
                continue
            cur = results[f"B{budget}_{selector}"]["f1_by_query"]
            d, p = paired_bootstrap_delta([cur[i] for i in ids], [ref[i] for i in ids], replicates=1500, seed=11)
            pvals[selector] = p
            report[f"B{budget}_{selector}"] = {"delta": d.point, "ci": [d.low, d.high], "p": p}
            print(f"    B{budget:<5d} {selector:22s} delta={d.point:+.4f} CI[{d.low:+.4f},{d.high:+.4f}] p={p:.4f}")
        adj = holm(pvals)
        for selector, (padj, sig) in adj.items():
            report[f"B{budget}_{selector}"]["p_holm"] = padj
            report[f"B{budget}_{selector}"]["significant"] = sig

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "dataset": args.dataset, "partition": args.partition, "owners": args.owners,
        "seeds": args.seeds, "n_queries": len(queries),
        "means": {k: {"f1": sum(v["f1_by_query"].values()) / len(v["f1_by_query"]),
                      "disclosed": v["disclosed_mean"]} for k, v in results.items()},
        "comparisons": report,
    }, indent=2))
    print(f"\n  wrote {out}")


if __name__ == "__main__":
    main()
