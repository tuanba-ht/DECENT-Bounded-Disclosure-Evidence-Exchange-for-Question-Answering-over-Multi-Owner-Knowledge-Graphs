"""Aggregation for DECENT runs: stratified tables, paired bootstrap CIs, Pareto fronts."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


def load_run(run_dir: str | Path) -> dict[str, list[dict[str, Any]]]:
    run_dir = Path(run_dir)
    arms: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(run_dir.glob("*.jsonl")):
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if rows:
            arms[path.stem] = rows
    return arms


def owners_spanned(row: dict[str, Any]) -> int:
    if "owners_spanned" in row:
        return int(row["owners_spanned"])
    spanned = row.get("metadata", {}).get("owners_spanned")
    if isinstance(spanned, list):
        return len(spanned)
    return int(spanned or 0)


def summarise(rows: Iterable[dict[str, Any]]) -> dict[str, float]:
    rows = list(rows)
    if not rows:
        return {}
    return {
        "n": len(rows),
        "f1": mean(r["answer_f1"] for r in rows),
        "em": mean(r["exact_match"] for r in rows),
        "coverage": mean(r["coverage"] for r in rows),
        "disc_T": mean(r["disclosed_triples"] for r in rows),
        "disc_B": mean(r.get("disclosed_bindings", 0) for r in rows),
        "disc_cost": mean(r.get("disclosure_cost", r["disclosed_triples"]) for r in rows),
        "rounds": mean(r["rounds"] for r in rows),
        "messages": mean(r["messages"] for r in rows),
        "abstain_rate": mean(1.0 if r["abstained"] else 0.0 for r in rows),
        "witness_violation_rate": mean(
            1.0 if r["audit_summary"].get("witness_violation") else 0.0 for r in rows
        ),
        "union_violation_rate": mean(
            1.0 if r["audit_summary"].get("union_violation") else 0.0 for r in rows
        ),
        "owner_entropy": mean(r["owner_entropy"] for r in rows),
    }


def paired_bootstrap(
    arm_a: list[dict[str, Any]],
    arm_b: list[dict[str, Any]],
    field: str = "answer_f1",
    iters: int = 2000,
    seed: int = 7,
) -> dict[str, float]:
    """Paired bootstrap over questions for delta(arm_a - arm_b)."""
    index_b = {row["query_id"]: row for row in arm_b}
    pairs = [(row[field], index_b[row["query_id"]][field]) for row in arm_a if row["query_id"] in index_b]
    if not pairs:
        return {}
    rng = random.Random(seed)
    observed = mean(a - b for a, b in pairs)
    deltas = []
    n = len(pairs)
    for _ in range(iters):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        deltas.append(mean(a - b for a, b in sample))
    deltas.sort()
    lo = deltas[int(0.025 * iters)]
    hi = deltas[int(0.975 * iters) - 1]
    p_two_sided = 2 * min(
        sum(1 for d in deltas if d <= 0) / iters,
        sum(1 for d in deltas if d >= 0) / iters,
    )
    return {"delta": observed, "ci_low": lo, "ci_high": hi, "p": min(1.0, p_two_sided), "n_paired": n}


def pareto_front(points: list[tuple[str, float, float]]) -> list[str]:
    """points = (label, disclosure_cost, accuracy). Lower cost / higher accuracy dominates."""
    front = []
    for label, cost, acc in points:
        dominated = any(
            (other_cost <= cost and other_acc >= acc and (other_cost < cost or other_acc > acc))
            for other_label, other_cost, other_acc in points
            if other_label != label
        )
        if not dominated:
            front.append(label)
    return front


def report(run_dirs: list[str], out_dir: str) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    per_cell: dict[str, dict[str, Any]] = {}
    pooled: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for run_dir in run_dirs:
        arms = load_run(run_dir)
        cell = Path(run_dir).name
        per_cell[cell] = {arm: summarise(rows) for arm, rows in arms.items()}
        for arm, rows in arms.items():
            pooled[arm].extend(rows)

    overall = {arm: summarise(rows) for arm, rows in pooled.items()}

    # Stratify by how many owners a gold witness spans.
    strata: dict[str, dict[str, dict[str, float]]] = {}
    for arm, rows in pooled.items():
        buckets: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            buckets[owners_spanned(row)].append(row)
        strata[arm] = {f"spanned_{k}": summarise(v) for k, v in sorted(buckets.items())}

    # Paired comparisons against the two reference arms.
    comparisons: dict[str, dict[str, Any]] = {}
    for reference in ("broadcast_all", "single_broker", "oracle_semijoin"):
        if reference not in pooled:
            continue
        comparisons[reference] = {
            arm: paired_bootstrap(pooled[arm], pooled[reference])
            for arm in pooled
            if arm != reference
        }

    points = [(arm, stats["disc_cost"], stats["f1"]) for arm, stats in overall.items() if stats]
    front = pareto_front(points)

    csv_lines = ["arm,n,f1,em,coverage,disc_T,disc_B,disc_cost,rounds,messages,abstain_rate,witness_violation_rate,on_pareto_front"]
    for arm, stats in sorted(overall.items(), key=lambda kv: kv[1]["disc_cost"]):
        csv_lines.append(
            ",".join(
                [
                    arm,
                    str(stats["n"]),
                    *[f"{stats[k]:.4f}" for k in ["f1", "em", "coverage", "disc_T", "disc_B", "disc_cost", "rounds", "messages", "abstain_rate", "witness_violation_rate"]],
                    "1" if arm in front else "0",
                ]
            )
        )
    (out / "main_table.csv").write_text("\n".join(csv_lines) + "\n")

    payload = {
        "run_dirs": run_dirs,
        "overall": overall,
        "per_cell": per_cell,
        "stratified_by_owners_spanned": strata,
        "paired_bootstrap_vs": comparisons,
        "pareto_front": front,
    }
    (out / "report.json").write_text(json.dumps(payload, indent=2))
    return payload
