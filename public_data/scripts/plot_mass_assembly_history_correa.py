#!/usr/bin/env python
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


SCRIPT_DIR = Path(__file__).resolve().parent
PUBLIC_DATA_DIR = SCRIPT_DIR.parent
DATA_DIR = PUBLIC_DATA_DIR / "figure_data" / "mass_assembly_history"
ARTICLE_DIR = PUBLIC_DATA_DIR.parent
BT_OVER_PL_OUTPUT = DATA_DIR / "bt_over_pl_mass_fraction_ratio.csv"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cosmology_plot_style import apply_journal_style, format_axes, save_publication_figure  # noqa: E402


apply_journal_style(base_fontsize=8.5)

Z_MAX = 8.0
QUANTITATIVE_Z_MAX = 6.0
TARGETS = [3.0e8, 1.0e9, 3.0e9, 1.0e10, 3.0e10, 1.0e11, 3.0e11]


def row_for_target(summary: pd.DataFrame, target: float) -> pd.Series:
    values = summary["target_M0_msun"].to_numpy(dtype=float)
    return summary.iloc[int(np.argmin(np.abs(np.log10(values / target))))]


def direct_for_target(data: pd.DataFrame, target: float) -> pd.DataFrame:
    values = data["target_M0_msun"].to_numpy(dtype=float)
    nearest = values[int(np.argmin(np.abs(np.log10(values / target))))]
    return data[(data["target_M0_msun"] == nearest) & (data["z"] <= Z_MAX)].sort_values("z")


def solved_curve(curves: pd.DataFrame, mass: float, spectrum: str) -> pd.DataFrame:
    mask = (curves["spectrum"] == spectrum) & np.isclose(
        curves["M0_msun"], mass, rtol=1.0e-10, atol=0.0
    )
    return curves[mask].sort_values("z")


def fixed_curve(curves: pd.DataFrame, mass: float) -> pd.DataFrame:
    return curves[np.isclose(curves["M0_msun"], mass, rtol=1.0e-10, atol=0.0)].sort_values("z")


def simulation_to_reference_ratio(
    direct: pd.DataFrame, reference: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray]:
    x_direct = np.log10(1.0 + direct["z"].to_numpy(dtype=float))
    x_reference = np.log10(1.0 + reference["z"].to_numpy(dtype=float))
    log_reference_mass = np.log10(reference["M_msun"].to_numpy(dtype=float))
    reference_mass = 10.0 ** np.interp(x_direct, x_reference, log_reference_mass)
    ratio = direct["median_M_msun"].to_numpy(dtype=float) / reference_mass
    return x_direct, ratio


def normalized_bt_to_pl_ratio(
    bt_direct: pd.DataFrame, pl_direct: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_bt = np.log10(1.0 + bt_direct["z"].to_numpy(dtype=float))
    x_pl = np.log10(1.0 + pl_direct["z"].to_numpy(dtype=float))
    pl_mass = 10.0 ** np.interp(
        x_bt,
        x_pl,
        np.log10(pl_direct["median_M_msun"].to_numpy(dtype=float)),
    )
    bt_mass = bt_direct["median_M_msun"].to_numpy(dtype=float)
    pl_fraction = pl_mass / pl_mass[0]
    bt_fraction = bt_mass / bt_mass[0]
    return x_bt, bt_fraction / pl_fraction, pl_mass, pl_fraction, bt_fraction


def make_figure(output: Path) -> None:
    curves = pd.read_csv(DATA_DIR / "qzf_project_warren_half_mass_allmass_curves.csv")
    pl_data = pd.read_csv(DATA_DIR / "pl_warren_median_mah.csv")
    bt_data = pd.read_csv(DATA_DIR / "bt_soft_warren_median_mah.csv")
    pl_summary = pd.read_csv(DATA_DIR / "pl_warren_selection_summary.csv")
    bt_summary = pd.read_csv(DATA_DIR / "bt_soft_warren_selection_summary.csv")

    pl_fixed_curves = pd.read_csv(DATA_DIR / "pl_project_warren_curves.csv")
    bt_fixed_curves = pd.read_csv(DATA_DIR / "bt_project_warren_curves.csv")

    fig, (ax, ratio_ax, bt_pl_ax) = plt.subplots(
        3,
        1,
        figsize=(7.35, 7.25),
        sharex=True,
        gridspec_kw={"height_ratios": [4.25, 1.25, 1.25], "hspace": 0.07},
    )
    colors = plt.get_cmap("viridis")(np.linspace(0.10, 0.88, len(TARGETS)))
    bt_over_pl_rows = []

    for target, color in zip(TARGETS, colors):
        pl_row = row_for_target(pl_summary, target)
        bt_row = row_for_target(bt_summary, target)
        pl_direct = direct_for_target(pl_data, target)
        bt_direct = direct_for_target(bt_data, target)
        pl_solved = solved_curve(curves, float(pl_row["median_M0_Msun"]), "pl")
        bt_solved = solved_curve(curves, float(bt_row["median_M0_Msun"]), "bt_soft")
        pl_fixed = fixed_curve(pl_fixed_curves, float(pl_row["median_M0_Msun"]))
        bt_fixed = fixed_curve(bt_fixed_curves, float(bt_row["median_M0_Msun"]))

        ax.plot(np.log10(1.0 + pl_fixed["z"]), pl_fixed["M_msun"], color=color, lw=0.65, ls="--", alpha=0.22)
        ax.plot(np.log10(1.0 + bt_fixed["z"]), bt_fixed["M_msun"], color=color, lw=0.65, ls=":", alpha=0.26)
        ax.plot(np.log10(1.0 + pl_solved["z"]), pl_solved["M_msun"], color=color, lw=1.15, ls="--", alpha=0.90)
        ax.plot(np.log10(1.0 + bt_solved["z"]), bt_solved["M_msun"], color=color, lw=1.15, ls=":", alpha=0.95)
        ax.plot(
            np.log10(1.0 + pl_direct["z"]),
            pl_direct["median_M_msun"],
            color=color,
            ls="none",
            marker="o",
            markersize=3.0,
        )
        ax.plot(
            np.log10(1.0 + bt_direct["z"]),
            bt_direct["median_M_msun"],
            color=color,
            ls="none",
            marker="^",
            markersize=3.2,
            alpha=0.95,
        )

        pl_ratio_x, pl_ratio = simulation_to_reference_ratio(pl_direct, pl_solved)
        bt_ratio_x, bt_ratio = simulation_to_reference_ratio(bt_direct, bt_solved)
        ratio_ax.plot(
            pl_ratio_x,
            pl_ratio,
            color=color,
            ls="none",
            marker="o",
            markersize=2.8,
        )
        ratio_ax.plot(
            bt_ratio_x,
            bt_ratio,
            color=color,
            ls="none",
            marker="^",
            markersize=3.0,
            alpha=0.95,
        )

        bt_pl_x, bt_pl_ratio, pl_mass, pl_fraction, bt_fraction = normalized_bt_to_pl_ratio(
            bt_direct, pl_direct
        )
        bt_pl_ax.plot(
            bt_pl_x,
            bt_pl_ratio,
            color=color,
            lw=0.85,
            marker="o",
            markersize=2.6,
            alpha=0.95,
        )
        for index, row in bt_direct.reset_index(drop=True).iterrows():
            bt_over_pl_rows.append(
                {
                    "target_M0_msun": target,
                    "z": float(row["z"]),
                    "log10_1_plus_z": float(bt_pl_x[index]),
                    "pl_median_M_msun_interpolated": float(pl_mass[index]),
                    "bt_median_M_msun": float(row["median_M_msun"]),
                    "pl_mass_fraction": float(pl_fraction[index]),
                    "bt_mass_fraction": float(bt_fraction[index]),
                    "bt_over_pl_mass_fraction": float(bt_pl_ratio[index]),
                }
            )

    pd.DataFrame(bt_over_pl_rows).to_csv(BT_OVER_PL_OUTPUT, index=False)

    trusted_x_max = np.log10(1.0 + QUANTITATIVE_Z_MAX)
    plotted_x_max = np.log10(1.0 + Z_MAX)
    for panel in (ax, ratio_ax, bt_pl_ax):
        panel.axvspan(
            trusted_x_max,
            plotted_x_max,
            color="0.75",
            alpha=0.16,
            lw=0,
            zorder=0,
        )

    ax.set_yscale("log")
    ax.set_xlim(0.0, np.log10(1.0 + Z_MAX))
    ax.set_ylim(5.0e6, 7.0e11)
    ax.set_ylabel(r"Median $M(z)\,[M_\odot]$", labelpad=8)
    ax.set_title("Median MAHs and Correa reference relations", pad=7)
    format_axes(ax, grid=True)

    ratio_ax.axhspan(0.9, 1.1, color="0.75", alpha=0.18, lw=0, zorder=0)
    ratio_ax.axhline(1.0, color="0.25", lw=0.75, zorder=1)
    ratio_ax.set_yscale("log")
    ratio_ax.set_ylim(0.8, 3.3)
    ratio_ax.set_yticks([0.8, 1.0, 1.5, 2.0, 3.0])
    ratio_ax.set_yticklabels(["0.8", "1", "1.5", "2", "3"])
    ratio_ax.set_ylabel(r"$M_{\rm sim}/M_{\rm Correa}$", labelpad=7)
    format_axes(ratio_ax, grid=True)
    plt.setp(ratio_ax.get_xticklabels(), visible=False)

    bt_pl_ax.axhspan(0.9, 1.1, color="0.75", alpha=0.18, lw=0, zorder=0)
    bt_pl_ax.axhline(1.0, color="0.25", lw=0.75, zorder=1)
    bt_pl_ax.set_ylim(0.9, 5.0)
    bt_pl_ax.set_yticks([1.0, 2.0, 3.0, 4.0, 5.0])
    bt_pl_ax.set_xlabel(r"$\log_{10}(1+z)$", labelpad=7)
    bt_pl_ax.set_ylabel(r"$(M/M_0)_{\rm BT}/(M/M_0)_{\rm PL}$", labelpad=7)
    format_axes(bt_pl_ax, grid=True)

    style_handles = [
        plt.Line2D([], [], color="0.25", ls="none", marker="o", markersize=3.0, label="PL median"),
        plt.Line2D([], [], color="0.25", ls="none", marker="^", markersize=3.2, label="BT median"),
        plt.Line2D([], [], color="0.25", lw=1.1, ls="--", label=r"PL solved $q,\tilde{z}_{\rm f}$"),
        plt.Line2D([], [], color="0.25", lw=1.1, ls=":", label=r"BT solved $q,\tilde{z}_{\rm f}$"),
        plt.Line2D([], [], color="0.25", lw=0.7, ls="-", alpha=0.25, label="fixed relation"),
    ]
    first = ax.legend(handles=style_handles, loc="lower left", fontsize=7.1)
    ax.add_artist(first)

    mass_handles = [
        plt.Line2D([], [], color=color, lw=1.8, label=rf"${target:.0e}$")
        for target, color in zip(TARGETS, colors)
    ]
    ax.legend(
        handles=mass_handles,
        title=r"$M_0\,[M_\odot]$",
        loc="upper right",
        fontsize=6.1,
        title_fontsize=7.0,
        handlelength=1.4,
        borderaxespad=0.25,
    )
    fig.subplots_adjust(left=0.17, right=0.985, bottom=0.10, top=0.92)
    save_publication_figure(fig, output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTICLE_DIR / "mass-assembly-history-correa-halfmass.png",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    make_figure(args.output)
    print(args.output)
