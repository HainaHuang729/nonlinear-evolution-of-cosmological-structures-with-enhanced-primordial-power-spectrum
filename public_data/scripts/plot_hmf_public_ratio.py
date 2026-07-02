#!/usr/bin/env python
"""Lightweight FoF HMF paper figure from public CSV products."""

from collections import defaultdict
from pathlib import Path
import csv

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, LogFormatterMathtext, LogLocator, NullFormatter

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes, format_redshift, panel_label


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(p for p in SCRIPT_DIR.parents if (p / "main.tex").exists())
DATA_ROOT = ARTICLE_ROOT / "public_data" / "figure_data" / "fof_hmf"
POINTS_PATH = DATA_ROOT / "fof_reed07_hmf_points.csv"
RATIO_PATH = DATA_ROOT / "fof_reed07_hmf_residuals.csv"
OUTPUT_PATH = ARTICLE_ROOT / "mass-function.png"

SNAPS = ["0056", "0040", "0032", "0030", "0027", "0024"]
MODEL_MAP = {"PL": "PL", "BT_soft": "BTKP1", "BT_deep": "BTKP10", "BTKP1": "BTKP1", "BTKP10": "BTKP10"}
MODELS = {
    "PL": {"color": JOURNAL_COLORS["black"], "marker": "o", "linestyle": "-"},
    "BTKP1": {"color": JOURNAL_COLORS["blue"], "marker": "^", "linestyle": "--"},
    "BTKP10": {"color": JOURNAL_COLORS["green"], "marker": "s", "linestyle": "-."},
}
MODEL_LABELS = {
    "PL": "PL",
    "BTKP1": r"BT $k_p=1$",
    "BTKP10": r"BT $k_p=10$",
}
HMF_XMIN_MSUN = 5.0e7
HMF_XMAX_MSUN = 2.0e11
MAIN_PARTICLE_MASS_MSUN = 1.89e6
HMF_N20_MASS_MSUN = 20.0 * MAIN_PARTICLE_MASS_MSUN
HMF_CATALOG_CUT_MSUN = 1.0e8
RATIO_TICKS = np.array([0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000.0])
RATIO_LABEL_TICKS = np.array([0.1, 1, 10, 100, 1000.0])
BT_PL_LABEL_TICKS = np.array([0.1, 1, 10, 100, 1000.0])
SIM_REED_YLIM = (0.2, 30.0)
SIM_REED_LABEL_TICKS = np.array([0.3, 1, 3, 10, 30.0])


def normalize_snap(value):
    return str(int(float(value))).zfill(4)


def as_float(value, default=np.nan):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def read_public_tables():
    points = defaultdict(list)
    ratios = defaultdict(list)

    with POINTS_PATH.open(newline="") as handle:
        for row in csv.DictReader(handle):
            snap = normalize_snap(row.get("snapshot", ""))
            model = MODEL_MAP.get(row.get("model", ""), row.get("model", ""))
            if snap not in SNAPS or model not in MODELS:
                continue
            points[(snap, model)].append(
                {
                    "redshift": as_float(row.get("redshift")),
                    "log10_M_FOF_Msun": as_float(row.get("log10_M_FOF_Msun")),
                    "dn_dlog10M": as_float(row.get("dn_dlog10M")),
                    "poisson_err": as_float(row.get("poisson_err")),
                }
            )

    with RATIO_PATH.open(newline="") as handle:
        for row in csv.DictReader(handle):
            snap = normalize_snap(row.get("snapshot", ""))
            model = MODEL_MAP.get(row.get("model", ""), row.get("model", ""))
            if snap not in SNAPS or model not in MODELS:
                continue
            ratios[(snap, model)].append(
                {
                    "redshift": as_float(row.get("redshift")),
                    "log10_M_FOF_Msun": as_float(row.get("log10_M_FOF_Msun")),
                    "reed07_dndlog10M_interp": as_float(row.get("reed07_dndlog10M_interp")),
                    "sim_over_reed07": as_float(row.get("sim_over_reed07")),
                    "ratio_err": as_float(row.get("ratio_err")),
                }
            )

    for table in (points, ratios):
        for rows in table.values():
            rows.sort(key=lambda item: item["log10_M_FOF_Msun"])

    return points, ratios


def values(rows, key):
    return np.asarray([row[key] for row in rows], dtype=float)


def first_redshift(points, snap):
    for model in MODELS:
        rows = points.get((snap, model), [])
        if rows:
            return float(rows[0]["redshift"])
    return np.nan


def mark_resolution(ax):
    ax.axvspan(HMF_N20_MASS_MSUN, HMF_CATALOG_CUT_MSUN, color="0.82", alpha=0.22, lw=0, zorder=0)
    ax.axvline(HMF_CATALOG_CUT_MSUN, color="0.35", linestyle="--", linewidth=0.85, alpha=0.9, zorder=1)


def ratio_tick_label(value, _pos):
    if value <= 0 or not np.isfinite(value):
        return ""
    exponent = np.log10(value)
    rounded = int(np.rint(exponent))
    if np.isclose(exponent, rounded, atol=1.0e-10):
        return rf"$10^{{{rounded}}}$"
    return f"{value:g}"


def set_log_ticks(ax, ratio=False, ratio_ticks=None):
    ax.xaxis.set_major_locator(FixedLocator(10.0 ** np.arange(8, 12)))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=80))
    ax.xaxis.set_minor_formatter(NullFormatter())
    if ratio:
        ymin, ymax = ax.get_ylim()
        if ratio_ticks is None:
            ratio_ticks = RATIO_LABEL_TICKS
        ticks = ratio_ticks[(ratio_ticks >= ymin) & (ratio_ticks <= ymax)]
        if len(ticks) >= 2:
            ax.yaxis.set_major_locator(FixedLocator(ticks))
            ax.yaxis.set_major_formatter(FuncFormatter(ratio_tick_label))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=20))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.tick_params(axis="y", which="major", labelsize=8.0, pad=1.0)
        for tick_label in ax.get_yticklabels():
            tick_label.set_verticalalignment("center")


def ratio_ylim(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values) & (values > 0)]
    if len(values) == 0:
        return 0.5, 10.0
    ymin = max(0.08, values.min() * 0.82)
    ymax = max(2.0, values.max() * 1.18)
    if ymax / ymin > 30:
        ymin = 10 ** np.floor(np.log10(ymin))
        ymax = 1.35 * 10 ** np.ceil(np.log10(ymax))
    return ymin, ymax


def main():
    apply_journal_style(base_fontsize=11.2)
    points, ratios = read_public_tables()

    bt_pl_values = []
    bt_pl_cache = {}
    for snap in SNAPS:
        pl = points.get((snap, "PL"), [])
        for model in ["BTKP1", "BTKP10"]:
            bt = points.get((snap, model), [])
            n = min(len(pl), len(bt))
            if n == 0:
                continue
            pln = pl[:n]
            btn = bt[:n]
            pl_dn = values(pln, "dn_dlog10M")
            bt_dn = values(btn, "dn_dlog10M")
            valid = (pl_dn > 0) & (bt_dn > 0)
            ratio = bt_dn[valid] / pl_dn[valid]
            err = ratio * np.sqrt(
                (values(btn, "poisson_err")[valid] / bt_dn[valid]) ** 2
                + (values(pln, "poisson_err")[valid] / pl_dn[valid]) ** 2
            )
            mass = 10 ** (0.5 * (values(btn, "log10_M_FOF_Msun")[valid] + values(pln, "log10_M_FOF_Msun")[valid]))
            bt_pl_cache[(snap, model)] = (mass, ratio, err)
            bt_pl_values.extend(ratio)
    bt_pl_ylim = ratio_ylim(bt_pl_values)
    sim_reed_ylim = SIM_REED_YLIM

    fig = plt.figure(figsize=(8.6, 8.25))
    outer = gridspec.GridSpec(2, 3, figure=fig, left=0.09, right=0.995, bottom=0.075, top=0.985, hspace=0.22, wspace=0.10)
    for idx, snap in enumerate(SNAPS):
        inner = gridspec.GridSpecFromSubplotSpec(3, 1, subplot_spec=outer[idx], height_ratios=[4.0, 1.15, 1.25], hspace=0.08)
        ax = fig.add_subplot(inner[0])
        ax_bt = fig.add_subplot(inner[1], sharex=ax)
        ax_model = fig.add_subplot(inner[2], sharex=ax)
        row = idx // 3
        col = idx % 3
        redshift = first_redshift(points, snap)

        for model, style in MODELS.items():
            p = points.get((snap, model), [])
            r = ratios.get((snap, model), [])
            if r:
                ax.plot(10 ** values(r, "log10_M_FOF_Msun"), values(r, "reed07_dndlog10M_interp"), style["linestyle"], color=style["color"], lw=1.15)
                ax_model.errorbar(
                    10 ** values(r, "log10_M_FOF_Msun"),
                    values(r, "sim_over_reed07"),
                    yerr=values(r, "ratio_err"),
                    fmt=style["marker"],
                    color=style["color"],
                    markersize=2.8,
                    capsize=1.2,
                    markerfacecolor="white",
                    markeredgewidth=0.7,
                    elinewidth=0.55,
                )
            if p:
                ax.errorbar(
                    10 ** values(p, "log10_M_FOF_Msun"),
                    values(p, "dn_dlog10M"),
                    yerr=values(p, "poisson_err"),
                    fmt=style["marker"],
                    color=style["color"],
                    markersize=3.0,
                    capsize=1.3,
                    markerfacecolor="white",
                    markeredgewidth=0.75,
                    elinewidth=0.6,
                )

        for model in ["BTKP1", "BTKP10"]:
            if (snap, model) not in bt_pl_cache:
                continue
            mass, ratio, err = bt_pl_cache[(snap, model)]
            style = MODELS[model]
            ax_bt.errorbar(mass, ratio, yerr=err, fmt=style["marker"], color=style["color"], markersize=2.9, capsize=1.2, markerfacecolor="white", markeredgewidth=0.7, elinewidth=0.55)

        for ratio_ax in (ax_bt, ax_model):
            ratio_ax.axhline(1.0, color="0.2", lw=0.7, alpha=0.65)
            ratio_ax.axhline(2.0, color="0.5", ls=":", lw=0.6, alpha=0.55)
            ratio_ax.axhline(5.0, color="0.5", ls=":", lw=0.6, alpha=0.55)
            ratio_ax.set(xscale="log", yscale="log", xlim=(HMF_XMIN_MSUN, HMF_XMAX_MSUN))
            format_axes(ratio_ax, grid=True)
            mark_resolution(ratio_ax)
        ax_bt.set_ylim(*bt_pl_ylim)
        ax_model.set_ylim(*sim_reed_ylim)
        set_log_ticks(ax_bt, ratio=True, ratio_ticks=BT_PL_LABEL_TICKS)
        set_log_ticks(ax_model, ratio=True, ratio_ticks=SIM_REED_LABEL_TICKS)

        ax.set(xscale="log", yscale="log", xlim=(HMF_XMIN_MSUN, HMF_XMAX_MSUN), ylim=(1e-7 if redshift >= 8 else 1e-4, 1e2))
        format_axes(ax, grid=True)
        mark_resolution(ax)
        set_log_ticks(ax)
        panel_label(ax, rf"$z={format_redshift(redshift, 2)}$", loc=(0.95, 0.92), ha="right", fontsize=10.5)

        ax_model.set_xlabel(r"$M_{\mathrm{FOF}}\,[M_\odot]$", fontweight="bold", labelpad=5)
        ax.tick_params(labelbottom=False)
        ax_bt.tick_params(labelbottom=False)
        if col == 0:
            ax.set_ylabel(r"$dn/d\log_{10}M\,[{\rm Mpc}^{-3}]$", fontweight="bold", labelpad=5)
            ax_bt.set_ylabel(r"$f_{\rm BT}/f_{\rm PL}$", fontweight="bold", labelpad=5)
            ax_model.set_ylabel(r"$\mathrm{sim}/\mathrm{Reed07}$", fontweight="bold", labelpad=5)
        else:
            ax.tick_params(labelleft=False)
            ax_bt.tick_params(labelleft=False)
            ax_model.tick_params(labelleft=False)

    handles = []
    labels = []
    for model, style in MODELS.items():
        line = plt.Line2D([0], [0], color=style["color"], ls=style["linestyle"], lw=1.15)
        point = plt.Line2D([0], [0], color=style["color"], marker=style["marker"], markerfacecolor="white", ls="", markersize=3.0)
        handles.append((line, point))
        labels.append(MODEL_LABELS[model])
    fig.axes[0].legend(handles, labels, loc="lower left", fontsize=8.8, frameon=True, framealpha=0.75, edgecolor="none")
    fig.savefig(OUTPUT_PATH, dpi=120, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
