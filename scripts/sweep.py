"""Run one DECENT sweep cell grid and collect per-query records."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "code")
from decent.runner import run_experiment  # noqa: E402

# Budgets are counted in disclosure units, so the useful range grows with chain
# length. MetaQA 3-hop uses a wider grid than the other datasets.
BUDGETS_DEFAULT = [2, 3, 4, 6, 8, 12, None]
BUDGETS_BY_DATASET = {
    # 4 and 12 sit below the feasibility threshold; the rest span up to the unbudgeted run.
    "metaqa3hop": [4, 12, 20, 40, 80, 160, 320, 640, 1280, 2560, None],
}


def budgets_for(dataset: str) -> list[int | None]:
    return BUDGETS_BY_DATASET.get(dataset, BUDGETS_DEFAULT)


def arms(budgets: list[int | None], challenge_rate: float = 0.1) -> list[object]:
    # single_union breaks the ownership constraint. It is a reference ceiling and is
    # reported separately (see baselines.CEILINGS).
    specs: list[object] = [
        "single_broker",
        "broadcast_all",
        "oracle_semijoin",
        "random_gossip",
        "star_coordinator",
        "single_union",
    ]
    for budget in budgets:
        label = f"decent_hash_B{budget if budget is not None else 'inf'}"
        params = {"certificate_mode": "hash", "challenge_rate": challenge_rate}
        if budget is not None:
            params["budget"] = budget
        specs.append({"name": "decent", "label": label, "params": params})
    specs.append({"name": "decent", "label": "decent_raw_inf", "params": {}})
    return specs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--query-path", required=True)
    ap.add_argument("--kb-path", required=True)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--partitions", nargs="+", default=["hash", "relation_family"])
    ap.add_argument("--owner-counts", nargs="+", type=int, default=[5])
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    ap.add_argument("--out-root", default="experiments/runs")
    ap.add_argument(
        "--budgets",
        nargs="+",
        default=None,
        help="Disclosure budgets; 'inf' for the unbudgeted arm. Defaults to the per-dataset grid.",
    )
    args = ap.parse_args()
    if args.budgets is None:
        budgets = budgets_for(args.dataset)
    else:
        budgets = [None if b.lower() in ("inf", "none") else int(b) for b in args.budgets]
    print(f"[sweep] budgets for {args.dataset}: {budgets}", flush=True)

    for partition in args.partitions:
        for owners in args.owner_counts:
            for seed in args.seeds:
                cell = f"{args.dataset}_{partition}_n{owners}_s{seed}"
                cfg = {
                    "kb_path": args.kb_path,
                    "query_path": args.query_path,
                    "partition_method": partition,
                    "num_owners": owners,
                    "partition_seed": seed,
                    "methods": arms(budgets),
                    "output_dir": f"{args.out_root}/{cell}",
                    "limit": args.limit,
                }
                cfg_path = Path("experiments/configs") / f"{cell}.json"
                cfg_path.write_text(json.dumps(cfg, indent=2))
                print(f"[sweep] {cell}", flush=True)
                summary = run_experiment(str(cfg_path))
                for label, entry in summary["methods"].items():
                    print(
                        f"    {label:18s} f1={entry['avg_f1_new']:.3f} "
                        f"discT={entry['avg_disclosed_triples_new']:.2f} {entry['wall_seconds']}s",
                        flush=True,
                    )


if __name__ == "__main__":
    main()
