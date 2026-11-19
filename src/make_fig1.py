# Journal-quality Figure 1: test perplexity against alpha.
# Each panel is one book and one training size, so a panel compares only
# alpha values inside one cell. The dashed line marks the published alpha,
# 0.4. The open circle marks the alpha chosen on the development slice.

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "fig1_perplexity.png"

def main():
    sweep = list(csv.DictReader((ROOT / "results" / "sweep.csv").open(encoding="utf-8")))
    chosen = {r["book"] + "|" + r["train_tokens"]: float(r["chosen_alpha"])
              for r in csv.DictReader((ROOT / "results" / "chosen.csv").open(encoding="utf-8"))}

    cells = {}
    for r in sweep:
        key = (r["book"], int(r["train_tokens"]))
        cells.setdefault(key, []).append((float(r["alpha"]), float(r["test_pp"])))

    BOOK = {"pride": "Pride and Prejudice", "emma": "Emma"}
    SIZE = {2000: "2,000 tokens", 10000: "10,000 tokens", 50000: "50,000 tokens"}
    BOOKS = ["pride", "emma"]
    SIZES = [2000, 10000, 50000]

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 10,
        "axes.labelsize": 10,
        "axes.edgecolor": "0.25",
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
    })

    fig, axes = plt.subplots(2, 3, figsize=(9.6, 5.4))
    for i, book in enumerate(BOOKS):
        for j, size in enumerate(SIZES):
            ax = axes[i][j]
            pts = sorted(cells[(book, size)])
            alphas = [a for a, _ in pts]
            pps = [p for _, p in pts]
            ax.axvline(0.4, color="0.5", linestyle="--", linewidth=1.0, zorder=1)
            ax.plot(alphas, pps, marker="o", markersize=3.5, linewidth=1.3,
                    color="#1d4e89", zorder=3)
            ca = chosen[book + "|" + str(size)]
            cval = dict(pts)[ca]
            ax.plot([ca], [cval], marker="o", markersize=8.5,
                    markerfacecolor="none", markeredgecolor="#b42318",
                    markeredgewidth=1.5, linestyle="none", zorder=4)
            ax.set_title(BOOK[book] + ", " + SIZE[size])
            ax.set_xticks([0.1, 0.2, 0.4, 0.6, 0.8])
            ax.grid(True, color="0.9", linewidth=0.6, zorder=0)
            ax.tick_params(labelsize=9)
            if j == 0:
                ax.set_ylabel("test perplexity")
            if i == 1:
                ax.set_xlabel("α")

    fig.tight_layout(h_pad=1.4, w_pad=1.2)
    fig.savefig(OUT, dpi=300)
    print("saved", OUT)


if __name__ == "__main__":
    main()
