#!/usr/bin/env python3
"""Plot the appendix TrackId FOF Gamma diagnostic.

The statistic selects z=0 FOF halos and follows their Warren-corrected FOF
masses through HBT-HERONS TrackId. It is intentionally separate from the
current-M200c population mean dM200c/dt measurement in the main text.
"""

from __future__ import annotations

import argparse
import gc
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import h5py
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_PATH = Path(__file__).resolve()
ARTICLE_ROOT = next((p for p in SCRIPT_PATH.parents if (p / "main.tex").exists()), SCRIPT_PATH.parents[2])
PUBLIC_MASS_ACCRETION_DIR = ARTICLE_ROOT / "public_data" / "figure_data" / "mass_accretion"
PUBLIC_BYBIN_PATH = PUBLIC_MASS_ACCRETION_DIR / "fof_gamma_bybin.csv"
PROJECT_BIG_SIM_ENV = os.environ.get("PROJECT_BIG_SIM_ROOT")
_ROOT_CANDIDATES: list[Path] = []
if PROJECT_BIG_SIM_ENV:
    _ROOT_CANDIDATES.append(Path(PROJECT_BIG_SIM_ENV).expanduser())
for anchor in (SCRIPT_PATH.parent, *SCRIPT_PATH.parents, Path.cwd(), *Path.cwd().parents):
    _ROOT_CANDIDATES.extend((anchor, anchor / "project_big_sim", anchor.parent / "project_big_sim"))

PROJECT_BIG_SIM_ROOT = next(
    (
        path
        for path in _ROOT_CANDIDATES
        if path.name == "project_big_sim" and (path / "data/PL/PL_25_1024").exists()
    ),
    Path("/project/tkcastrosim/HNHuang/project_big_sim"),
)
DATA_ROOT = Path(os.environ.get("BT_MAR_DATA_ROOT", PROJECT_BIG_SIM_ROOT / "data")).expanduser().resolve()

STYLE_ROOT = next(
    (
        path
        for path in (
            SCRIPT_PATH.parent,
            *SCRIPT_PATH.parents,
            PROJECT_BIG_SIM_ROOT.parent / "tools",
            PROJECT_BIG_SIM_ROOT,
        )
        if (path / "cosmology_plot_style.py").exists()
    ),
    None,
)
if STYLE_ROOT is not None and str(STYLE_ROOT) not in sys.path:
    sys.path.insert(0, str(STYLE_ROOT))

try:
    from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes, save_publication_figure
except Exception:  # pragma: no cover - fallback only used outside the project workspace.
    JOURNAL_COLORS = {"black": "#222222", "blue": "#2f70b7", "green": "#3b8a4a"}

    def apply_journal_style(base_fontsize: float = 9.0) -> None:
        plt.rcParams.update({"font.size": base_fontsize})

    def format_axes(ax, grid: bool = True) -> None:
        if grid:
            ax.grid(alpha=0.22)

    def save_publication_figure(fig, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)


MASS_UNIT_MSUN = 1.0e10
MASS_EDGES_CODE = np.logspace(-2.0, 2.0, 21)
MASS_EDGES_MSUN = MASS_EDGES_CODE * MASS_UNIT_MSUN
MIN_HALOS = 20
DEFAULT_SNAP_START = 21
DEFAULT_SNAP_END = 56

MODEL_SPECS = {
    "PL": {
        "label": "PL",
        "color": JOURNAL_COLORS["black"],
        "dir": DATA_ROOT
        / "PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus",
    },
    "BT_soft": {
        "label": r"BT $k_p=1$",
        "color": JOURNAL_COLORS["blue"],
        "dir": DATA_ROOT
        / "bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus",
    },
    "BT_deep": {
        "label": r"BT $k_p=10$",
        "color": JOURNAL_COLORS["green"],
        "dir": DATA_ROOT
        / "bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus",
    },
}

METHOD_LABELS = {
    "raw_adjacent": "raw same-TrackId adjacent",
    "cumulative_envelope": "cumulative maximum envelope",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute Gamma=dlnM/dlna from same-TrackId Warren-corrected FOF histories "
            "for PL, BTKP1, and BTKP10."
        )
    )
    parser.add_argument(
        "--models",
        default=os.environ.get("BT_MAR_MODELS", "PL,BT_soft,BT_deep"),
        help="Comma-separated model keys. Default: PL,BT_soft,BT_deep.",
    )
    parser.add_argument(
        "--snap-start",
        type=int,
        default=int(os.environ.get("BT_MAR_SNAP_START", DEFAULT_SNAP_START)),
        help="First snapshot number to use. Default: 21.",
    )
    parser.add_argument(
        "--snap-end",
        type=int,
        default=int(os.environ.get("BT_MAR_SNAP_END", DEFAULT_SNAP_END)),
        help="Last snapshot number to use. Default: 56.",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("BT_MAR_OUTPUT_DIR", str(PUBLIC_MASS_ACCRETION_DIR)),
        help="Directory for CSV outputs. Default: public_data/figure_data/mass_accretion.",
    )
    parser.add_argument(
        "--figure-dir",
        default=os.environ.get("BT_MAR_FIGURE_DIR", str(ARTICLE_ROOT)),
        help="Directory for the PNG output. Default: article root.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute model caches even if cached per-model CSVs exist.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Only write CSVs. Useful for short chunk runs that will be combined later.",
    )
    parser.add_argument(
        "--combine-glob",
        default="",
        help="Glob of existing chunk mass_accretion_rate_bybin.csv files to combine instead of reading HDF5.",
    )
    return parser.parse_args()


def snap_label(snap: int) -> str:
    return f"{snap:04d}"


def catalog_path(model_dir: Path, snap: int) -> Path:
    return model_dir / f"halo_properties_{snap_label(snap)}.hdf5"


def read_catalog(model_dir: Path, snap: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = catalog_path(model_dir, snap)
    with h5py.File(path, "r") as handle:
        track = handle["InputHalos/HBTplus/TrackId"][...].astype(np.uint64, copy=False)
        mass = handle["InputHalos/FOF/Masses"][...].astype(np.float64, copy=False)
        size = handle["InputHalos/FOF/Sizes"][...].astype(np.float64, copy=False)
    return track, mass, size


def load_redshifts(model_dir: Path, snaps: list[int]) -> np.ndarray:
    redshift = []
    for snap in snaps:
        with h5py.File(catalog_path(model_dir, snap), "r") as handle:
            z = float(np.asarray(handle["Header"].attrs["Redshift"]).reshape(-1)[0])
        redshift.append(0.0 if abs(z) < 1.0e-12 else z)
    return np.asarray(redshift, dtype=np.float64)


def estimate_particle_mass(mass: np.ndarray, size: np.ndarray) -> float:
    ok = np.isfinite(mass) & np.isfinite(size) & (mass > 0.0) & (size > 0.0)
    if not np.any(ok):
        raise ValueError("Cannot estimate particle mass: no positive Mass/Size values.")
    return float(np.median(mass[ok] / size[ok]))


def correct_mass(mass: np.ndarray, particle_mass: float) -> np.ndarray:
    corrected = np.full(mass.shape, np.nan, dtype=np.float64)
    ok = np.isfinite(mass) & (mass > 0.0)
    corrected[ok] = mass[ok] - mass[ok] * (mass[ok] / particle_mass) ** (-0.6)
    return corrected


def matched_positions(sorted_keys: np.ndarray, order: np.ndarray, track: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pos = np.searchsorted(sorted_keys, track)
    in_range = pos < len(sorted_keys)
    hit = np.zeros(len(track), dtype=bool)
    hit[in_range] = sorted_keys[pos[in_range]] == track[in_range]
    rows = order[pos[hit]]
    catalog_rows = np.flatnonzero(hit)
    return catalog_rows.astype(np.int64, copy=False), rows.astype(np.int64, copy=False)


def cumulative_max_preserve_gaps(history: np.ndarray) -> np.ndarray:
    envelope = np.full(history.shape, np.nan, dtype=np.float32)
    running = np.full(history.shape[0], np.nan, dtype=np.float64)
    for col in range(history.shape[1]):
        values = history[:, col].astype(np.float64, copy=False)
        finite = np.isfinite(values) & (values > 0.0)
        if not np.any(finite):
            continue
        previous = running[finite]
        running[finite] = np.where(np.isfinite(previous), np.maximum(previous, values[finite]), values[finite])
        envelope[finite, col] = running[finite].astype(np.float32)
    return envelope


def summarize_history_gamma(
    *,
    model: str,
    label: str,
    method: str,
    history: np.ndarray,
    selected_mass_code: np.ndarray,
    bin_index: np.ndarray,
    redshift: np.ndarray,
    scale_factor: np.ndarray,
    particle_mass: float,
    snaps: list[int],
) -> pd.DataFrame:
    rows = []
    a_mid = np.sqrt(scale_factor[:-1] * scale_factor[1:])
    z_mid = 1.0 / a_mid - 1.0
    delta_ln_a = np.diff(np.log(scale_factor))
    for pair_col in range(history.shape[1] - 1):
        left = history[:, pair_col]
        right = history[:, pair_col + 1]
        finite_pair = np.isfinite(left) & np.isfinite(right) & (left > 0.0) & (right > 0.0)
        if not np.any(finite_pair):
            continue
        finite_idx = np.flatnonzero(finite_pair)
        left_vals = left[finite_idx].astype(np.float64, copy=False)
        right_vals = right[finite_idx].astype(np.float64, copy=False)
        with np.errstate(invalid="ignore", divide="ignore"):
            gamma_vals = (np.log(right_vals) - np.log(left_vals)) / delta_ln_a[pair_col]
        finite_gamma = np.isfinite(gamma_vals)
        if not np.any(finite_gamma):
            continue
        finite_idx = finite_idx[finite_gamma]
        gamma_vals = gamma_vals[finite_gamma]
        pair_bins = bin_index[finite_idx]
        pair_masses = selected_mass_code[finite_idx]
        for bin_id, (left_code, right_code) in enumerate(zip(MASS_EDGES_CODE[:-1], MASS_EDGES_CODE[1:]), start=1):
            use = pair_bins == (bin_id - 1)
            n_halos = int(np.count_nonzero(use))
            if n_halos < MIN_HALOS:
                continue
            vals = gamma_vals[use]
            mvals_msun = pair_masses[use] * MASS_UNIT_MSUN
            rows.append(
                {
                    "model": model,
                    "label": label,
                    "method": method,
                    "method_label": METHOD_LABELS[method],
                    "mass_bin": bin_id,
                    "mass_bin_left_msun": left_code * MASS_UNIT_MSUN,
                    "mass_bin_right_msun": right_code * MASS_UNIT_MSUN,
                    "M0_mean_msun": float(np.mean(mvals_msun)),
                    "M0_geomean_msun": float(10.0 ** np.mean(np.log10(mvals_msun))),
                    "snap_left": snaps[pair_col],
                    "snap_right": snaps[pair_col + 1],
                    "z_left": float(redshift[pair_col]),
                    "z_right": float(redshift[pair_col + 1]),
                    "z_mid": float(z_mid[pair_col]),
                    "a_mid": float(a_mid[pair_col]),
                    "n_halos": n_halos,
                    "Gamma_median": float(np.nanmedian(vals)),
                    "Gamma_q16": float(np.nanpercentile(vals, 16.0)),
                    "Gamma_q84": float(np.nanpercentile(vals, 84.0)),
                    "Gamma_mean": float(np.nanmean(vals)),
                    "negative_fraction": float(np.nanmean(vals < 0.0)),
                    "particle_mass_code": particle_mass,
                    "particle_mass_msun": particle_mass * MASS_UNIT_MSUN,
                }
            )
    return pd.DataFrame(rows)


def compute_model(model: str, info: dict[str, object], snaps: list[int], cache_dir: Path, force: bool) -> pd.DataFrame:
    cache_path = cache_dir / f"mass_accretion_rate_bybin_{model}.csv"
    if cache_path.exists() and not force:
        print(f"{model}: using cache {cache_path}", flush=True)
        return pd.read_csv(cache_path)

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
    n_final = int(selected_track.size)
    print(f"{model}: selected {n_final} z=0 FOF halos; particle_mass_code={particle_mass:.6e}", flush=True)

    order = np.argsort(selected_track)
    sorted_track = selected_track[order]
    history = np.full((n_final, len(snaps)), np.nan, dtype=np.float32)

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
        print(f"{model}: {snap_label(snap)} matched_positive={int(np.isfinite(history[:, col]).sum())}", flush=True)
        del track, mass_raw, size, mass, catalog_rows, rows
        gc.collect()

    bin_index = np.digitize(selected_mass, MASS_EDGES_CODE, right=False) - 1
    bin_index[(selected_mass == MASS_EDGES_CODE[-1])] = len(MASS_EDGES_CODE) - 2

    frames = []
    frames.append(
        summarize_history_gamma(
            model=model,
            label=str(info["label"]),
            method="raw_adjacent",
            history=history,
            selected_mass_code=selected_mass,
            bin_index=bin_index,
            redshift=redshift,
            scale_factor=scale_factor,
            particle_mass=particle_mass,
            snaps=snaps,
        )
    )

    envelope = cumulative_max_preserve_gaps(history)
    frames.append(
        summarize_history_gamma(
            model=model,
            label=str(info["label"]),
            method="cumulative_envelope",
            history=envelope,
            selected_mass_code=selected_mass,
            bin_index=bin_index,
            redshift=redshift,
            scale_factor=scale_factor,
            particle_mass=particle_mass,
            snaps=snaps,
        )
    )

    out = pd.concat(frames, ignore_index=True)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(cache_path, index=False)
    print(f"{model}: wrote cache {cache_path}", flush=True)
    del history, envelope
    gc.collect()
    return out


def representative_mass_bins() -> list[int]:
    centers = np.sqrt(MASS_EDGES_MSUN[:-1] * MASS_EDGES_MSUN[1:])
    targets = (8.0e8, 1.25e9, 1.25e10, 1.25e11)
    bins = []
    for target in targets:
        idx = int(np.argmin(np.abs(np.log10(centers) - np.log10(target)))) + 1
        if idx not in bins:
            bins.append(idx)
    return bins


def make_summary(bybin: pd.DataFrame) -> pd.DataFrame:
    rep_bins = representative_mass_bins()
    sub = bybin.loc[bybin["mass_bin"].isin(rep_bins)].copy()
    keys = [
        "method",
        "mass_bin",
        "mass_bin_left_msun",
        "mass_bin_right_msun",
        "snap_left",
        "snap_right",
        "z_mid",
        "a_mid",
    ]
    pieces = []
    for model in ("PL", "BT_soft", "BT_deep"):
        model_sub = sub.loc[sub["model"] == model, keys + ["M0_mean_msun", "n_halos", "Gamma_median", "Gamma_q16", "Gamma_q84"]]
        model_sub = model_sub.rename(
            columns={
                "M0_mean_msun": f"{model}_M0_mean_msun",
                "n_halos": f"{model}_n_halos",
                "Gamma_median": f"{model}_Gamma_median",
                "Gamma_q16": f"{model}_Gamma_q16",
                "Gamma_q84": f"{model}_Gamma_q84",
            }
        )
        pieces.append(model_sub)

    if not pieces:
        return pd.DataFrame()
    summary = pieces[0]
    for piece in pieces[1:]:
        summary = summary.merge(piece, on=keys, how="outer")
    summary["BT_soft_minus_PL_Gamma_median"] = summary["BT_soft_Gamma_median"] - summary["PL_Gamma_median"]
    summary["BT_deep_minus_PL_Gamma_median"] = summary["BT_deep_Gamma_median"] - summary["PL_Gamma_median"]
    summary["BT_soft_over_PL_Gamma_median"] = summary["BT_soft_Gamma_median"] / summary["PL_Gamma_median"]
    summary["BT_deep_over_PL_Gamma_median"] = summary["BT_deep_Gamma_median"] / summary["PL_Gamma_median"]
    return summary.sort_values(["method", "mass_bin", "snap_left", "snap_right"]).reset_index(drop=True)


def mass_bin_title(bin_id: int) -> str:
    left = MASS_EDGES_MSUN[bin_id - 1]
    right = MASS_EDGES_MSUN[bin_id]
    return rf"$10^{{{np.log10(left):.1f}}}$--$10^{{{np.log10(right):.1f}}}\,M_\odot$"


def set_row_ylim(axes: np.ndarray, data: pd.DataFrame) -> None:
    vals = data[["Gamma_q16", "Gamma_q84", "Gamma_median"]].to_numpy(dtype=float).ravel()
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return
    lo, hi = np.nanpercentile(vals, [2.0, 98.0])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return
    span = hi - lo
    lo -= 0.08 * span
    hi += 0.08 * span
    if lo > 0.0:
        lo = 0.0
    if hi < 0.0:
        hi = 0.0
    for ax in axes:
        ax.set_ylim(lo, hi)


def plot_bybin(bybin: pd.DataFrame, figure_path: Path) -> None:
    rep_bins = representative_mass_bins()
    method = "raw_adjacent"
    plot_data = bybin.loc[(bybin["method"] == method) & bybin["mass_bin"].isin(rep_bins)].copy()
    plot_data["z_plot"] = 1.0 / plot_data["a_mid"].to_numpy(dtype=float) - 1.0
    z_values = plot_data["z_plot"].to_numpy(dtype=float)
    z_values = z_values[np.isfinite(z_values)]
    z_left = float(np.nanmax(z_values) * 1.02) if z_values.size else 1.0
    z_right = 0.0
    apply_journal_style(base_fontsize=8.9)
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(5.9, 5.9),
        sharex=True,
        sharey=True,
        squeeze=False,
    )

    row_data = plot_data
    for panel_idx, bin_id in enumerate(rep_bins):
        row, col = divmod(panel_idx, 2)
        ax = axes[row, col]
        ax.axhline(0.0, color="0.60", linewidth=0.7, linestyle=":")
        panel = row_data.loc[row_data["mass_bin"] == bin_id]
        for model, info in MODEL_SPECS.items():
            sub = panel.loc[panel["model"] == model].sort_values("z_plot")
            if sub.empty:
                continue
            x = sub["z_plot"].to_numpy(dtype=float)
            y = sub["Gamma_median"].to_numpy(dtype=float)
            lo = sub["Gamma_q16"].to_numpy(dtype=float)
            hi = sub["Gamma_q84"].to_numpy(dtype=float)
            color = str(info["color"])
            ax.plot(x, y, color=color, linewidth=1.25, label=str(info["label"]))
            ax.fill_between(x, lo, hi, color=color, alpha=0.15, linewidth=0.0)
        ax.xaxis.set_label_position("bottom")
        ax.xaxis.tick_bottom()
        ax.tick_params(axis="x", top=True, labeltop=False, bottom=True, labelbottom=True, pad=2)
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
            ax.set_ylabel(r"$\Gamma=d\ln M/d\ln a$")
        if row == 1:
            ax.set_xlabel("Redshift z", labelpad=3)
        else:
            ax.tick_params(axis="x", labelbottom=False)
        ax.set_xlim(z_left, z_right)
        ax.set_box_aspect(1)
        format_axes(ax, grid=True)
    set_row_ylim(axes.ravel(), row_data)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        axes[0, 0].legend(
            handles,
            labels,
            loc="upper right",
            ncol=1,
            frameon=False,
            fontsize=7.2,
            handlelength=1.6,
            borderpad=0.1,
            labelspacing=0.25,
        )
    fig.subplots_adjust(top=0.985, bottom=0.085, left=0.13, right=0.99, hspace=0.08, wspace=0.08)
    save_publication_figure(fig, figure_path)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    figure_dir = Path(args.figure_dir).expanduser().resolve()
    cache_dir = output_dir / "fof_gamma_trackid_cache"
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    using_public_bybin = PUBLIC_BYBIN_PATH.exists() and not args.combine_glob and os.environ.get("BT_MAR_USE_CATALOG", "0") != "1"
    if using_public_bybin:
        bybin = pd.read_csv(PUBLIC_BYBIN_PATH)
    elif args.combine_glob:
        import glob

        paths = [Path(path) for path in sorted(glob.glob(args.combine_glob))]
        if not paths:
            raise FileNotFoundError(f"No files matched --combine-glob={args.combine_glob!r}")
        frames = [pd.read_csv(path) for path in paths]
        bybin = pd.concat(frames, ignore_index=True)
        dedupe_keys = [
            "model",
            "method",
            "mass_bin",
            "snap_left",
            "snap_right",
        ]
        bybin = (
            bybin.sort_values(dedupe_keys)
            .drop_duplicates(subset=dedupe_keys, keep="last")
            .reset_index(drop=True)
        )
    else:
        models = [item.strip() for item in args.models.split(",") if item.strip()]
        unknown = [model for model in models if model not in MODEL_SPECS]
        if unknown:
            raise ValueError(f"Unknown model keys: {unknown}. Known keys: {sorted(MODEL_SPECS)}")

        snaps = list(range(args.snap_start, args.snap_end + 1))
        if len(snaps) < 2:
            raise ValueError("Need at least two snapshots to compute Gamma.")

        frames = []
        for model in models:
            frames.append(compute_model(model, MODEL_SPECS[model], snaps, cache_dir, args.force))
        bybin = pd.concat(frames, ignore_index=True)

    bybin_path = output_dir / "fof_gamma_bybin.csv"
    summary_path = output_dir / "fof_gamma_summary.csv"
    figure_path = figure_dir / "mass-accretion-rate-fof-gamma.png"

    summary = make_summary(bybin)
    if not using_public_bybin or bybin_path.resolve() != PUBLIC_BYBIN_PATH.resolve():
        bybin.to_csv(bybin_path, index=False)
    if not using_public_bybin or summary_path.resolve() != (PUBLIC_MASS_ACCRETION_DIR / "fof_gamma_summary.csv").resolve():
        summary.to_csv(summary_path, index=False)
    if not args.no_plot:
        plot_bybin(bybin, figure_path)

    print(bybin_path)
    print(summary_path)
    if not args.no_plot:
        print(figure_path)
    if not summary.empty:
        for method in ["raw_adjacent", "cumulative_envelope"]:
            focus = summary.loc[summary["method"] == method]
            focus = focus.loc[np.isfinite(focus["BT_soft_minus_PL_Gamma_median"])]
            if focus.empty:
                continue
            idx = focus["BT_soft_minus_PL_Gamma_median"].abs().idxmax()
            row = focus.loc[idx]
            print(
                f"{method}: largest |BTKP1-PL| among representative bins = "
                f"{row['BT_soft_minus_PL_Gamma_median']:.3g} at mass_bin={int(row['mass_bin'])}, "
                f"z_mid={row['z_mid']:.3g}",
                flush=True,
            )


if __name__ == "__main__":
    main()
