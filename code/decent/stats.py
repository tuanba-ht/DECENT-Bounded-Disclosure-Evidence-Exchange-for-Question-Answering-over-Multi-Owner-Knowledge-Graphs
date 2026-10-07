"""Paired bootstrap confidence intervals and Holm correction.

Arms are evaluated on the same questions, so comparisons are paired: question
indices are resampled once per replicate and applied to both arms.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Interval:
    point: float
    low: float
    high: float

    def __str__(self) -> str:
        return f"{self.point:.3f} [{self.low:.3f}, {self.high:.3f}]"


def bootstrap_mean(values: list[float], replicates: int = 2000, seed: int = 0, alpha: float = 0.05) -> Interval:
    if not values:
        return Interval(float("nan"), float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(replicates):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo = means[int(alpha / 2 * replicates)]
    hi = means[min(replicates - 1, int((1 - alpha / 2) * replicates))]
    return Interval(sum(values) / n, lo, hi)


def paired_bootstrap_delta(
    a: list[float], b: list[float], replicates: int = 2000, seed: int = 0, alpha: float = 0.05
) -> tuple[Interval, float]:
    """CI for mean(a) - mean(b) over the same questions, plus a two-sided p-value.

    The p-value is the bootstrap proportion of replicates whose delta falls on the
    opposite side of zero from the observed delta, doubled -- the usual two-sided
    convention. It is never reported below 1/replicates.
    """
    if len(a) != len(b):
        raise ValueError(f"paired comparison needs equal lengths, got {len(a)} and {len(b)}")
    if not a:
        return Interval(float("nan"), float("nan"), float("nan")), float("nan")
    rng = random.Random(seed)
    n = len(a)
    observed = (sum(a) - sum(b)) / n
    deltas = []
    for _ in range(replicates):
        idx = [rng.randrange(n) for _ in range(n)]
        deltas.append(sum(a[i] - b[i] for i in idx) / n)
    deltas.sort()
    lo = deltas[int(alpha / 2 * replicates)]
    hi = deltas[min(replicates - 1, int((1 - alpha / 2) * replicates))]
    opposite = sum(1 for d in deltas if (d <= 0) if observed > 0) or sum(1 for d in deltas if (d >= 0) if observed <= 0)
    p = min(1.0, max(1.0 / replicates, 2.0 * opposite / replicates))
    return Interval(observed, lo, hi), p


def holm(pvalues: dict[str, float], alpha: float = 0.05) -> dict[str, tuple[float, bool]]:
    """Holm-Bonferroni step-down. Returns {name: (adjusted p, significant)}."""
    ordered = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(ordered)
    out: dict[str, tuple[float, bool]] = {}
    running = 0.0
    for rank, (name, p) in enumerate(ordered):
        adjusted = min(1.0, max(running, (m - rank) * p))
        running = adjusted
        out[name] = (adjusted, adjusted <= alpha)
    # Once a hypothesis fails, every later one fails too.
    failed = False
    for name, _ in ordered:
        adj, sig = out[name]
        if failed:
            out[name] = (adj, False)
        elif not sig:
            failed = True
    return out
