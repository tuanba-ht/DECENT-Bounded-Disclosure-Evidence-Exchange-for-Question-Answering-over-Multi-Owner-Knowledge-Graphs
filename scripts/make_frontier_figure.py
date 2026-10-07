"""Budget sweep figure on MetaQA-2: macro-F1 and adversary recall against the budget.

Pooled values are read from each cell's summary.json.
"""
from __future__ import annotations

import json
from collections import defaultdict
from glob import glob
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK = "#16181d"
MUTED = "#6f747c"
RULE = "#dcdfe4"
ANS = "#1f5fa8"
ADV = "#e07b39"
SERIF = ["Linux Libertine O", "Libertine", "DejaVu Serif"]

plt.rcParams.update({
    "font.family": "serif", "font.serif": SERIF, "font.size": 7.6,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Linux Libertine O",
    "mathtext.it": "Linux Libertine O:italic",
    "mathtext.bf": "Linux Libertine O:bold",
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": RULE,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

DATASET = "metaqa2hop"


def sweep(ds: str):
    cells = defaultdict(lambda: ([], [], []))
    for d in glob(f"experiments/runs/{ds}_*_n5_s*"):
        methods = json.loads(Path(d, "summary.json").read_text())["methods"]
        for arm, meta in methods.items():
            adv = meta.get("adversary")
            if not arm.startswith("decent_hash_") or not adv:
                continue
            f, r, p = cells[arm]
            f.append(meta["avg_f1_new"])
            r.append(adv["disc_I_recall_relevant"])
            p.append(adv["disc_I_precision"])

    def order(arm: str) -> float:
        b = arm.split("_B")[1]
        return float("inf") if b == "inf" else int(b)

    mean = lambda v: sum(v) / len(v)
    return [(arm.split("_B")[1], mean(cells[arm][0]), mean(cells[arm][1]), mean(cells[arm][2]))
            for arm in sorted(cells, key=order)]


def main() -> None:
    rows = sweep(DATASET)
    labels = ["inf" if b == "inf" else b for b, _, _, _ in rows]
    xs = list(range(len(rows)))
    f1 = [f for _, f, _, _ in rows]
    adv = [a for _, _, a, _ in rows]
    for row in rows:
        print("B=%s F1=%.3f recall=%.3f precision=%.3f" % row)

    fig, ax = plt.subplots(figsize=(3.32, 2.06))
    fig.subplots_adjust(left=0.135, right=0.985, top=0.955, bottom=0.185)

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=RULE, lw=0.5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.fill_between(xs, adv, f1, color=ANS, alpha=0.07, lw=0, zorder=1)
    ax.plot(xs, f1, color=ANS, lw=1.6, marker="o", ms=3.0, zorder=4,
            label="macro-F1 of returned answers")
    ax.plot(xs, adv, color=ADV, lw=1.5, ls=(0, (3.5, 2)), marker="s", ms=3.0,
            zorder=4, label="adversary recall")

    ax.legend(loc="lower right", frameon=False, fontsize=7.2, handlelength=2.0,
              labelspacing=0.32, handletextpad=0.5, borderpad=0.0,
              bbox_to_anchor=(1.0, 0.015), bbox_transform=ax.transAxes)

    ax.set_xlim(-0.25, len(xs) - 0.75)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("per-query disclosure budget $B$", fontsize=7.5, labelpad=1.5)
    ax.set_ylabel("fraction", fontsize=7.5, labelpad=2)
    ax.tick_params(length=2, pad=2, labelsize=7.0)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xticks(xs)
    ax.set_xticklabels(labels)
    ax.minorticks_off()

    out = Path("results")
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "frontier_metaqa2.pdf", bbox_inches="tight", pad_inches=0.015)
    fig.savefig(out / "frontier_metaqa2.png", dpi=300, bbox_inches="tight", pad_inches=0.015)
    print("margin first/last:", round(f1[0] - adv[0], 3), round(f1[-1] - adv[-1], 3))


if __name__ == "__main__":
    main()
