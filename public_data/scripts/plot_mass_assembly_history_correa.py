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
from matplotlib.ticker import NullLocator
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PUBLIC_DATA_DIR = SCRIPT_DIR.parent
DATA_DIR = PUBLIC_DATA_DIR / "figure_data" / "mass_assembly_history"
ARTICLE_DIR = PUBLIC_DATA_DIR.parent
BT_OVER_PL_OUTPUT = DATA_DIR / "bt_over_pl_mass_fraction_ratio.csv"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cosmology_plot_style import apply_journal_style, format_axes, save_publication_figure, sparse_errorbar  # noqa: E402


apply_journal_style(base_fontsize=10.6)

Z_MAX = 8.0
TARGETS = [1.0e9, 3.0e9, 1.0e10, 3.0e10, 1.0e11, 3.0e11]


def row_for_target(summary: pd.DataFrame, target: float) -> pd.Series:
    values = summary["target_M0_msun"].to_numpy(dtype=float)
    return summary.iloc[int(np.argmin(np.abs(np.log10(values / target))))]


def direct_for_target(data: pd.DataFrame, target: float) -> pd.DataFrame:
    values = data["target_M0_msun"].to_numpy(dtype=float)
    nearest = values[int(np.argmin(np.abs(np.log10(values / target))))]
    return data[(data["target_M0_msun"] == nearest) & (data["z"] <= Z_MAX)].sort_values("z")


def reference_curve(curves: pd.DataFrame, mass: float) -> pd.DataFrame:
    mask = np.isclose(curves["M0_msun"], mass, rtol=1.0e-10, atol=0.0)
    return curves[mask].sort_values("z")


def simulation_to_reference_ratio(
    direct: pd.DataFrame, reference: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_direct = np.log10(1.0 + direct["z"].to_numpy(dtype=float))
    x_reference = np.log10(1.0 + reference["z"].to_numpy(dtype=float))
    log_reference_mass = np.log10(reference["M_msun"].to_numpy(dtype=float))
    reference_mass = 10.0 ** np.interp(x_direct, x_reference, log_reference_mass)
    ratio = direct["median_M_msun"].to_numpy(dtype=float) / reference_mass
    return x_direct, ratio, reference_mass


def mass_interval_errors(
    errorbars: pd.DataFrame,
    model: str,
    target: float,
    redshifts: np.ndarray,
    interval_kind: str,
) -> np.ndarray:
    interval_columns = {
        "bootstrap": (
            "bootstrap_p16_median_M_msun",
            "bootstrap_p84_median_M_msun",
        ),
        "halo": ("halo_p16_M_msun", "halo_p84_M_msun"),
    }
    lower_column, upper_column = interval_columns[interval_kind]
    model_rows = errorbars[errorbars["model"] == model]
    available_targets = model_rows["target_M0_msun"].to_numpy(dtype=float)
    nearest = available_targets[
        int(np.argmin(np.abs(np.log10(available_targets / target))))
    ]
    model_rows = model_rows[model_rows["target_M0_msun"] == nearest]
    lower = []
    upper = []
    for redshift in redshifts:
        row = model_rows[
            np.isclose(model_rows["z"], redshift, rtol=0.0, atol=1.0e-8)
        ]
        if row.empty:
            lower.append(np.nan)
            upper.append(np.nan)
            continue
        entry = row.iloc[0]
        median = float(entry["median_M_msun"])
        lower.append(median - float(entry[lower_column]))
        upper.append(float(entry[upper_column]) - median)
    return np.vstack([lower, upper])


def direct_halo_interval_errors(direct: pd.DataFrame) -> np.ndarray:
    median = direct["median_M_msun"].to_numpy(dtype=float)
    lower = median - direct["p16_M_msun"].to_numpy(dtype=float)
    upper = direct["p84_M_msun"].to_numpy(dtype=float) - median
    return np.vstack([lower, upper])


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


def make_figure(
    output: Path,
    errorbar_table: Path | None = None,
    interval_kind: str = "track-bootstrap",
) -> None:
    pl_curves = pd.read_csv(DATA_DIR / "pl_project_warren_curves.csv")
    bt_curves = pd.read_csv(DATA_DIR / "bt_project_warren_curves.csv")
    pl_data = pd.read_csv(DATA_DIR / "pl_warren_median_mah.csv")
    bt_data = pd.read_csv(DATA_DIR / "bt_soft_warren_median_mah.csv")
    pl_summary = pd.read_csv(DATA_DIR / "pl_warren_selection_summary.csv")
    bt_summary = pd.read_csv(DATA_DIR / "bt_soft_warren_selection_summary.csv")
    errorbars = pd.read_csv(errorbar_table) if errorbar_table is not None else None

    if interval_kind == "track-bootstrap":
        table = DATA_DIR / "mah_track_bootstrap.csv" if errorbar_table is None else errorbar_table
        errorbars = pd.read_csv(table)

    fig, (ax, ratio_ax, bt_pl_ax) = plt.subplots(
        3,
        1,
        figsize=(3.58, 5.15),
        sharex=True,
        gridspec_kw={"height_ratios": [4.25, 1.2, 2.0], "hspace": 0.095},
    )
    colors = plt.get_cmap("magma")(np.linspace(0.13, 0.76, len(TARGETS)))
    bt_over_pl_rows = []

    for target, color in zip(TARGETS, colors):
        pl_row = row_for_target(pl_summary, target)
        bt_row = row_for_target(bt_summary, target)
        pl_direct = direct_for_target(pl_data, target)
        bt_direct = direct_for_target(bt_data, target)
        pl_solved = reference_curve(pl_curves, float(pl_row["median_M0_Msun"]))
        bt_solved = reference_curve(bt_curves, float(bt_row["median_M0_Msun"]))
        ax.plot(np.log10(1.0 + pl_solved["z"]), pl_solved["M_msun"], color=color, lw=1.15, ls="--", alpha=0.90)
        ax.plot(np.log10(1.0 + bt_solved["z"]), bt_solved["M_msun"], color=color, lw=1.15, ls=":", alpha=0.95)
        if interval_kind == "halo":
            pl_mass_errors = direct_halo_interval_errors(pl_direct)
            bt_mass_errors = direct_halo_interval_errors(bt_direct)
        elif interval_kind == "track-bootstrap":
            def track_errors(model, direct):
                subset = errorbars[(errorbars["model"] == model) & (errorbars["target_M0_msun"] == target)].sort_values("z")
                np.testing.assert_allclose(subset["z"], direct["z"], atol=1e-8)
                np.testing.assert_allclose(subset["median_M_msun"], direct["median_M_msun"])
                for count in ("n_halos", "n_positive_mass"):
                    np.testing.assert_array_equal(subset[count], direct[count])
                ax.fill_between(np.log10(1 + direct["z"].to_numpy()),
                                direct["p16_M_msun"].to_numpy(), direct["p84_M_msun"].to_numpy(),
                                facecolor=color, alpha=0.11, linewidth=0, zorder=0.8)
                return subset

            pl_stats = track_errors("PL", pl_direct)
            bt_stats = track_errors("BT_kp1", bt_direct)
            pl_mass_errors = pl_stats["median_bootstrap_se"].to_numpy()
            bt_mass_errors = bt_stats["median_bootstrap_se"].to_numpy()
        elif errorbars is not None:
            pl_mass_errors = mass_interval_errors(
                errorbars,
                "PL",
                target,
                pl_direct["z"].to_numpy(dtype=float),
                interval_kind,
            )
            bt_mass_errors = mass_interval_errors(
                errorbars,
                "BT_kp1",
                target,
                bt_direct["z"].to_numpy(dtype=float),
                interval_kind,
            )
        else:
            raise ValueError("--errorbar-table is required for bootstrap intervals")
        sparse_errorbar(ax,
            np.log10(1.0 + pl_direct["z"]),
            pl_direct["median_M_msun"],
            yerr=pl_mass_errors,
            color=color,
            ls="none",
            marker="o",
            markersize=3.0,
            elinewidth=0.65,
            capsize=1.2,
            capthick=0.65,
        )
        sparse_errorbar(ax,
            np.log10(1.0 + bt_direct["z"]),
            bt_direct["median_M_msun"],
            yerr=bt_mass_errors,
            color=color,
            ls="none",
            marker="^",
            markersize=3.2,
            elinewidth=0.65,
            capsize=1.2,
            capthick=0.65,
            alpha=0.95,
        )

        pl_ratio_x, pl_ratio, pl_reference_mass = simulation_to_reference_ratio(
            pl_direct, pl_solved
        )
        bt_ratio_x, bt_ratio, bt_reference_mass = simulation_to_reference_ratio(
            bt_direct, bt_solved
        )
        pl_ratio_errors = (
            pl_mass_errors / pl_reference_mass if pl_mass_errors is not None else None
        )
        bt_ratio_errors = (
            bt_mass_errors / bt_reference_mass if bt_mass_errors is not None else None
        )
        sparse_errorbar(ratio_ax,
            pl_ratio_x,
            pl_ratio,
            yerr=pl_ratio_errors,
            color=color,
            ls="none",
            marker="o",
            markersize=2.8,
            elinewidth=0.45,
            capsize=0.8,
            capthick=0.45,
            alpha=0.95,
        )
        sparse_errorbar(ratio_ax,
            bt_ratio_x,
            bt_ratio,
            yerr=bt_ratio_errors,
            color=color,
            ls="none",
            marker="^",
            markersize=3.0,
            elinewidth=0.45,
            capsize=0.8,
            capthick=0.45,
            alpha=0.95,
        )

        bt_pl_x, bt_pl_ratio, pl_mass, pl_fraction, bt_fraction = normalized_bt_to_pl_ratio(
            bt_direct, pl_direct
        )
        if interval_kind == "track-bootstrap":
            np.testing.assert_allclose(bt_pl_ratio, bt_stats["normalized_bt_over_pl"])
            bt_pl_ax.errorbar(bt_pl_x, bt_pl_ratio, yerr=bt_stats["ratio_bootstrap_se"],
                              fmt="none", ecolor=color, elinewidth=0.5, capsize=0, alpha=0.85)
        bt_pl_ax.plot(
            bt_pl_x,
            bt_pl_ratio,
            color=color,
            ls="none",
            marker="o",
            markersize=2.6,
            markevery=3,
            alpha=0.95,
        )
        bt_pl_ax.plot(bt_pl_x, bt_pl_ratio, color=color, ls="none",
                      marker=".", markersize=1.35, alpha=0.65)
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

    ax.set_yscale("log")
    ax.set_xlim(0.0, np.log10(1.0 + Z_MAX))
    ax.set_ylim(5.0e6, 7.0e11)
    ax.set_ylabel(r"Median $M(z)\,[M_\odot]$", labelpad=8)
    format_axes(ax, grid=True)

    ratio_ax.axhline(1.0, color="0.25", lw=0.75, zorder=1)
    ratio_ax.set_yscale("log")
    ratio_ax.set_ylim(0.8, 3.3)
    ratio_ax.set_yticks([1.0, 2.0, 3.0], labels=["1", "2", "3"])
    ratio_ax.yaxis.set_minor_locator(NullLocator())
    ratio_ax.set_ylabel(r"$M_{\rm sim}/M_{\rm Correa}$", labelpad=7)
    format_axes(ratio_ax, grid=True)
    plt.setp(ratio_ax.get_xticklabels(), visible=False)

    bt_pl_ax.axhline(1.0, color="0.25", lw=0.75, zorder=1)
    bt_pl_ax.set_ylim(0.68, 5.0)
    bt_pl_ax.set_yticks([1.0, 3.0, 5.0])
    bt_pl_ax.set_xlabel(r"$\log_{10}(1+z)$", labelpad=7)
    bt_pl_ax.set_ylabel(r"$f_{\rm BT}/f_{\rm PL}$", labelpad=7)
    format_axes(bt_pl_ax, grid=True)
    bt_pl_ax.tick_params(axis="x", pad=7)

    x_z6 = np.log10(1.0 + 6.0)
    for panel_ax in (ax, ratio_ax, bt_pl_ax):
        panel_ax.axvline(x_z6, color="0.45", ls="--", lw=0.8, zorder=1)
    ax.text(
        x_z6 - 0.015,
        4.2e11,
        r"$z=6$",
        ha="right",
        va="top",
        fontsize=9.0,
        color="0.35",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.5},
    )

    style_handles = [
        plt.Line2D([], [], color="0.25", ls="none", marker="o", markersize=3.0, label="PL median"),
        plt.Line2D([], [], color="0.25", ls="none", marker="^", markersize=3.2, label=r"BT $k_p=1$ median"),
        plt.Line2D([], [], color="0.25", lw=1.1, ls="--", label="PL Correa-EPS"),
        plt.Line2D([], [], color="0.25", lw=1.1, ls=":", label=r"BT $k_p=1$ Correa-EPS"),
    ]
    bt_pl_ax.legend(
        handles=style_handles,
        loc="upper left",
        fontsize=9.2,
        labelspacing=0.24,
        handletextpad=0.42,
        handlelength=1.4,
        borderaxespad=0.38,
        frameon=True,
        framealpha=1,
        facecolor="white",
        edgecolor="none",
    )

    mass_handles = []
    for target, color in zip(TARGETS, colors):
        exponent = int(np.floor(np.log10(target)))
        coefficient = round(target / 10**exponent)
        power = "10^{%d}" % exponent
        label = "$" + (rf"{coefficient}\times" if coefficient != 1 else "") + power + "$"
        mass_handles.append(plt.Line2D([], [], color=color, lw=1.8, label=label))
    ax.legend(
        handles=mass_handles,
        title=r"$M_0\,[M_\odot]$",
        loc="lower left",
        ncol=2,
        fontsize=10.4,
        title_fontsize=11.2,
        handlelength=1.4,
        handletextpad=0.38,
        columnspacing=0.68,
        labelspacing=0.18,
        borderpad=0.18,
        borderaxespad=0.41,
        frameon=True,
        framealpha=1,
        facecolor="white",
        edgecolor="none",
    )
    fig.subplots_adjust(left=0.21, right=0.98, bottom=0.113, top=0.978)
    save_publication_figure(fig, output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTICLE_DIR / "mass-assembly-history-correa.png",
    )
    parser.add_argument(
        "--errorbar-table",
        type=Path,
        default=None,
        help="Bootstrap table; only required when --interval-kind=bootstrap.",
    )
    parser.add_argument(
        "--interval-kind",
        choices=["track-bootstrap", "bootstrap", "halo"],
        default="track-bootstrap",
        help="Show bootstrap uncertainty of the median or halo-to-halo percentiles.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    make_figure(args.output, args.errorbar_table, args.interval_kind)
    print(args.output)
