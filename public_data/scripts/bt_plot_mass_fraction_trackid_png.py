#!/usr/bin/env python3
"""Same-TrackId FOF assembly history, M(z)/M0, for PL and BT models."""

from __future__ import annotations

import argparse
import gc
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bt_plot_mass_accretion_rate_trackid_png import (
    ARTICLE_ROOT,
    DEFAULT_SNAP_END,
    DEFAULT_SNAP_START,
    MASS_EDGES_CODE,
    MASS_EDGES_MSUN,
    MASS_UNIT_MSUN,
    MIN_HALOS,
    MODEL_SPECS,
    PUBLIC_MASS_ACCRETION_DIR,
    apply_journal_style,
    catalog_path,
    correct_mass,
    estimate_particle_mass,
    format_axes,
    load_redshifts,
    mass_bin_title,
    matched_positions,
    read_catalog,
    representative_mass_bins,
    save_publication_figure,
)


PUBLIC_FRACTION_PATH = PUBLIC_MASS_ACCRETION_DIR / "mass_fraction_trackid_bybin.csv"
OUTPUT_PATH = ARTICLE_ROOT / "mass-fraction-trackid.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot M(z)/M0 from same-TrackId Warren-corrected FOF histories."
    )
    parser.add_argument("--models", default="PL,BT_soft,BT_deep")
    parser.add_argument("--snap-start", type=int, default=DEFAULT_SNAP_START)
    parser.add_argument("--snap-end", type=int, default=DEFAULT_SNAP_END)
    parser.add_argument("--output-csv", default=str(PUBLIC_FRACTION_PATH))
    parser.add_argument("--output-figure", default=str(OUTPUT_PATH))
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def summarize_fraction(
    *,
    model: str,
    label: str,
    history: np.ndarray,
    selected_mass_code: np.ndarray,
    bin_index: np.ndarray,
    redshift: np.ndarray,
    scale_factor: np.ndarray,
    particle_mass: float,
    snaps: list[int],
) -> pd.DataFrame:
    rows = []
    for col, snap in enumerate(snaps):
        mass = history[:, col].astype(np.float64, copy=False)
        with np.errstate(invalid="ignore", divide="ignore"):
            fraction = mass / selected_mass_code
        finite = np.isfinite(fraction) & (fraction > 0.0) & np.isfinite(selected_mass_code) & (selected_mass_code > 0.0)
        if not np.any(finite):
            continue
        for bin_id, (left_code, right_code) in enumerate(zip(MASS_EDGES_CODE[:-1], MASS_EDGES_CODE[1:]), start=1):
            use = finite & (bin_index == (bin_id - 1))
            n_halos = int(np.count_nonzero(use))
            if n_halos < MIN_HALOS:
                continue
            vals = fraction[use]
            m0_vals_msun = selected_mass_code[use] * MASS_UNIT_MSUN
            rows.append(
                {
                    "model": model,
                    "label": label,
                    "mass_bin": bin_id,
                    "mass_bin_left_msun": left_code * MASS_UNIT_MSUN,
                    "mass_bin_right_msun": right_code * MASS_UNIT_MSUN,
                    "M0_mean_msun": float(np.mean(m0_vals_msun)),
                    "M0_geomean_msun": float(10.0 ** np.mean(np.log10(m0_vals_msun))),
                    "snapshot": snap,
                    "redshift": float(redshift[col]),
                    "scale_factor": float(scale_factor[col]),
                    "n_halos": n_halos,
                    "M_over_M0_median": float(np.nanmedian(vals)),
                    "M_over_M0_q16": float(np.nanpercentile(vals, 16.0)),
                    "M_over_M0_q84": float(np.nanpercentile(vals, 84.0)),
                    "M_over_M0_mean": float(np.nanmean(vals)),
                    "particle_mass_code": particle_mass,
                    "particle_mass_msun": particle_mass * MASS_UNIT_MSUN,
                }
            )
    return pd.DataFrame(rows)


def compute_model_fraction(model: str, info: dict[str, object], snaps: list[int]) -> pd.DataFrame:
    model_dir = Path(info["dir"])
    missing = [snap for snap in snaps if not catalog_path(model_dir, snap).exists()]
    if missing:
        raise FileNotFoundError(f"{model}: missing HBTplus catalogs for snapshots {missing[:5]} at {model_dir}")

    redshift = load_redshifts(model_dir, snaps)
    scale_factor = 1.0 / (1.0 + redshift)
    track56, mass56_raw, size56 = read_catalog(model_dir, DEFAULT_SNAP_END)
    particle_mass = estimate_particle_mass(mass56_raw, size56)
    mass56 = correct_mass(mass56_raw, particle_mass)
    final_ok = (
        np.isfinite(mass56)
        & np.isfinite(size56)
        & (size56 > 0.0)
        & (mass56 >= MASS_EDGES_CODE[0])
        & (mass56 <= MASS_EDGES_CODE[-1])
    )
    selected_track = track56[final_ok]
    selected_mass = mass56[final_ok]
    print(f"{model}: selected {selected_track.size} z=0 FOF halos", flush=True)

    order = np.argsort(selected_track)
    sorted_track = selected_track[order]
    history = np.full((selected_track.size, len(snaps)), np.nan, dtype=np.float32)

    for col, snap in enumerate(snaps):
        track, mass_raw, size = read_catalog(model_dir, snap)
        mass = correct_mass(mass_raw, particle_mass)
        catalog_rows, rows = matched_positions(sorted_track, order, track)
        if catalog_rows.size:
            good = (
                np.isfinite(mass[catalog_rows])
                & (mass[catalog_rows] > 0.0)
                & np.isfinite(size[catalog_rows])
                & (size[catalog_rows] > 0.0)
            )
            if np.any(good):
                history[rows[good], col] = mass[catalog_rows[good]].astype(np.float32)
        print(f"{model}: {snap:04d} matched_positive={int(np.isfinite(history[:, col]).sum())}", flush=True)
        del track, mass_raw, size, mass, catalog_rows, rows
        gc.collect()

    bin_index = np.digitize(selected_mass, MASS_EDGES_CODE, right=False) - 1
    bin_index[selected_mass == MASS_EDGES_CODE[-1]] = len(MASS_EDGES_CODE) - 2
    out = summarize_fraction(
        model=model,
        label=str(info["label"]),
        history=history,
        selected_mass_code=selected_mass,
        bin_index=bin_index,
        redshift=redshift,
        scale_factor=scale_factor,
        particle_mass=particle_mass,
        snaps=snaps,
    )
    del history
    gc.collect()
    return out


def collect_fraction(args: argparse.Namespace) -> pd.DataFrame:
    output_csv = Path(args.output_csv).expanduser().resolve()
    if output_csv.exists() and not args.force:
        return pd.read_csv(output_csv)
    models = [item.strip() for item in args.models.split(",") if item.strip()]
    unknown = [model for model in models if model not in MODEL_SPECS]
    if unknown:
        raise ValueError(f"Unknown model keys: {unknown}. Known keys: {sorted(MODEL_SPECS)}")
    snaps = list(range(args.snap_start, args.snap_end + 1))
    frames = [compute_model_fraction(model, MODEL_SPECS[model], snaps) for model in models]
    data = pd.concat(frames, ignore_index=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_csv, index=False)
    print(output_csv, flush=True)
    return data


def set_fraction_ylim(axes: np.ndarray, data: pd.DataFrame) -> None:
    vals = data[["M_over_M0_q16", "M_over_M0_q84", "M_over_M0_median"]].to_numpy(dtype=float).ravel()
    vals = vals[np.isfinite(vals)]
    ymax = max(1.05, float(np.nanpercentile(vals, 99.0)) * 1.05) if vals.size else 1.05
    ymax = min(ymax, 1.35)
    for ax in axes:
        ax.set_ylim(-0.03, ymax)


def plot_fraction(data: pd.DataFrame, output_path: Path) -> None:
    rep_bins = representative_mass_bins()
    plot_data = data.loc[data["mass_bin"].isin(rep_bins)]
    z_values = plot_data["redshift"].to_numpy(dtype=float)
    z_values = z_values[np.isfinite(z_values)]
    z_left = float(np.nanmax(z_values) * 1.02) if z_values.size else 1.0
    z_right = 0.0

    apply_journal_style(base_fontsize=8.9)
    fig, axes = plt.subplots(2, 2, figsize=(5.9, 5.9), sharex=True, sharey=True, squeeze=False)
    for panel_idx, bin_id in enumerate(rep_bins):
        row, col = divmod(panel_idx, 2)
        ax = axes[row, col]
        ax.axhline(1.0, color="0.45", linewidth=0.7, linestyle=":")
        panel = plot_data.loc[plot_data["mass_bin"] == bin_id]
        for model, info in MODEL_SPECS.items():
            sub = panel.loc[panel["model"] == model].sort_values("redshift")
            if sub.empty:
                continue
            x = sub["redshift"].to_numpy(dtype=float)
            y = sub["M_over_M0_median"].to_numpy(dtype=float)
            lo = sub["M_over_M0_q16"].to_numpy(dtype=float)
            hi = sub["M_over_M0_q84"].to_numpy(dtype=float)
            color = str(info["color"])
            ax.plot(x, y, color=color, linewidth=1.25, label=str(info["label"]))
            ax.fill_between(x, lo, hi, color=color, alpha=0.15, linewidth=0.0)
        ax.text(
            0.04,
            0.94,
            mass_bin_title(bin_id),
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=7.8,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.78, pad=0.8),
        )
        if col == 0:
            ax.set_ylabel(r"$M(z)/M_0$")
        if row == 1:
            ax.set_xlabel("Redshift z", labelpad=3)
        else:
            ax.tick_params(axis="x", labelbottom=False)
        ax.set_xlim(z_left, z_right)
        ax.set_box_aspect(1)
        format_axes(ax, grid=True)
    set_fraction_ylim(axes.ravel(), plot_data)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        axes[0, 0].legend(
            handles,
            labels,
            loc="lower left",
            ncol=1,
            frameon=False,
            fontsize=7.2,
            handlelength=1.6,
            borderpad=0.1,
            labelspacing=0.25,
        )
    fig.subplots_adjust(top=0.985, bottom=0.085, left=0.13, right=0.99, hspace=0.08, wspace=0.08)
    save_publication_figure(fig, output_path)
    print(output_path, flush=True)


def main() -> None:
    args = parse_args()
    data = collect_fraction(args)
    plot_fraction(data, Path(args.output_figure).expanduser().resolve())


if __name__ == "__main__":
    main()
