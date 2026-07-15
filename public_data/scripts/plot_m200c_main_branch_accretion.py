#!/usr/bin/env python3
"""Plot M200c accretion along the most-massive-progenitor branch."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_PATH = Path(__file__).resolve()
ARTICLE_ROOT = next((p for p in SCRIPT_PATH.parents if (p / "main.tex").exists()), SCRIPT_PATH.parents[2])
PUBLIC_DATA_PATH = (
    ARTICLE_ROOT / "public_data/figure_data/mass_accretion/m200c_main_branch_accretion.csv"
)

if str(SCRIPT_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PATH.parent))

try:
    from cosmology_plot_style import (
        JOURNAL_COLORS,
        apply_journal_style,
        format_axes,
        save_publication_figure,
    )
except ImportError:
    JOURNAL_COLORS = {"black": "#000000", "blue": "#0072B2", "green": "#009E73"}

    def apply_journal_style(base_fontsize: float = 8.5) -> None:
        plt.rcParams.update({"font.size": base_fontsize})

    def format_axes(ax, grid: bool = False) -> None:
        if grid:
            ax.grid(color="0.88", linewidth=0.5)

    def save_publication_figure(fig, output_path: Path, close: bool = True) -> None:
        fig.savefig(Path(output_path).with_suffix(".png"), dpi=600, bbox_inches="tight")
        if close:
            plt.close(fig)


MODEL_STYLES = {
    "PL": {"label": "PL", "color": JOURNAL_COLORS["black"]},
    "BT_soft": {"label": r"BT $k_p=1$", "color": JOURNAL_COLORS["blue"]},
    "BT_deep": {"label": r"BT $k_p=10$", "color": JOURNAL_COLORS["green"]},
}
PANEL_BINS = [
    (1.0e9, 3.16e9),
    (3.16e9, 1.0e10),
    (1.0e10, 3.16e10),
    (3.16e10, 1.0e11),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=PUBLIC_DATA_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTICLE_ROOT / "mass-accretion-rate-m200c-main-branch.png",
    )
    parser.add_argument("--check-output", type=Path, default=None)
    parser.add_argument(
        "--show-scatter",
        action="store_true",
        help="Show the 16th--84th percentile halo-to-halo range.",
    )
    return parser.parse_args()


def mass_bin_label(left: float, right: float) -> str:
    left_power = round(2.0 * np.log10(left)) / 2.0
    right_power = round(2.0 * np.log10(right)) / 2.0
    return rf"$10^{{{left_power:g}}}\leq M_{{200c}}/M_\odot<10^{{{right_power:g}}}$"


def select_bin(data: pd.DataFrame, model: str, left: float, right: float) -> pd.DataFrame:
    return data.loc[
        (data["model"] == model)
        & np.isclose(data["mass_bin_left_msun"], left)
        & np.isclose(data["mass_bin_right_msun"], right)
    ].sort_values("z_descendant")


def draw_panel(
    ax,
    data: pd.DataFrame,
    left: float,
    right: float,
    show_legend: bool,
    show_scatter: bool,
) -> None:
    plotted_values: list[np.ndarray] = []
    pl = select_bin(data, "PL", left, right)
    if not pl.empty:
        ax.plot(
            pl["z_descendant"],
            pl["correa2015_mean_dMdt_msun_yr"],
            color="0.48",
            linestyle="--",
            linewidth=1.45,
            label="Correa15 mean (PL)",
            zorder=2,
        )
        plotted_values.append(pl["correa2015_mean_dMdt_msun_yr"].to_numpy(dtype=float))

    for model, style in MODEL_STYLES.items():
        subset = select_bin(data, model, left, right)
        if subset.empty:
            continue
        redshift = subset["z_descendant"].to_numpy(dtype=float)
        median_rate = subset["median_dM200c_dt_msun_yr"].to_numpy(dtype=float)
        if show_scatter:
            lower_rate = subset["p16_dM200c_dt_msun_yr"].to_numpy(dtype=float)
            upper_rate = subset["p84_dM200c_dt_msun_yr"].to_numpy(dtype=float)
            ax.fill_between(
                redshift,
                lower_rate,
                upper_rate,
                color=style["color"],
                alpha=0.10,
                linewidth=0,
                zorder=1,
            )
            plotted_values.extend((lower_rate, upper_rate))
        ax.plot(
            redshift,
            median_rate,
            color=style["color"],
            linewidth=1.8,
            marker="o",
            markersize=3.0,
            markeredgewidth=0,
            label=style["label"],
            zorder=3,
        )
        plotted_values.append(median_rate)

    finite_values = np.concatenate([values[np.isfinite(values)] for values in plotted_values])
    upper = max(0.0, float(np.max(finite_values)))
    lower = min(0.0, float(np.min(finite_values)))
    padding = max(0.05 * (upper - lower), 0.02 * upper, 1.0e-3)
    ax.set_ylim(lower - padding if lower < 0.0 else 0.0, upper + padding)
    ax.invert_xaxis()
    ax.set_box_aspect(1)
    ax.minorticks_on()
    format_axes(ax, grid=False)
    ax.text(
        0.04,
        0.95,
        mass_bin_label(left, right),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.0,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 1.0},
    )
    if show_legend:
        ax.legend(loc="upper right", fontsize=7.4, handlelength=1.6, labelspacing=0.25)


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.data)
    required = {
        "model",
        "z_descendant",
        "mass_bin_left_msun",
        "mass_bin_right_msun",
        "median_dM200c_dt_msun_yr",
        "p16_dM200c_dt_msun_yr",
        "p84_dM200c_dt_msun_yr",
        "correa2015_mean_dMdt_msun_yr",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"{args.data} is missing columns: {missing}")

    apply_journal_style(base_fontsize=8.5)
    fig, axes = plt.subplots(2, 2, figsize=(7.05, 7.0), constrained_layout=False)
    for index, (ax, (left, right)) in enumerate(zip(axes.flat, PANEL_BINS)):
        draw_panel(
            ax,
            data,
            left,
            right,
            show_legend=index == 0,
            show_scatter=args.show_scatter,
        )
        if index // 2 == 1:
            ax.set_xlabel("Redshift $z$")
        else:
            ax.tick_params(labelbottom=False)
        if index % 2 == 0:
            ax.set_ylabel(r"$\mathrm{median}\,(\mathrm{d}M_{200c}/\mathrm{d}t)$ [$M_\odot\,{\rm yr}^{-1}$]")
        else:
            ax.tick_params(labelleft=False)

    fig.subplots_adjust(left=0.12, right=0.99, bottom=0.09, top=0.99, wspace=0.08, hspace=0.08)
    save_publication_figure(fig, args.output)
    print(f"Wrote {args.output.with_suffix('.png')}")

    if args.check_output is not None:
        args.check_output.parent.mkdir(parents=True, exist_ok=True)
        args.check_output.write_bytes(args.output.with_suffix(".png").read_bytes())
        print(f"Wrote {args.check_output}")


if __name__ == "__main__":
    main()
