"""Paper-style radial DM profiles: PL (black), BTKP1 (blue), BTKP10 (green) with BT/PL ratio."""
import json, sys
from pathlib import Path

import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

P = Path("/oss06/data/project/tkcastrosim/HNHuang/project_big_sim")
SCRIPT_DIR = P / "analysis/_used_by_article_nonlinear_evolution_pps/article_reproducibility_release_2026-07-24/public_data/scripts"
PROF_DIR = P / "analysis/particle_profiles_20261105"
OUT = PROF_DIR / "radial_profiles_particles_paperstyle.png"

sys.path.insert(0, str(SCRIPT_DIR))
import cosmology_plot_style as cps  # noqa: E402

cps.apply_journal_style(8.5)
C = cps.JOURNAL_COLORS

RUNS = {"PL": ("PL", C["black"]), "BTKP1": ("kp1", C["blue"]), "BTKP10": ("kp10", C["green"])}
prof = {}
for label, (tag, colour) in RUNS.items():
    f = PROF_DIR / f"profiles_{tag}.json"
    if not f.exists():
        print("missing", f, flush=True)
        continue
    prof[label] = json.loads(f.read_text())
print("loaded:", list(prof), flush=True)

bins = [1e9, 1e10, 1e11, 1e12]
fig, axes = plt.subplots(4, 2, figsize=(7.4, 6.3),
                         gridspec_kw={"height_ratios": [3.0, 1.05, 3.0, 1.05]},
                         squeeze=False, sharex="col")
for k, mass in enumerate(bins):
    row = 2 * (k // 2)
    col = k % 2
    ax = axes[row, col]
    rax = axes[row + 1, col]
    curves = {}
    for label, rows_all in prof.items():
        rows = [r for r in rows_all if r["mass"] == mass and r["centre"] == "so"]
        if not rows:
            continue
        x = np.array(rows[0]["r_over_r200"])
        arr = np.array([r["rho"] for r in rows]) * 1e-9
        if "count" in rows[0]:
            cnt = np.array([r["count"] for r in rows], float)
            bad = (cnt < 10).sum(0) >= max(1, int(0.5 * len(rows)))
        else:
            bad = np.zeros(len(x), dtype=bool)
        med = np.where(bad, np.nan, np.median(arr, 0))
        lo = np.where(bad, np.nan, np.percentile(arr, 16, 0))
        hi = np.where(bad, np.nan, np.percentile(arr, 84, 0))
        colour = RUNS[label][1]
        ax.plot(x, med, color=colour, lw=1.5, label=label)
        ax.fill_between(x, lo, hi, color=colour, alpha=0.18, lw=0)
        curves[label] = (x, med)
    if "PL" in curves and "BTKP1" in curves:
        xp, yp = curves["PL"]
        for label in ("BTKP1", "BTKP10"):
            if label not in curves:
                continue
            xb, yb = curves[label]
            ratio = np.where(np.isfinite(yb) & np.isfinite(yp), yb / yp, np.nan)
            rax.plot(xb, ratio, color=RUNS[label][1], lw=1.2, label=label)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.01, 1)
    ax.set_ylabel(r"$\rho_{\rm DM}(r)\,[M_\odot\,{\rm kpc}^{-3}]$")
    ax.set_title(r"$M_{200m}\sim10^{%d}\,M_\odot$" % int(np.log10(mass)))
    ax.legend(loc="lower left")
    rax.set_xscale("log"); rax.set_yscale("log")
    rax.set_ylim(0.45, 4.5)
    rax.yaxis.set_major_locator(FixedLocator([0.5, 1.0, 2.0, 4.0]))
    rax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:g}"))
    rax.yaxis.set_minor_formatter(NullFormatter())
    rax.axhline(1.0, color="0.55", linewidth=0.7, alpha=0.85)
    rax.set_xlabel(r"$r/R_{200m}$")
    rax.set_ylabel("BT / PL")
fig.subplots_adjust(hspace=0.16, wspace=0.30, left=0.09, right=0.985, top=0.95, bottom=0.09)
cps.save_publication_figure(fig, OUT)
print("saved", OUT, flush=True)
