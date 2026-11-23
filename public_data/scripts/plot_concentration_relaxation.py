#!/usr/bin/env python3
"""Plot the relaxation-split and full-sample concentration-mass comparison figures."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter, PercentFormatter
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(
    (parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists()),
    SCRIPT_DIR.parents[1],
)
DATA_DIR = ARTICLE_ROOT / "public_data" / "figure_data" / "concentration_relaxation"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import cosmology_plot_style as style  # noqa: E402

MODELS = ("PL", "BTKP1", "BTKP10")
LABELS = ("PL", r"BT $k_p=1$", r"BT $k_p=10$")
MARKERS = ("o", "^", "s")
MIN_HALOS = 20
PANELS = (
    ("0056", "0.00", (8, 13.5), (0.55, 2.18)),
    ("0048", "1.07", (8, 13.5), (0.38, 1.82)),
    ("0040", "3.44", (8, 12.65), (0.20, 1.28)),
    ("0032", "8.52", (8, 11.65), (0.00, 1.05)),
)
MASS_LABEL = r"$\log_{10}(M_{200c}/M_{\odot})$"
PRESCRIPTION_LABEL = {"I21R": "I21 relaxed"}
CONC_LABEL = r"$\log_{10}(c_{200c})$"


def read_rows(data_dir: Path, name: str) -> list[dict[str, str]]:
    with (data_dir / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def i21_plot_rows(
    rows: list[dict[str, str]],
    selection_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    """Attach I21-selected measurements on the evaluated comparison bins."""
    fields = ("model", "snapshot", "log10_mass_center")
    selected = {tuple(row[key] for key in fields): row for row in selection_rows}
    result: list[dict[str, object]] = []
    for row in rows:
        key = tuple(row[field] for field in fields)
        match = selected.get(key)
        if match is None:
            result.append(
                row
                | {
                    "n_relaxed": 0,
                    "c200c_relaxed": np.nan,
                    "logc_relaxed_p16": np.nan,
                    "logc_relaxed_p84": np.nan,
                    "relaxed_fraction_all": np.nan,
                    "relaxed_fraction_upper": np.nan,
                }
            )
            continue
        total = int(row["n_all"])
        if total != int(match["n_all"]):
            raise ValueError(f"Mismatched bin halo count for {key}: {total} != {match['n_all']}")
        count = int(match["n_i21_bound"])
        unknown = int(match["n_missing_bound"])
        result.append(
            row
            | {
                "n_relaxed": count,
                "c200c_relaxed": match["c200c_relaxed_bound"],
                "logc_relaxed_p16": match["logc_relaxed_p16_bound"],
                "logc_relaxed_p84": match["logc_relaxed_p84_bound"],
                "relaxed_fraction_all": count / total,
                "relaxed_fraction_upper": (count + unknown) / total,
            }
        )
    return result


def series(rows: list[dict[str, object]], model: str, snapshot: str) -> dict[str, np.ndarray]:
    subset = sorted(
        (row for row in rows if row["model"] == model and row["snapshot"] == snapshot),
        key=lambda row: float(row["log10_mass_center"]),
    )
    return {
        key: np.array([float(row[key]) for row in subset])
        for key in subset[0]
        if key not in {"model", "strict_all", "strict_matched"}
    }


def positive_log10(values: np.ndarray) -> np.ndarray:
    return np.log10(values, out=np.full_like(values, np.nan), where=values > 0)


def points(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    count: np.ndarray,
    color: str,
    marker: str,
    filled: bool,
) -> np.ndarray:
    selected = np.isfinite(y) & (count >= MIN_HALOS)
    ax.plot(
        x[selected],
        y[selected],
        linestyle="none",
        marker=marker,
        color=color,
        markersize=5.0,
        markeredgewidth=1.05,
        markerfacecolor=color if filled else "white",
        zorder=5 if filled else 4,
    )
    return selected


def setup(ax: plt.Axes, *, shade: bool = False) -> None:
    style.format_axes(ax, grid=True)
    ax.set_axisbelow(True)
    if shade:
        ax.axvspan(8, np.log10(1.89e9), color="0.94", linewidth=0, zorder=0)
    for spine in ax.spines.values():
        spine.set_linewidth(1.45)
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontweight("bold")


def add_legend(fig: plt.Figure, colors: tuple[str, ...], prescription: str) -> None:
    model_handles = [
        Line2D(
            [],
            [],
            color=color,
            marker=marker,
            markerfacecolor=color if prescription in {"L16", "I21R"} else "white",
            linestyle="none",
            markersize=5,
            label=label,
        )
        for color, marker, label in zip(colors, MARKERS, LABELS)
    ]
    theory_handle = Line2D(
        [],
        [],
        color="0.25",
        linestyle="--",
        linewidth=1.3,
        label=PRESCRIPTION_LABEL.get(prescription, prescription),
    )
    if prescription in {"D19", "L16", "I21R"}:
        handles = model_handles + [theory_handle]
    else:
        handles = model_handles + [
            Line2D([], [], color="0.25", marker="o", linestyle="none", markersize=5, label="Relaxed"),
            Line2D(
                [],
                [],
                color="0.25",
                marker="o",
                markerfacecolor="white",
                linestyle="none",
                markersize=5,
                label="Unrelaxed (top), all halos (middle)",
            ),
            theory_handle,
        ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.014),
        ncols=len(handles),
        fontsize=10.6,
        columnspacing=1.0,
        handletextpad=0.36,
    )


def grid_around_redshift(ax: plt.Axes, label: plt.Text, renderer: object) -> None:
    """Keep grid lines clear of the measured redshift-label bounding box."""
    box = label.get_window_extent(renderer).padded(renderer.points_to_pixels(2.5))
    (left, bottom), (right, top) = ax.transAxes.inverted().transform(box.get_points())
    ax.grid(False)
    for ticks, limits, lower, upper, gap_start, gap_end, vertical in (
        (ax.get_xticks(), ax.get_xlim(), left, right, bottom, top, True),
        (ax.get_yticks(), ax.get_ylim(), bottom, top, left, right, False),
    ):
        minimum, maximum = limits
        for tick in ticks:
            fraction = (tick - minimum) / (maximum - minimum)
            if not 0 < fraction < 1:
                continue
            segments = ((0, gap_start), (gap_end, 1)) if lower < fraction < upper else ((0, 1),)
            for segment in segments:
                fixed = [fraction, fraction]
                x, y = (fixed, segment) if vertical else (segment, fixed)
                ax.plot(x, y, transform=ax.transAxes, color="0.88", linewidth=0.5, zorder=0.9)


def bt_pl_ratios(
    ax: plt.Axes,
    measurements: dict[str, dict[str, np.ndarray]],
    colors: tuple[str, ...],
    sample: str,
    filled: bool,
) -> bool:
    pl = measurements["PL"]
    count_field = f"n_{sample}"
    concentration_field = f"c200c_{sample}"
    has_common_bins = False
    for model, color, marker in zip(MODELS[1:], colors[1:], MARKERS[1:]):
        bt = measurements[model]
        mass, bt_index, pl_index = np.intersect1d(
            bt["log10_mass_center"],
            pl["log10_mass_center"],
            return_indices=True,
        )
        count = np.minimum(bt[count_field][bt_index], pl[count_field][pl_index])
        numerator = bt[concentration_field][bt_index]
        denominator = pl[concentration_field][pl_index]
        ratio = np.divide(numerator, denominator, out=np.full_like(mass, np.nan), where=denominator > 0)
        shown = points(ax, mass, ratio, count, color, marker, filled)
        has_common_bins |= bool(shown.any())
    ax.axhline(1, color="0.45", linewidth=0.85)
    ax.set_ylim(0.62, 4.18)
    ax.set_yticks([1, 2, 3, 4])
    return has_common_bins


def overview(
    rows: list[dict[str, object]],
    colors: tuple[str, ...],
    prescription: str,
    curve_rows: list[dict[str, str]] | None = None,
    *,
    log_ratio: bool = True,
    bt_pl: bool = True,
    redshift_gap: float = 0.21,
) -> plt.Figure:
    spread = prescription in {"D19", "L16", "I21R"}
    relaxed_only = prescription in {"L16", "I21R"}
    if prescription == "D19":
        concentration_groups = ratio_groups = (("all", False),)
    elif relaxed_only:
        concentration_groups = ratio_groups = (("relaxed", True),)
    else:
        concentration_groups = (("unrelaxed", False), ("relaxed", True))
        ratio_groups = (("all", False), ("relaxed", True))

    fig = plt.figure(figsize=(8.6, 8.45))
    grid = fig.add_gridspec(
        2,
        2,
        left=0.115,
        right=0.985,
        bottom=0.107,
        top=0.972,
        wspace=0.17,
        hspace=redshift_gap,
    )
    add_legend(fig, colors, prescription)
    redshift_labels: list[tuple[plt.Axes, plt.Text]] = []

    for i, (snapshot, z, xlim, ylim) in enumerate(PANELS):
        row, column = divmod(i, 2)
        ratio_height = 1.95 if log_ratio else 1.55
        bottom_height = 1.71 if bt_pl else 1.30
        sub = grid[row, column].subgridspec(
            3, 1, height_ratios=(4.75, ratio_height, bottom_height), hspace=0.075
        )
        top = fig.add_subplot(sub[0])
        ratio = fig.add_subplot(sub[1], sharex=top)
        frac = fig.add_subplot(sub[2], sharex=top)
        ratios: list[float] = []
        concentrations: list[float] = []
        measurements = {model: series(rows, model, snapshot) for model in MODELS}

        for model, color, marker in zip(MODELS, colors, MARKERS):
            data = measurements[model]
            x = data["log10_mass_center"]
            theory = data[f"c200c_{prescription}"]
            fraction_count = data["n_relaxed" if relaxed_only else "n_all"]
            qualified = fraction_count >= MIN_HALOS
            if curve_rows is None:
                curve_x, curve_c = x, theory
            else:
                curve = [r for r in curve_rows if r["model"] == model and r["snapshot"] == snapshot]
                curve_x, curve_c = (
                    np.array([float(r[k]) for r in curve]) for k in ("log10_mass", "c200c_I21R")
                )
            top.plot(curve_x, positive_log10(curve_c), "--", color=color, linewidth=1.35, alpha=0.85)

            for group, filled in concentration_groups:
                logc = positive_log10(data[f"c200c_{group}"])
                selected = points(top, x, logc, data[f"n_{group}"], color, marker, filled)
                concentrations.extend(logc[selected])
                if spread:
                    lo = data[f"logc_{group}_p16"]
                    hi = data[f"logc_{group}_p84"]
                    ok = selected & np.isfinite(lo) & np.isfinite(hi)
                    top.errorbar(
                        x[ok],
                        logc[ok],
                        yerr=[logc[ok] - lo[ok], hi[ok] - logc[ok]],
                        fmt="none",
                        capsize=1.7,
                        linewidth=0.85,
                        capthick=0.85,
                        ecolor=color,
                        alpha=0.24 if group == "unrelaxed" else 0.67,
                        zorder=3 if filled else 2.5,
                    )
                    concentrations.extend(np.r_[lo[ok], hi[ok]])

            for group, filled in ratio_groups:
                values = data[f"c200c_{group}"] / theory
                selected = points(ratio, x, values, data[f"n_{group}"], color, marker, filled)
                ratios.extend(values[selected])

            if not bt_pl:
                low = data["relaxed_fraction_all"]
                high = data["relaxed_fraction_upper"]
                frac.fill_between(x, low, high, where=qualified, color=color, linewidth=0, alpha=0.13)
                frac.plot(x, np.where(qualified, low, np.nan), color=color, linestyle="-", linewidth=1, alpha=0.8)
                points(frac, x, low, fraction_count, color, marker, filled=True)

        top.set_xlim(xlim)
        top.set_xticks(np.arange(np.ceil(xlim[0]), xlim[1], 1))
        top.set_ylim(min(ylim[0], min(concentrations) - 0.05), max(ylim[1], max(concentrations) + 0.05))
        if snapshot == "0032":
            top.set_yticks([0.25, 0.50, 0.75, 1.00])

        ratio.axhline(1, color="0.45", linewidth=0.85)
        if log_ratio:
            low, high = min(ratios, default=1), max(ratios, default=1)
            if low <= 0:
                raise ValueError(f"Expected positive ratios for {prescription} {snapshot}, got {low}")
            extent = max(1.5, high * 1.08, 1.08 / low)
            ratio.set_yscale("log")
            ratio.set_ylim(1 / extent, extent)
            ratio.set_yticks([0.8, 1.0, 1.25], labels=["0.8", "1.0", "1.25"])
            ratio.yaxis.set_minor_locator(FixedLocator([0.7, 0.9, 1.1, 1.4]))
            ratio.yaxis.set_minor_formatter(NullFormatter())
        else:
            ratio.set_ylim(min(0.64, min(ratios, default=1) - 0.035), max(1.28, max(ratios, default=1) + 0.035))
            ratio.yaxis.set_major_locator(FixedLocator([0.8, 1.0, 1.2]))
            ratio.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
            ratio.yaxis.set_minor_locator(FixedLocator([0.7, 0.9, 1.1]))

        if bt_pl:
            sample = "relaxed" if relaxed_only else "all"
            has_common_bins = bt_pl_ratios(frac, measurements, colors, sample, relaxed_only)
        else:
            has_common_bins = True
            frac.set_ylim(-0.06, 1.06)
            frac.set_yticks([0, 0.5, 1])
            frac.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))

        label = top.text(
            0.95,
            0.91,
            rf"$z={z}$",
            transform=top.transAxes,
            ha="right",
            va="top",
            fontsize=15.2,
            zorder=6,
        )
        redshift_labels.append((top, label))
        for ax in (top, ratio, frac):
            setup(ax, shade=True)
        if bt_pl and not has_common_bins:
            frac.grid(False)
            frac.text(0.5, 0.62, "No common bins", transform=frac.transAxes, fontsize=10.4, ha="center", va="center")
        ratio.tick_params(axis="y", which="major", labelsize=13.4)
        for ax in (top, ratio):
            ax.tick_params(labelbottom=False)
        # Keep x-tick labels on both rows because panels have distinct upper mass limits.
        frac.tick_params(labelbottom=True)
        if row == 1:
            frac.set_xlabel(MASS_LABEL)
        if column == 0:
            top.set_ylabel(CONC_LABEL)
            denominator = r"I21,rel" if prescription == "I21R" else prescription
            ratio.set_ylabel(rf"$c_{{\rm sim}}/c_{{\rm {denominator}}}$", fontsize=12)
            bottom_label = r"$c_{\rm BT}/c_{\rm PL}$" if bt_pl else r"$f_{\rm relaxed}$"
            frac.set_ylabel(bottom_label, fontsize=12)
            for ax in (top, ratio, frac):
                ax.yaxis.set_label_coords(-0.18, 0.5)

    fig.canvas.draw()
    for ax, label in redshift_labels:
        grid_around_redshift(ax, label, fig.canvas.get_renderer())
    return fig


def export(
    fig: plt.Figure,
    output_dir: Path,
    stem: str,
    *,
    png_only: bool = False,
    qa_scripts: Path | None = None,
) -> Path:
    if qa_scripts and (qa_scripts / "audit_panel_alignment.py").exists():
        if str(qa_scripts) not in sys.path:
            sys.path.insert(0, str(qa_scripts))
        from audit_panel_alignment import require_matplotlib_panel_alignment

        require_matplotlib_panel_alignment(fig, strict=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    fig.savefig(png_path, dpi=320, bbox_inches=None)
    if not png_only:
        fig.savefig(output_dir / f"{stem}.pdf", bbox_inches=None)
        fig.savefig(output_dir / f"{stem}.svg", bbox_inches=None)
    plt.close(fig)
    print(f"Saved: {png_path}", flush=True)
    return png_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=ARTICLE_ROOT)
    parser.add_argument("--theory", nargs="+", choices=("L16", "D19", "I21R"), default=["D19", "I21R", "L16"])
    parser.add_argument("--png-only", action="store_true", help="Write only manuscript PNG files.")
    parser.add_argument("--no-log-ratio", action="store_true", help="Use linear ratio panels instead of log scale.")
    parser.add_argument("--no-bt-pl", action="store_true", help="Plot relaxed fraction instead of BT/PL bottom panel.")
    parser.add_argument("--redshift-gap", type=float, default=0.21)
    parser.add_argument("--qa-scripts", type=Path, default=None, help="Optional alignment QA script directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    style.apply_journal_style(base_fontsize=11.1)
    plt.rcParams.update({"font.family": "serif", "savefig.bbox": None, "pdf.fonttype": 42, "svg.fonttype": "none"})
    colors = tuple(style.MODEL_COLORS[key] for key in ("PL", "BT1", "BT10"))

    base_rows = read_rows(data_dir, "prescription_comparison_by_mass_bin.csv")
    i21_selection = None
    i21_curves = None

    for prescription in args.theory:
        if prescription == "I21R":
            if i21_selection is None:
                i21_selection = read_rows(data_dir, "i21_selection_96_bins.csv")
                i21_curves = read_rows(data_dir, "i21_relaxed_curves.csv")
            rows = i21_plot_rows(base_rows, i21_selection)
            curves = i21_curves
            slug = "i21-relaxed-fit"
        else:
            rows = base_rows
            curves = None
            slug = prescription.lower()

        fig = overview(
            rows,
            colors,
            prescription,
            curves,
            log_ratio=not args.no_log_ratio,
            bt_pl=not args.no_bt_pl,
            redshift_gap=args.redshift_gap,
        )
        export(
            fig,
            output_dir,
            f"concentration-qc-{slug}-relaxation",
            png_only=args.png_only,
            qa_scripts=args.qa_scripts,
        )


if __name__ == "__main__":
    main()
