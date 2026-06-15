#!/usr/bin/env python3
"""Plot the input matter power spectra used in the manuscript."""

import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, LogFormatterMathtext
import numpy as np


WORKSPACE = Path("/project/tkcastrosim/HNHuang")
PROJECT = WORKSPACE / "project_big_sim"
ANALYSIS_ROOT = PROJECT / "analysis" / "_used_by_article_nonlinear_evolution_pps"
DATA_DIR = ANALYSIS_ROOT / "initial_condition"
OUT_DIR = ANALYSIS_ROOT / "paperplot" / "figures"
PAPER_DIR = PROJECT / "papers" / "article_nonlinear_evolution_pps"
POSTER_FIG_DIR = PROJECT / "posters" / "poster_blue_tilted_pps" / "figures"
TOOLS_DIR = WORKSPACE / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes  # noqa: E402

SPECTRA = [
    (
        "PL",
        DATA_DIR / "input_powerspec_kp_1.0_ms_1.0_5.000000_0.0.txt",
        {"color": JOURNAL_COLORS["black"], "linestyle": "-", "linewidth": 1.45},
    ),
    (
        "BT(soft)",
        DATA_DIR / "input_powerspec_kp_1.0_ms_1.5_256.000000_0.0.txt",
        {"color": JOURNAL_COLORS["blue"], "linestyle": "--", "linewidth": 1.45},
    ),
    (
        "BT(deep)",
        DATA_DIR / "input_powerspec_kp_10.0_ms_1.5_256.000000_0.0.txt",
        {"color": JOURNAL_COLORS["green"], "linestyle": "-.", "linewidth": 1.45},
    ),
]

FIDUCIAL_BOX_HMPC = 25.0
FIDUCIAL_MESH_N = 1024
K_NY_FIDUCIAL = np.pi * FIDUCIAL_MESH_N / FIDUCIAL_BOX_HMPC
K_HIGHK_CAUTION = 0.5 * K_NY_FIDUCIAL
BT_PIVOTS = (1.0, 10.0)


def mark_input_scale_reference(ax) -> None:
    """Mark BT pivot positions and the fiducial particle-grid scale."""
    ax.axvspan(K_HIGHK_CAUTION, K_NY_FIDUCIAL, color="0.75", alpha=0.10, lw=0, zorder=0)
    ax.axvspan(K_NY_FIDUCIAL, 1.0e3, color="0.82", alpha=0.22, lw=0, zorder=0)
    for pivot in BT_PIVOTS:
        ax.axvline(pivot, color="0.35", linestyle=":", linewidth=0.8, alpha=0.85, zorder=1)
    ax.axvline(K_NY_FIDUCIAL, color="0.25", linestyle="--", linewidth=0.9, alpha=0.9, zorder=1)
    ax.text(
        K_NY_FIDUCIAL,
        1.8e-12,
        r"$k_{\rm Ny}$",
        rotation=90,
        ha="right",
        va="bottom",
        fontsize=6.8,
        color="0.25",
    )
    for pivot, label in zip(BT_PIVOTS, (r"$k_p=1$", r"$k_p=10$")):
        ax.text(
            pivot,
            4.8e-13,
            label,
            rotation=90,
            ha="right",
            va="bottom",
            fontsize=6.6,
            color="0.30",
        )


def main() -> None:
    apply_journal_style(base_fontsize=8.8)
    fig, ax = plt.subplots(figsize=(3.45, 2.65))

    for label, path, style in SPECTRA:
        data = np.loadtxt(path)
        k = data[:, 0]
        power = data[:, 1]
        mask = (k >= 1e-3) & (k <= 1e3)
        ax.loglog(k[mask], power[mask], label=label, **style)

    mark_input_scale_reference(ax)
    ax.set_xlim(1e-3, 1e3)
    ax.set_ylim(1e-13, 1e-2)
    ax.xaxis.set_major_locator(FixedLocator(10.0 ** np.arange(-3, 4)))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.yaxis.set_major_locator(FixedLocator(10.0 ** np.arange(-13, -2, 2)))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.set_xlabel(r"$k\,[h\,{\rm Mpc}^{-1}]$")
    ax.set_ylabel(r"$P(k)\,[({\rm Mpc}/h)^3]$")
    format_axes(ax)
    ax.legend(
        loc="lower left",
        fontsize=7.4,
        frameon=True,
        fancybox=False,
        framealpha=0.75,
        edgecolor="none",
        borderpad=0.25,
        handlelength=1.6,
        handletextpad=0.45,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    POSTER_FIG_DIR.mkdir(parents=True, exist_ok=True)
    for path in (
        OUT_DIR / "input-power-spectrum.png",
        PAPER_DIR / "input-power-spectrum.png",
        POSTER_FIG_DIR / "input-power-spectrum.png",
    ):
        fig.savefig(path, dpi=600, bbox_inches="tight", pad_inches=0.06)
        print(path)


if __name__ == "__main__":
    main()
