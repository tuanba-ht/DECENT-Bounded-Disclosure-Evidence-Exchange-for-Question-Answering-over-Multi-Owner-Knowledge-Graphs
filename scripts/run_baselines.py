"""Run the adapted baselines on the same shards as the main sweep.

Uses the same partition function and seeds as sweep.py. ``single_broker`` is run
again as a control: its numbers must match the main sweep.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "code")
from decent.runner import run_experiment  # noqa: E402

METHODS = [
    "single_broker",        # control: must match the main table exactly
    "splitrag_adapted",
    "clause_adapted",
    "asksafely_suppress",
    "centralised_join",     # ceiling, reported separately
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--query-path", required=True)
    ap.add_argument("--kb-path", required=True)
    ap.add_argument("--partitions", nargs="+", default=["hash", "relation_family", "community"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    ap.add_argument("--owners", type=int, default=5)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--out-root", default="experiments/runs_baselines")
    args = ap.parse_args()

    for partition in args.partitions:
        for seed in args.seeds:
            cell = f"{args.dataset}_{partition}_n{args.owners}_s{seed}"
            out = Path(args.out_root) / cell
            if (out / "summary.json").exists():
                print(f"[skip] {cell}", flush=True)
                continue
            cfg = {
                "kb_path": args.kb_path,
                "query_path": args.query_path,
                "partition_method": partition,
                "num_owners": args.owners,
                "partition_seed": seed,
                "methods": METHODS,
                "output_dir": str(out),
                "limit": args.limit,
            }
            cfg_path = Path("experiments/configs") / f"baseline_{cell}.json"
            cfg_path.write_text(json.dumps(cfg, indent=2))
            print(f"[run ] {cell}", flush=True)
            summary = run_experiment(str(cfg_path))
            for label, entry in summary["methods"].items():
                print(f"    {label:20s} f1={entry['avg_f1_new']:.3f} "
                      f"discT={entry['avg_disclosed_triples_new']:.2f} {entry['wall_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
