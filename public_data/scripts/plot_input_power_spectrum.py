#!/usr/bin/env python3
"""Plot the manuscript input spectra from the public reduced table."""

import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, LogFormatterMathtext
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(
    (parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists()),
    SCRIPT_DIR.parents[2],
)
PUBLIC_DATA_PATH = (
    ARTICLE_ROOT
    / "public_data"
    / "figure_data"
    / "input_power_spectra"
    / "input_power_spectra.csv"
)
OUTPUT_PATH = Path(
    os.environ.get("INPUT_POWER_SPECTRUM_OUTPUT_PATH", ARTICLE_ROOT / "input-power-spectrum.png")
)
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes  # noqa: E402

SPECTRA = [
    (
        "PL",
        "PL",
        {"color": JOURNAL_COLORS["black"], "linestyle": "-", "linewidth": 1.45},
    ),
    (
        "BT_soft",
        r"BT $k_p=1$",
        {"color": JOURNAL_COLORS["blue"], "linestyle": "--", "linewidth": 1.45},
    ),
    (
        "BT_deep",
        r"BT $k_p=10$",
        {"color": JOURNAL_COLORS["green"], "linestyle": "-.", "linewidth": 1.45},
    ),
]

FIDUCIAL_BOX_HMPC = 25.0
FIDUCIAL_MESH_N = 1024
K_NY_FIDUCIAL = np.pi * FIDUCIAL_MESH_N / FIDUCIAL_BOX_HMPC
K_HIGHK_CAUTION = 0.5 * K_NY_FIDUCIAL
BT_PIVOTS = (1.0, 10.0)


def read_public_spectra() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Read the portable CSV without relying on the original cluster paths."""
    if not PUBLIC_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing public input-spectrum table: {PUBLIC_DATA_PATH}")
    table = np.genfromtxt(
        PUBLIC_DATA_PATH,
        delimiter=",",
        names=True,
        dtype=None,
        encoding="utf-8",
    )
    spectra = {}
    for model, _label, _style in SPECTRA:
        selected = table[table["model"] == model]
        if len(selected) == 0:
            raise ValueError(f"No rows for {model} in {PUBLIC_DATA_PATH}")
        order = np.argsort(selected["k_hMpc"])
        spectra[model] = (
            np.asarray(selected["k_hMpc"][order], dtype=float),
            np.asarray(selected["P_k_Mpc_over_h_cubed"][order], dtype=float),
        )
    return spectra


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
    spectra = read_public_spectra()

    for model, label, style in SPECTRA:
        k, power = spectra[model]
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

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=600, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
