"""plot_divergence.py: the figure for the README from divergence.csv.

Usage: python plot_divergence.py divergence.csv <output dir>
Writes divergence-light.png and divergence-dark.png (two small multiples sharing the time axis).
Colors are the first two categorical slots of a validated palette, stepped per mode.
"""
import csv
import sys
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter

src = sys.argv[1] if len(sys.argv) > 1 else "divergence.csv"
out = sys.argv[2] if len(sys.argv) > 2 else "."

t, p_ulp, v_ulp, p_gold, v_gold = [], [], [], [], []
with open(src, newline="") as f:
    for row in csv.DictReader(f):
        t.append(float(row["t_min"]))
        p_ulp.append(float(row["dpitch_ulp_deg"]))
        v_ulp.append(float(row["dvol_ulp_m3"]))
        p_gold.append(float(row["dpitch_golden_deg"]) if row["dpitch_golden_deg"] else math.nan)
        v_gold.append(float(row["dvol_golden_m3"]) if row["dvol_golden_m3"] else math.nan)

# a difference of exactly zero cannot sit on a log axis: leave the gap, it is the point of the figure
nz = lambda xs: [x if x > 0 else math.nan for x in xs]
FIRST_OVERTOP_MIN = 60.8     # water first flows over a bulkhead top (bulkhead C at E deck)
FOUNDER_MIN = 157.3

THEMES = {
    "light": dict(surface="#fcfcfb", text="#0b0b0b", muted="#52514e", grid="#e6e5e1", s1="#2a78d6", s2="#eb6834"),
    "dark":  dict(surface="#1a1a19", text="#ffffff", muted="#c3c2b7", grid="#2e2e2c", s1="#3987e5", s2="#d95926"),
}

for mode, c in THEMES.items():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.edgecolor": c["grid"], "axes.labelcolor": c["text"], "axes.titlecolor": c["text"],
        "xtick.color": c["muted"], "ytick.color": c["muted"], "text.color": c["text"],
        "figure.facecolor": c["surface"], "axes.facecolor": c["surface"], "savefig.facecolor": c["surface"],
    })
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=160, sharex=True)
    panels = [
        (axes[0], p_ulp, p_gold, "Pitch difference, degrees", (1e-17, 1)),
        (axes[1], v_ulp, v_gold, "Flood-water difference, m³ summed over 64 spaces", (1e-14, 1e3)),
    ]
    for ax, ulp, gold, title, ylim in panels:
        ax.set_yscale("log")
        ax.set_ylim(*ylim)
        ax.set_xlim(0, 160)
        ax.grid(True, which="major", color=c["grid"], linewidth=0.8)
        ax.yaxis.set_major_locator(LogLocator(base=10, numticks=8))
        ax.yaxis.set_minor_formatter(NullFormatter())
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.axvline(FIRST_OVERTOP_MIN, color=c["muted"], linewidth=0.8)
        ax.axvline(FOUNDER_MIN, color=c["muted"], linewidth=0.8)
        ax.plot(t, nz(ulp), color=c["s1"], linewidth=2, solid_joinstyle="round", solid_capstyle="round",
                label="one parameter moved by one ulp (CdBreach 0.6 → 0.6000000000000001)")
        ax.plot(t, nz(gold), color=c["s2"], linewidth=2, solid_joinstyle="round", solid_capstyle="round",
                label="same run on two machines (one Math.pow rounded differently)")
        ax.set_title(title, loc="left", fontsize=11, pad=10)
        ax.set_xlabel("minutes after the collision")
        ax.tick_params(length=0)
    # annotations in text tokens, never in the series color; placed in empty regions of each panel
    axes[0].text(FIRST_OVERTOP_MIN + 1.8, 1e-9, "water first flows over\na bulkhead top (61 min)", color=c["muted"], fontsize=8.5, va="bottom")
    axes[0].text(FOUNDER_MIN - 1.8, 1e-9, "founders\n(157 min)", color=c["muted"], fontsize=8.5, va="bottom", ha="right")
    axes[0].text(2, 1e-12, "two machines: identical to the\nlast bit for 72 minutes (no line)", color=c["muted"], fontsize=8.5, va="bottom")
    axes[1].text(FIRST_OVERTOP_MIN + 1.8, 1e-6, "61 min", color=c["muted"], fontsize=8.5, va="bottom")
    axes[1].text(FOUNDER_MIN - 1.8, 1e-6, "157 min", color=c["muted"], fontsize=8.5, va="bottom", ha="right")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("One ulp, two hours later: Titanic flooding model, calibrated 1912 run",
                 x=0.045, y=0.975, ha="left", fontsize=12.5, fontweight="bold", color=c["text"])
    fig.text(0.045, 0.915, "absolute difference between two runs, per minute of simulated time (log scale; exact zeros leave a gap)",
             fontsize=9, color=c["muted"])
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.040, 0.885), frameon=False, ncol=1,
               fontsize=9, labelcolor=c["text"], handlelength=1.8, borderaxespad=0)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.72, bottom=0.13, wspace=0.18)
    path = f"{out}/divergence-{mode}.png"
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)
