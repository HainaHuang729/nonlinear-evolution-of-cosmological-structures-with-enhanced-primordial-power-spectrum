"""PS25 BT/PL version, original colours, HMcode and Sim/HM removed; explicit layout spacing."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=BASE.parents[1] / "power-spectrum-btpl.png")
OUT = parser.parse_args().output
OUT.parent.mkdir(parents=True, exist_ok=True)

COLORS = {"PL": "#000000", "BTKP1": "#0072B2", "BTKP10": "#009E73"}
MARKERS = {"PL": "o", "BTKP1": "^", "BTKP10": "s"}
LABELS = {"pl": "PL", "kp1": "BTKP1", "kp10": "BTKP10"}
DISPLAY = {"PL": "PL", "BTKP1": r"BT $k_p=1$", "BTKP10": r"BT $k_p=10$"}
ZLIST = [0.0, 1.0717968600643704, 3.4410805658271204, 8.519850605215494]

spec = defaultdict(list)
for r in csv.DictReader(open(BASE / "spectra.csv")):
    if int(float(r["displayed"])) != 1:
        continue
    spec[(r["model"], round(float(r["redshift"]), 3))].append((float(r["k_hMpc"]), float(r["P_sim"])))
rat = defaultdict(list)
for r in csv.DictReader(open(BASE / "ratios.csv")):
    rat[(r["model"], round(float(r["redshift"]), 3))].append((float(r["k_hMpc"]), float(r["BT_over_PL"])))

fig = plt.figure(figsize=(12.5, 10.5))
outer = fig.add_gridspec(2, 2, left=0.085, right=0.94, bottom=0.075, top=0.895, hspace=0.30, wspace=0.30)
axes = []
for i, z in enumerate(ZLIST):
    inner = outer[i // 2, i % 2].subgridspec(2, 1, height_ratios=[3.0, 1.0], hspace=0.30)
    top = fig.add_subplot(inner[0])
    low = fig.add_subplot(inner[1], sharex=top)
    axes.append((top, low, z))
    for model, label in LABELS.items():
        pts = sorted(spec.get((model, round(z, 3)), []))
        if pts:
            k, p = np.asarray(pts).T
            top.plot(k, p, color=COLORS[label], marker=MARKERS[label], ls="none", ms=3.4, mfc="none")
        pr = sorted(rat.get((model, round(z, 3)), []))
        if pr and model != "pl":
            k, r = np.asarray(pr).T
            low.plot(k, r, color=COLORS[label], marker=MARKERS[label], ls="-", lw=0.9, ms=3.4, mfc="none")
    top.set_xscale("log"); top.set_yscale("log")
    top.set_xlim(2.3, 35.0); top.set_ylim(1e-3, 1e3)
    low.set_xscale("log")
    low.axhline(1.0, color="0.45", lw=0.7, ls=":")
    top.set_title(rf"$z={z:.3f}$", fontsize=11, pad=6)
    for ax in (top, low):
        ax.grid(alpha=0.22, which="both", lw=0.4)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    low.set_xlabel(r"$k\ [h\,\mathrm{Mpc}^{-1}]$", fontsize=10, labelpad=3)
    top.set_yticks([1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0])
    low.yaxis.tick_right()
    low.yaxis.set_label_position("right")
    row_ratios = [value for (model, redshift), points in rat.items()
                  if model != "pl" and redshift == round(z, 3)
                  for k, value in points if 2.3 <= k <= 35.0]
    ratio_max = max(2.0, float(np.ceil(max(row_ratios, default=1.0) * 1.08)))
    low.set_yticks(np.arange(1.0, ratio_max + 0.1, 1.0))
    low.set_ylim(0.8, ratio_max)
    low.tick_params(axis="y", labelsize=8)
    if i % 2 == 0:
        top.set_ylabel(r"$P(k)\ [h^{-3}\,\mathrm{Mpc}^{3}]$", fontsize=10, labelpad=4)
    low.set_ylabel(r"$\mathrm{BT/PL}$", fontsize=10, labelpad=4)
    plt.setp(top.get_xticklabels(), visible=False)

handles = [plt.Line2D([], [], color=COLORS[v], marker=MARKERS[v], ls="none", mfc="none", label=DISPLAY[v]) for v in ("PL", "BTKP1", "BTKP10")]
fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.935))
fig.suptitle("Matter power spectrum and BT/PL ratio (simulations only)", fontsize=12, y=0.975)

fig.canvas.draw()
renderer = fig.canvas.get_renderer()
texts = []
for ax in fig.axes:
    for t in [ax.title, ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels()]:
        if t.get_text().strip() and t.get_visible():
            bb = t.get_window_extent(renderer)
            if bb.width > 1 and bb.height > 1:
                texts.append((t.get_text().strip(), bb))
overlaps = 0
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        a, b = texts[i][1], texts[j][1]
        if a.overlaps(b):
            overlaps += 1
            if overlaps <= 5:
                print("overlap:", repr(texts[i][0]), "<->", repr(texts[j][0]))
fig.savefig(OUT, dpi=250, bbox_inches=None)
print("saved", OUT, "text_overlaps:", overlaps)
