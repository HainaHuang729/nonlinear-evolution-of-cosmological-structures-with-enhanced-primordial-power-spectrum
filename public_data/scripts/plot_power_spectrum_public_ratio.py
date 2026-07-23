#!/usr/bin/env python
"""Replot the nonlinear power-spectrum figure from public figure data.

This lightweight path avoids regenerating the HMcode curves.  It uses the
HMcode values already tabulated at the simulation bins in the public residual
table, then plots the validation panels as direct sim/HMcode ratios.
"""

from collections import defaultdict
from pathlib import Path
import csv
import os
import sys

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator, NullFormatter


SCRIPT_PATH = Path(__file__).resolve()
ARTICLE_ROOT = next(
    (p for p in SCRIPT_PATH.parents if (p / "main.tex").exists()),
    SCRIPT_PATH.parents[2],
)
PUBLIC_DATA_ROOT = ARTICLE_ROOT / "public_data"
STYLE_ROOT = next(
    (
        p
        for p in (SCRIPT_PATH.parent, *SCRIPT_PATH.parents)
        if (p / "cosmology_plot_style.py").exists()
    ),
    SCRIPT_PATH.parent,
)
if str(STYLE_ROOT) not in sys.path:
    sys.path.insert(0, str(STYLE_ROOT))

from cosmology_plot_style import (  # noqa: E402
    JOURNAL_COLORS,
    apply_journal_style,
    format_axes,
    format_redshift,
    panel_label,
)


SNAP_LIST = ["0056", "0048", "0040", "0032"]
SNAP_SET = set(SNAP_LIST)
OUTPUT_PATH = Path(
    os.environ.get("POWER_SPECTRUM_OUTPUT_PATH", ARTICLE_ROOT / "power-spectrum.png")
)
FIGURE_DATA_ROOT = PUBLIC_DATA_ROOT / "figure_data" / "nonlinear_power_spectrum"
MEASUREMENT_CSV_PATH = FIGURE_DATA_ROOT / "power_spectrum_measurements.csv"
RATIO_CSV_PATH = FIGURE_DATA_ROOT / "power_spectrum_ratios.csv"
POWER_RESIDUAL_CSV_PATH = FIGURE_DATA_ROOT / "power_spectrum_hmcode_residuals.csv"

H_VAL = 0.6736
MESH_N = 1024
K_NY_25 = np.pi * MESH_N / 25.0
K_NY_256 = np.pi * MESH_N / 256.0
K_MIN_25 = 4.0 * (2.0 * np.pi / 25.0)
K_MIN_256 = 4.0 * (2.0 * np.pi / 256.0)
TRUSTED_K_RANGES = {
    "25": (K_MIN_25, K_NY_25),
    "256": (K_MIN_256, K_NY_256),
}
POWER_RATIO_YLIM = (0.5, 10.0)
POWER_RATIO_TICKS = np.array([0.5, 1.0, 2.0, 5.0, 10.0])
POWER_RESIDUAL_YLIM = (0.15, 2.0)
POWER_RESIDUAL_TICKS = np.array([0.2, 0.5, 1, 2.0])
TOP_MARKER_COUNT = 24
RATIO_MARKER_COUNT = 24
RESIDUAL_MARKER_COUNT = 16
SIM_LINEWIDTH = 0.55
SIM_ALPHA = 0.68
UNTRUSTED_ALPHA = 0.36

MODEL_ALIASES = {
    "BT_soft": "BTKP1",
    "BT_deep": "BTKP10",
    "BT_kp1": "BTKP1",
    "BT_kp10": "BTKP10",
    "BTKP1": "BTKP1",
    "BTKP10": "BTKP10",
    "PL": "PL",
}
TEXT_ALIASES = {
    "BT_soft": "BTKP1",
    "BT_deep": "BTKP10",
    "BT soft": "BTKP1",
    "BT deep": "BTKP10",
}

MODEL_COLORS = {
    "PL": JOURNAL_COLORS["black"],
    "BTKP1": JOURNAL_COLORS["blue"],
    "BTKP10": JOURNAL_COLORS["green"],
}
MODEL_MARKERS = {"PL": "o", "BTKP1": "^", "BTKP10": "s"}

THEORY_STYLES = {
    "PL": {"color": MODEL_COLORS["PL"], "linestyle": "-", "label": "PL theory"},
    "BTKP1": {
        "color": MODEL_COLORS["BTKP1"],
        "linestyle": "--",
        "label": r"BT $k_p=1$ theory",
    },
    "BTKP10": {
        "color": MODEL_COLORS["BTKP10"],
        "linestyle": "-.",
        "label": r"BT $k_p=10$ theory",
    },
}

BOX_MODELS = {
    "25": {
        "filled_markers": True,
        "pl_family": "cdm_25",
        "pl_label": "PL (25)",
        "pl_marker": MODEL_MARKERS["PL"],
        "pl_color": MODEL_COLORS["PL"],
        "bt_models": {
            "BTKP1": {
                "family": "bluetilted_kp1_ms1.5_25",
                "ratio_model": "BTKP1",
                "bt_label": r"BT $k_p=1$ (25)",
                "ratio_label": r"BT $k_p=1$ (25) / PL (25)",
                "bt_marker": MODEL_MARKERS["BTKP1"],
                "bt_color": MODEL_COLORS["BTKP1"],
            },
            "BTKP10": {
                "family": "bluetilted_kp10_ms1.5_25",
                "ratio_model": "BTKP10",
                "bt_label": r"BT $k_p=10$ (25)",
                "ratio_label": r"BT $k_p=10$ (25) / PL (25)",
                "bt_marker": MODEL_MARKERS["BTKP10"],
                "bt_color": MODEL_COLORS["BTKP10"],
            },
        },
    },
    "256": {
        "filled_markers": False,
        "pl_family": "new_PL_256_1024",
        "pl_label": "PL (256)",
        "pl_marker": MODEL_MARKERS["PL"],
        "pl_color": MODEL_COLORS["PL"],
        "bt_models": {
            "BTKP1": {
                "family": "bluetilted_kp1_ms1.5_256",
                "ratio_model": "BTKP1",
                "bt_label": r"BT $k_p=1$ (256)",
                "ratio_label": r"BT $k_p=1$ (256) / PL (256)",
                "bt_marker": MODEL_MARKERS["BTKP1"],
                "bt_color": MODEL_COLORS["BTKP1"],
            },
            "BTKP10": {
                "family": "bluetilted_kp10_ms1.5_256",
                "ratio_model": "BTKP10",
                "bt_label": r"BT $k_p=10$ (256)",
                "ratio_label": r"BT $k_p=10$ (256) / PL (256)",
                "bt_marker": MODEL_MARKERS["BTKP10"],
                "bt_color": MODEL_COLORS["BTKP10"],
            },
        },
    },
}


def canonical_model(value):
    return MODEL_ALIASES.get(str(value), str(value))


def canonical_text(value):
    text = str(value)
    for old, new in TEXT_ALIASES.items():
        text = text.replace(old, new)
    return text


def snap_key(value):
    text = str(value).strip()
    return text.zfill(4) if text.isdigit() else text


def box_key(value):
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def as_float(value, default=np.nan):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def valid_positive(value):
    return np.isfinite(value) and value > 0


def row_arrays(rows, y_key):
    return (
        np.asarray([row["k_hMpc"] for row in rows], dtype=float),
        np.asarray([row[y_key] for row in rows], dtype=float),
    )


def log_spaced_marker_indices(k_values, max_markers):
    """Select visually even marker locations without dropping the plotted curve."""
    k_values = np.asarray(k_values, dtype=float)
    valid_indices = np.flatnonzero(np.isfinite(k_values) & (k_values > 0.0))
    if valid_indices.size <= max_markers:
        return valid_indices

    log_k = np.log10(k_values[valid_indices])
    targets = np.linspace(log_k.min(), log_k.max(), max_markers)
    return np.unique(
        [valid_indices[np.argmin(np.abs(log_k - target))] for target in targets]
    )


def plot_simulation_series(
    ax,
    k_values,
    y_values,
    *,
    box_key,
    color,
    marker,
    max_markers,
    log_y=False,
    connect=False,
):
    """Plot trusted markers normally and retain excluded points as faded open markers."""
    k_values = np.asarray(k_values, dtype=float)
    y_values = np.asarray(y_values, dtype=float)
    valid = np.isfinite(k_values) & np.isfinite(y_values) & (k_values > 0) & (y_values > 0)
    k_values = k_values[valid]
    y_values = y_values[valid]
    if not len(k_values):
        return

    plotter = ax.loglog if log_y else ax.semilogx
    k_min, k_max = TRUSTED_K_RANGES[box_key]
    trusted = (k_values >= k_min) & (k_values <= k_max)

    if connect:
        plotter(
            k_values,
            y_values,
            color=color,
            linestyle="-",
            linewidth=SIM_LINEWIDTH,
            alpha=UNTRUSTED_ALPHA,
        )
        plotter(
            k_values[trusted],
            y_values[trusted],
            color=color,
            linestyle="-",
            linewidth=SIM_LINEWIDTH,
            alpha=SIM_ALPHA,
        )

    marker_indices = log_spaced_marker_indices(k_values, max_markers)
    marker_k = k_values[marker_indices]
    marker_y = y_values[marker_indices]
    marker_trusted = trusted[marker_indices]

    if np.any(marker_trusted):
        plotter(
            marker_k[marker_trusted],
            marker_y[marker_trusted],
            color=color,
            linestyle="",
            marker=marker,
            markersize=3.4,
            markerfacecolor=color if BOX_MODELS[box_key]["filled_markers"] else "none",
            markeredgewidth=0.75,
            alpha=SIM_ALPHA,
        )
    if np.any(~marker_trusted):
        plotter(
            marker_k[~marker_trusted],
            marker_y[~marker_trusted],
            color=color,
            linestyle="",
            marker=marker,
            markersize=3.4,
            markerfacecolor="none",
            markeredgewidth=0.75,
            alpha=UNTRUSTED_ALPHA,
        )


def needed_measurement_families():
    families = set()
    for box in BOX_MODELS.values():
        families.add(box["pl_family"])
        for config in box["bt_models"].values():
            families.add(config["family"])
    return families


def read_public_tables():
    measurements = defaultdict(list)
    ratios = defaultdict(list)
    residuals = defaultdict(list)
    theory_rows = defaultdict(list)
    family_filter = needed_measurement_families()

    with MEASUREMENT_CSV_PATH.open(newline="") as handle:
        for row in csv.DictReader(handle):
            family = row.get("family", "")
            snap = snap_key(row.get("snapshot", ""))
            if family not in family_filter or snap not in SNAP_SET:
                continue
            k_val = as_float(row.get("k_hMpc"))
            p_val = as_float(row.get("P_Mpc_over_h_cubed"))
            if not (valid_positive(k_val) and valid_positive(p_val)):
                continue
            measurements[(family, snap)].append(
                {
                    "redshift": as_float(row.get("redshift")),
                    "k_hMpc": k_val,
                    "P_Mpc_over_h_cubed": p_val,
                }
            )

    with RATIO_CSV_PATH.open(newline="") as handle:
        for row in csv.DictReader(handle):
            snap = snap_key(row.get("snapshot", ""))
            model = canonical_model(row.get("model", ""))
            box = box_key(row.get("box_hinv_Mpc", ""))
            if snap not in SNAP_SET or model not in {"BTKP1", "BTKP10"} or box not in BOX_MODELS:
                continue
            k_val = as_float(row.get("k_hMpc"))
            ratio_val = as_float(row.get("P_model_over_P_PL"))
            if not (valid_positive(k_val) and np.isfinite(ratio_val)):
                continue
            ratios[(box, model, snap)].append(
                {"k_hMpc": k_val, "P_model_over_P_PL": ratio_val}
            )

    with POWER_RESIDUAL_CSV_PATH.open(newline="") as handle:
        for row in csv.DictReader(handle):
            snap = snap_key(row.get("snapshot", ""))
            model = canonical_model(row.get("model", ""))
            box = box_key(row.get("box_hinv_Mpc", ""))
            if snap not in SNAP_SET or model not in THEORY_STYLES or box not in BOX_MODELS:
                continue
            k_val = as_float(row.get("k_hMpc"))
            p_sim = as_float(row.get("P_sim_Mpc_over_h_cubed"))
            p_hm = as_float(row.get("P_hmcode_Mpc_over_h_cubed"))
            sim_over = as_float(row.get("sim_over_hmcode"))
            if not np.isfinite(sim_over):
                sim_over = as_float(row.get("sim_over_hmcode_minus_1")) + 1.0
            if not (valid_positive(k_val) and valid_positive(p_hm)):
                continue
            theory_rows[(model, snap)].append(
                {"k_hMpc": k_val, "P_hmcode_Mpc_over_h_cubed": p_hm}
            )
            if not valid_positive(sim_over):
                continue
            residuals[(box, model, snap)].append(
                {
                    "k_hMpc": k_val,
                    "P_sim_Mpc_over_h_cubed": p_sim,
                    "P_hmcode_Mpc_over_h_cubed": p_hm,
                    "sim_over_hmcode": sim_over,
                }
            )

    for table in (measurements, ratios, residuals, theory_rows):
        for key, rows in table.items():
            rows.sort(key=lambda item: item["k_hMpc"])

    return measurements, ratios, residuals, theory_rows


def panel_measurements(measurements, family, snap):
    return measurements.get((family, snap), [])


def theory_curve(theory_rows, model, snap):
    rows = theory_rows.get((model, snap), [])
    if not rows:
        return np.asarray([]), np.asarray([])
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["k_hMpc"]].append(row["P_hmcode_Mpc_over_h_cubed"])
    k_vals = np.asarray(sorted(grouped), dtype=float)
    p_vals = np.asarray([np.median(grouped[k_val]) for k_val in k_vals], dtype=float)
    return (
        k_vals,
        p_vals,
    )


def log_interp(x, x_ref, y_ref):
    x = np.asarray(x, dtype=float)
    x_ref = np.asarray(x_ref, dtype=float)
    y_ref = np.asarray(y_ref, dtype=float)
    valid_ref = np.isfinite(x_ref) & np.isfinite(y_ref) & (x_ref > 0) & (y_ref > 0)
    valid_x = np.isfinite(x) & (x > 0)
    result = np.full_like(x, np.nan, dtype=float)
    if np.count_nonzero(valid_ref) < 2:
        return result
    in_range = valid_x & (x >= x_ref[valid_ref].min()) & (x <= x_ref[valid_ref].max())
    result[in_range] = 10 ** np.interp(
        np.log10(x[in_range]),
        np.log10(x_ref[valid_ref]),
        np.log10(y_ref[valid_ref]),
    )
    return result


def mark_reliability(ax_top, ax_ratio, annotate=False):
    for ax in (ax_top, ax_ratio):
        ax.axvline(K_MIN_256, color="0.35", linestyle=":", linewidth=0.8, alpha=0.8, zorder=1)
        ax.axvline(K_NY_256, color="0.35", linestyle=":", linewidth=0.8, alpha=0.8, zorder=1)
        ax.axvline(K_MIN_25, color="0.25", linestyle="--", linewidth=0.85, alpha=0.85, zorder=1)
        ax.axvline(K_NY_25, color="0.25", linestyle="--", linewidth=0.85, alpha=0.85, zorder=1)
        ax.axvspan(1.0e-2, K_MIN_256, color="0.82", alpha=0.16, lw=0, zorder=0)
        ax.axvspan(K_NY_25, 1.0e3, color="0.82", alpha=0.16, lw=0, zorder=0)
    if annotate:
        ax_top.text(
            0.96,
            0.72,
            r"vertical pairs: $4k_{\rm f}$, $k_{\rm Ny}$"
            + "\n"
            + r"dotted: 256; dashed: 25",
            transform=ax_top.transAxes,
            ha="right",
            va="top",
            fontsize=7.0,
            color="0.25",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.80, "pad": 0.9},
        )


def mark_residual_reliability(ax, box_key):
    k_min, k_max = TRUSTED_K_RANGES[box_key]
    linestyle = "--" if box_key == "25" else ":"
    color = "0.25" if box_key == "25" else "0.35"
    linewidth = 0.85 if box_key == "25" else 0.8
    ax.axvline(k_min, color=color, linestyle=linestyle, linewidth=linewidth, alpha=0.85, zorder=1)
    ax.axvline(k_max, color=color, linestyle=linestyle, linewidth=linewidth, alpha=0.85, zorder=1)
    ax.axvspan(1.0e-2, k_min, color="0.82", alpha=0.16, lw=0, zorder=0)
    ax.axvspan(k_max, 1.0e3, color="0.82", alpha=0.16, lw=0, zorder=0)
    ax.axhspan(0.9, 1.1, color="0.45", alpha=0.10, lw=0, zorder=0)


def ratio_tick_label(value, _pos, *, decade_only=False):
    if value <= 0 or not np.isfinite(value):
        return ""
    exponent = np.log10(value)
    rounded = int(np.rint(exponent))
    if np.isclose(exponent, rounded, atol=1.0e-10):
        return rf"$10^{{{rounded}}}$"
    if decade_only:
        return ""
    return f"{value:g}"


def set_ratio_yaxis(ax, ylim, ticks, *, decade_labels_only=False):
    ax.set_yscale("log")
    ax.set_ylim(*ylim)
    visible_ticks = ticks[(ticks >= ylim[0]) & (ticks <= ylim[1])]
    ax.yaxis.set_major_locator(FixedLocator(visible_ticks))
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, pos: ratio_tick_label(value, pos, decade_only=decade_labels_only))
    )
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=20))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="y", which="major", labelsize=7.0, pad=1.0)
    for tick_label in ax.get_yticklabels():
        tick_label.set_verticalalignment("center")


def redshift_for_snap(measurements, snap):
    rows = panel_measurements(measurements, "cdm_25", snap)
    if not rows:
        return np.nan
    return float(np.nanmedian([row["redshift"] for row in rows]))


def plot_power_spectrum():
    apply_journal_style(base_fontsize=9.0)
    measurements, ratios, residuals, theory_rows = read_public_tables()

    model_legend_handles = [
        plt.Line2D(
            [0],
            [0],
            color=THEORY_STYLES[model]["color"],
            linestyle=THEORY_STYLES[model]["linestyle"],
            linewidth=1.25,
            marker=MODEL_MARKERS[model],
            markersize=4.0,
            markerfacecolor=THEORY_STYLES[model]["color"],
            markeredgewidth=0.7,
        )
        for model in ("PL", "BTKP1", "BTKP10")
    ]
    model_legend_labels = ["PL", r"BT $k_p=1$", r"BT $k_p=10$"]
    box_legend_handles = [
        plt.Line2D(
            [0],
            [0],
            color="0.15",
            linestyle="",
            marker="o",
            markersize=4.2,
            markerfacecolor=facecolor,
            markeredgewidth=0.8,
        )
        for facecolor in ("0.15", "none")
    ]
    box_legend_labels = [
        r"$25\,h^{-1}\,\mathrm{Mpc}$ (filled)",
        r"$256\,h^{-1}\,\mathrm{Mpc}$ (open)",
    ]
    excluded_legend_handle = plt.Line2D(
        [0],
        [0],
        color="0.35",
        linestyle="",
        marker="o",
        markersize=4.2,
        markerfacecolor="none",
        markeredgewidth=0.8,
        alpha=UNTRUSTED_ALPHA,
    )

    fig = plt.figure(figsize=(8.8, 8.9))
    outer_grid = gridspec.GridSpec(
        2,
        2,
        figure=fig,
        left=0.105,
        right=0.985,
        bottom=0.090,
        top=0.965,
        hspace=0.12,
        wspace=0.10,
    )

    for idx, snap in enumerate(SNAP_LIST):
        inner_grid = gridspec.GridSpecFromSubplotSpec(
            4,
            1,
            subplot_spec=outer_grid[idx],
            height_ratios=[3.0, 1.0, 0.92, 0.92],
            hspace=0.03,
        )
        ax_top = fig.add_subplot(inner_grid[0])
        ax_ratio = fig.add_subplot(inner_grid[1], sharex=ax_top)
        ax_residual_25 = fig.add_subplot(inner_grid[2], sharex=ax_top)
        ax_residual_256 = fig.add_subplot(inner_grid[3], sharex=ax_top)
        residual_axes = {"25": ax_residual_25, "256": ax_residual_256}
        residual_values = {box_key: [] for box_key in BOX_MODELS}

        row = idx // 2
        col = idx % 2
        pl_z = redshift_for_snap(measurements, snap)

        theory_data = {}
        for model, style in THEORY_STYLES.items():
            k_theory, p_theory = theory_curve(theory_rows, model, snap)
            theory_data[model] = (k_theory, p_theory)
            if len(k_theory):
                ax_top.loglog(
                    k_theory,
                    p_theory,
                    style["linestyle"],
                    color=style["color"],
                    linewidth=1.25,
                    alpha=0.9,
                    label=style["label"],
                )

        k_pl_theory, p_pl_theory = theory_data["PL"]
        for model in ("BTKP1", "BTKP10"):
            k_bt_theory, p_bt_theory = theory_data[model]
            p_pl_interp = log_interp(k_bt_theory, k_pl_theory, p_pl_theory)
            valid = np.isfinite(p_pl_interp) & (p_pl_interp > 0)
            if np.any(valid):
                style = THEORY_STYLES[model]
                ax_ratio.semilogx(
                    k_bt_theory[valid],
                    p_bt_theory[valid] / p_pl_interp[valid],
                    style["linestyle"],
                    color=style["color"],
                    linewidth=1.2,
                    alpha=0.85,
                    label=style["label"].replace(" theory", r" theory / PL"),
                )

        for box_key, box in BOX_MODELS.items():
            pl_rows = panel_measurements(measurements, box["pl_family"], snap)
            if pl_rows:
                k_vals, p_vals = row_arrays(pl_rows, "P_Mpc_over_h_cubed")
                plot_simulation_series(
                    ax_top,
                    k_vals,
                    p_vals,
                    box_key=box_key,
                    color=box["pl_color"],
                    marker=box["pl_marker"],
                    max_markers=TOP_MARKER_COUNT,
                    log_y=True,
                )

            for bt_model, bt_config in box["bt_models"].items():
                bt_rows = panel_measurements(measurements, bt_config["family"], snap)
                if bt_rows:
                    k_vals, p_vals = row_arrays(bt_rows, "P_Mpc_over_h_cubed")
                    plot_simulation_series(
                        ax_top,
                        k_vals,
                        p_vals,
                        box_key=box_key,
                        color=bt_config["bt_color"],
                        marker=bt_config["bt_marker"],
                        max_markers=TOP_MARKER_COUNT,
                        log_y=True,
                    )

                ratio_rows = ratios.get((box_key, bt_config["ratio_model"], snap), [])
                if ratio_rows:
                    k_vals, ratio_vals = row_arrays(ratio_rows, "P_model_over_P_PL")
                    plot_simulation_series(
                        ax_ratio,
                        k_vals,
                        ratio_vals,
                        box_key=box_key,
                        color=bt_config["bt_color"],
                        marker=bt_config["bt_marker"],
                        max_markers=RATIO_MARKER_COUNT,
                    )

        for box_key, ax_residual in residual_axes.items():
            box = BOX_MODELS[box_key]
            for model in ("PL", "BTKP1", "BTKP10"):
                rows = residuals.get((box_key, model, snap), [])
                if not rows:
                    continue
                if model == "PL":
                    marker = box["pl_marker"]
                    color = box["pl_color"]
                else:
                    marker = box["bt_models"][model]["bt_marker"]
                    color = box["bt_models"][model]["bt_color"]
                k_vals, residual_ratio = row_arrays(rows, "sim_over_hmcode")
                plot_simulation_series(
                    ax_residual,
                    k_vals,
                    residual_ratio,
                    box_key=box_key,
                    color=color,
                    marker=marker,
                    max_markers=RESIDUAL_MARKER_COUNT,
                    connect=True,
                )
                residual_values[box_key].extend(
                    row["sim_over_hmcode"] for row in rows
                )

        ax_ratio.axhline(1.0, color="0.45", linestyle=":", linewidth=0.8)
        mark_reliability(ax_top, ax_ratio, annotate=(idx == 0))
        for box_key, ax_residual in residual_axes.items():
            ax_residual.axhline(1.0, color="0.45", linestyle=":", linewidth=0.8)
            mark_residual_reliability(ax_residual, box_key)
            panel_label(
                ax_residual,
                rf"${box_key}\,h^{{-1}}\,\mathrm{{Mpc}}$",
                loc=(0.97, 0.84),
                ha="right",
                fontsize=6.7,
            )

        ax_top.set_xlim(1e-2, 1e3)
        ax_top.set_ylim(1e-5, 1e5)
        set_ratio_yaxis(
            ax_ratio,
            POWER_RATIO_YLIM,
            POWER_RATIO_TICKS,
            decade_labels_only=False,
        )
        for ax_residual in residual_axes.values():
            set_ratio_yaxis(ax_residual, POWER_RESIDUAL_YLIM, POWER_RESIDUAL_TICKS)

        format_axes(ax_top)
        format_axes(ax_ratio)
        for ax_residual in residual_axes.values():
            format_axes(ax_residual)

        if col == 0:
            ax_top.set_ylabel(r"$P(k)\,[(\mathrm{Mpc}/h)^3]$", fontweight="bold", labelpad=5)
            ax_ratio.set_ylabel("BT/PL", fontweight="bold", labelpad=5)
            ax_residual_25.set_ylabel(r"sim/HM", fontweight="bold", labelpad=5)
            ax_residual_256.set_ylabel(r"sim/HM", fontweight="bold", labelpad=5)
        else:
            ax_top.tick_params(labelleft=False)
            ax_ratio.tick_params(labelleft=False)
            ax_residual_25.tick_params(labelleft=False)
            ax_residual_256.tick_params(labelleft=False)
        ax_residual_256.set_xlabel(r"$k\,[h\,\mathrm{Mpc}^{-1}]$", fontweight="bold", labelpad=5)
        ax_ratio.tick_params(labelbottom=False)
        ax_residual_25.tick_params(labelbottom=False)

        panel_label(
            ax_top,
            rf"$z={format_redshift(pl_z, 2)}$",
            loc=(0.94, 0.90),
            ha="right",
            fontsize=9.5,
        )
        plt.setp(ax_top.get_xticklabels(), visible=False)

        if idx == 0:
            ax_top.legend(
                model_legend_handles,
                model_legend_labels,
                loc="lower left",
                ncol=1,
                fontsize=7.2,
                title="Model: theory line / Sim marker",
                title_fontsize=6.8,
                frameon=True,
                framealpha=0.72,
                edgecolor="none",
                borderpad=0.25,
                labelspacing=0.18,
                handletextpad=0.35,
            )
        elif idx == 1:
            ax_top.legend(
                box_legend_handles,
                box_legend_labels,
                loc="lower left",
                bbox_to_anchor=(0.03, 0.05),
                ncol=1,
                fontsize=7.0,
                title="Simulation box",
                title_fontsize=6.8,
                frameon=True,
                framealpha=0.72,
                edgecolor="none",
                borderpad=0.2,
                handlelength=1.45,
                handletextpad=0.35,
                labelspacing=0.16,
            )
        elif idx == 2:
            ax_top.legend(
                [excluded_legend_handle],
                ["outside adopted range"],
                loc="lower left",
                fontsize=7.0,
                frameon=True,
                framealpha=0.72,
                edgecolor="none",
                borderpad=0.2,
                handlelength=1.45,
                handletextpad=0.35,
            )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    plot_power_spectrum()
