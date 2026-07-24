#!/usr/bin/env python3
from __future__ import annotations

import gc
import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import h5py
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = Path("/project/tkcastrosim/HNHuang")
PROJECT = WORKSPACE / "project_big_sim"
PAPERPLOT = PROJECT / "analysis/_used_by_article_nonlinear_evolution_pps/paperplot"
HM_DIR = PAPERPLOT / "halfmass_redshift"
PAPER_DIR = PROJECT / "papers/article_nonlinear_evolution_pps"
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))
TOOLS_DIR = WORKSPACE / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from cosmology_plot_style import (  # noqa: E402
    JOURNAL_COLORS,
    apply_journal_style,
    format_axes,
    save_publication_figure,
)


DATA_DIR = HM_DIR / "data/same_trackid_no_envelope"
FIG_DIR = HM_DIR / "figures"
PAPERPLOT_FIG_DIR = PAPERPLOT / "figures"
OUT_POINTS = DATA_DIR / "same_trackid_no_envelope_points.csv"
OUT_SUMMARY = DATA_DIR / "same_trackid_no_envelope_summary.csv"
OUT_FIG = FIG_DIR / "halfmass-redshift-trackid-no-envelope.png"
OUT_CANONICAL = PAPERPLOT_FIG_DIR / "halfmass-redshift-trackid-no-envelope.png"
OUT_PAPER = PAPER_DIR / "halfmass-redshift-trackid-no-envelope.png"
LOCAL_PUBLIC_POINTS = REPO_ROOT / "public_data/figure_data/halfmass_redshift/same_trackid_no_envelope_points.csv"
LOCAL_OUT_FIG = REPO_ROOT / "halfmass-redshift-trackid-no-envelope.png"
PORTABLE_OUTPUT_PATH = Path(os.environ.get("HALFMASS_OUTPUT_PATH", LOCAL_OUT_FIG))

SNAPS = [f"{i:04d}" for i in range(21, 57)]
MASS_EDGES_CODE = np.logspace(-2.0, 2.0, 21)
MASS_UNIT_MSUN = 1.0e10
MAIN_PARTICLE_MASS_MSUN = 1.89e6
N20_MASS_MSUN = 20.0 * MAIN_PARTICLE_MASS_MSUN
N100_MASS_MSUN = 100.0 * MAIN_PARTICLE_MASS_MSUN
MIN_HALOS = 20

MODELS = {
    "PL": {
        "label": "PL",
        "color": JOURNAL_COLORS["black"],
        "marker": "o",
        "dir": PROJECT / "data/PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus",
    },
    "BT_soft": {
        "label": r"BT $k_p=1$",
        "color": JOURNAL_COLORS["blue"],
        "marker": "^",
        "dir": PROJECT
        / "data/bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus",
    },
    "BT_deep": {
        "label": r"BT $k_p=10$",
        "color": JOURNAL_COLORS["green"],
        "marker": "s",
        "dir": PROJECT
        / "data/bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus",
    },
}


def literature_zhalf(m_msun: np.ndarray, *, a0: float, beta: float, h_fit: float) -> np.ndarray:
    return a0 * (np.asarray(m_msun, dtype=float) * h_fit / 1.0e10) ** beta - 1.0


def bk09_original(m_msun: np.ndarray) -> np.ndarray:
    return literature_zhalf(m_msun, a0=2.89, beta=-0.0563, h_fit=0.73)


def coco_hellwing16(m_msun: np.ndarray) -> np.ndarray:
    return literature_zhalf(m_msun, a0=2.77, beta=-0.0765, h_fit=0.704)


def read_catalog(model_dir: Path, snap: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with h5py.File(model_dir / f"halo_properties_{snap}.hdf5", "r") as handle:
        track = handle["InputHalos/HBTplus/TrackId"][...].astype(np.uint64)
        mass = handle["InputHalos/FOF/Masses"][...].astype(np.float64)
        size = handle["InputHalos/FOF/Sizes"][...].astype(np.float64)
    return track, mass, size


def load_redshift(model_dir: Path) -> np.ndarray:
    redshift = []
    for snap in SNAPS:
        with h5py.File(model_dir / f"halo_properties_{snap}.hdf5", "r") as handle:
            z = float(np.asarray(handle["Header"].attrs["Redshift"]).reshape(-1)[0])
        redshift.append(0.0 if abs(z) < 1.0e-12 else z)
    return np.array(redshift, dtype=np.float64)


def estimate_particle_mass(mass: np.ndarray, size: np.ndarray) -> float:
    ok = np.isfinite(mass) & np.isfinite(size) & (mass > 0.0) & (size > 0.0)
    return float(np.median(mass[ok] / size[ok]))


def correct_mass(mass: np.ndarray, particle_mass: float) -> np.ndarray:
    corrected = np.full_like(mass, np.nan, dtype=np.float64)
    ok = np.isfinite(mass) & (mass > 0.0)
    corrected[ok] = mass[ok] - mass[ok] * (mass[ok] / particle_mass) ** (-0.6)
    return corrected


def zhalf_raw_adjacent(history: np.ndarray, final_mass: np.ndarray, redshift: np.ndarray) -> np.ndarray:
    """Half-mass redshift from raw adjacent same-TrackId FOF detections.

    No gap filling and no cumulative envelope are applied. A halo is measurable
    only when two adjacent snapshots both have finite FOF masses and bracket
    M0/2 with an increasing mass step.
    """

    out = np.full(history.shape[0], np.nan, dtype=np.float64)
    threshold = final_mass / 2.0
    finite_threshold = np.isfinite(threshold) & (threshold > 0.0)
    left = history[:, :-1]
    right = history[:, 1:]
    adjacent = np.isfinite(left) & np.isfinite(right)
    crosses = (
        finite_threshold[:, None]
        & adjacent
        & (left <= threshold[:, None])
        & (threshold[:, None] <= right)
        & (right > left)
    )
    rows = np.nonzero(crosses.any(axis=1))[0]
    if len(rows) == 0:
        return out
    idx = np.argmax(crosses, axis=1)[rows]
    z0 = redshift[idx]
    z1 = redshift[idx + 1]
    m0 = left[rows, idx]
    m1 = right[rows, idx]
    out[rows] = z0 + (z1 - z0) * (threshold[rows] - m0) / (m1 - m0)
    return out


def model_points(model: str, info: dict) -> pd.DataFrame:
    cache = DATA_DIR / f"{model}_same_trackid_no_envelope_points.csv"
    if cache.exists():
        print(model, "using cache", cache, flush=True)
        return pd.read_csv(cache)

    model_dir = info["dir"]
    redshift = load_redshift(model_dir)
    track56, mass56_raw, size56 = read_catalog(model_dir, "0056")
    particle_mass = estimate_particle_mass(mass56_raw, size56)
    mass56 = correct_mass(mass56_raw, particle_mass)
    final_ok = (
        np.isfinite(mass56)
        & (mass56 >= MASS_EDGES_CODE[0])
        & (mass56 <= MASS_EDGES_CODE[-1])
        & np.isfinite(size56)
        & (size56 > 0.0)
    )
    selected_track = track56[final_ok]
    selected_mass = mass56[final_ok]
    selected_size = size56[final_ok]
    n_final = len(selected_track)
    print(model, "selected", n_final, "particle_mass", f"{particle_mass:.6e}", flush=True)

    order = np.argsort(selected_track)
    keys = selected_track[order]
    history = np.full((n_final, len(SNAPS)), np.nan, dtype=np.float32)
    present = np.zeros((n_final, len(SNAPS)), dtype=bool)

    for col, snap in enumerate(SNAPS):
        track, mass_raw, _ = read_catalog(model_dir, snap)
        mass = correct_mass(mass_raw, particle_mass)
        pos = np.searchsorted(keys, track)
        in_range = pos < len(keys)
        hit = np.zeros(len(track), dtype=bool)
        hit[in_range] = keys[pos[in_range]] == track[in_range]
        if np.any(hit):
            rows = order[pos[hit]]
            values = mass[hit]
            finite = np.isfinite(values)
            history[rows[finite], col] = values[finite].astype(np.float32)
            present[rows[finite], col] = True
        print(model, snap, int(present[:, col].sum()), flush=True)

    zhalf = zhalf_raw_adjacent(history.astype(np.float64), selected_mass, redshift)
    finite = np.isfinite(zhalf)
    bin_index = np.digitize(selected_mass, MASS_EDGES_CODE) - 1

    rows = []
    for bin_id, (left, right) in enumerate(zip(MASS_EDGES_CODE[:-1], MASS_EDGES_CODE[1:]), start=1):
        in_bin = bin_index == bin_id - 1
        use = finite & in_bin
        if np.count_nonzero(use) < MIN_HALOS:
            continue
        zvals = zhalf[use]
        mvals = selected_mass[use] * MASS_UNIT_MSUN
        rows.append(
            {
                "model": model,
                "label": info["label"],
                "method": "sameTrackId_rawAdjacent_noGap_noEnvelope_warrenFOF",
                "mass_bin": bin_id,
                "left_msun": left * MASS_UNIT_MSUN,
                "right_msun": right * MASS_UNIT_MSUN,
                "M0_mean_msun": float(np.mean(mvals)),
                "M0_geomean_msun": float(10.0 ** np.mean(np.log10(mvals))),
                "n_halos_total": int(np.count_nonzero(in_bin)),
                "n_halos": int(np.count_nonzero(use)),
                "selected_fraction": float(np.count_nonzero(use) / np.count_nonzero(in_bin)),
                "zhalf": float(np.mean(zvals)),
                "zhalf_median": float(np.median(zvals)),
                "zhalf_q16": float(np.nanpercentile(zvals, 16)),
                "zhalf_q84": float(np.nanpercentile(zvals, 84)),
                "size0_median": float(np.median(selected_size[use])),
                "particle_mass_code": particle_mass,
            }
        )

    points = pd.DataFrame(rows)
    points["z_bk09_original"] = bk09_original(points["M0_mean_msun"].to_numpy())
    points["z_coco_hellwing16"] = coco_hellwing16(points["M0_mean_msun"].to_numpy())
    points["dz_bk09_original"] = points["zhalf"] - points["z_bk09_original"]
    points["dz_coco_hellwing16"] = points["zhalf"] - points["z_coco_hellwing16"]
    points.to_csv(cache, index=False)
    del history, present
    gc.collect()
    print(model, "wrote cache", cache, flush=True)
    return points


def summarize(points: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, sub_model in points.groupby("model", sort=False):
        low = sub_model[sub_model["M0_mean_msun"] < 1.0e9]
        for fit, col in [
            ("BK09 original", "dz_bk09_original"),
            ("COCO/Hellwing16", "dz_coco_hellwing16"),
        ]:
            rows.append(
                {
                    "model": model,
                    "dataset": "sameTrackId_rawAdjacent_noGap_noEnvelope_warrenFOF",
                    "fit": fit,
                    "n_bins": int(len(sub_model)),
                    "n_halos": int(sub_model["n_halos"].sum()),
                    "n_halos_total": int(sub_model["n_halos_total"].sum()),
                    "selected_fraction": float(sub_model["n_halos"].sum() / sub_model["n_halos_total"].sum()),
                    "mean_dz": float(sub_model[col].mean()),
                    "mae_dz": float(sub_model[col].abs().mean()),
                    "rms_dz": float(np.sqrt(np.mean(sub_model[col] ** 2))),
                    "low_mass_n_bins_M_lt_1e9": int(len(low)),
                    "low_mass_mean_dz_M_lt_1e9": float(low[col].mean()) if len(low) else np.nan,
                    "low_mass_mae_dz_M_lt_1e9": float(low[col].abs().mean()) if len(low) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def plot(points: pd.DataFrame, output_path: Path = OUT_FIG) -> None:
    apply_journal_style(base_fontsize=9.2)
    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(5.05, 4.85),
        sharex=True,
        gridspec_kw={"height_ratios": [2.1, 1.0], "hspace": 0.05},
    )
    mgrid = np.logspace(8, 12, 300)
    for axis in (ax, rax):
        axis.axvspan(N20_MASS_MSUN, N100_MASS_MSUN, color="0.82", alpha=0.24, lw=0, zorder=0)
        axis.axvline(N100_MASS_MSUN, color="0.45", linestyle="--", linewidth=0.85, alpha=0.9, zorder=1)
    ax.plot(mgrid, bk09_original(mgrid), color="0.38", linewidth=1.45, linestyle="-.", label=r"BK09")
    ax.plot(
        mgrid,
        coco_hellwing16(mgrid),
        color="0.58",
        linewidth=1.45,
        linestyle="--",
        label=r"COCO/H16",
    )
    rax.axhline(0.0, color="0.45", linewidth=0.9)

    for model, info in MODELS.items():
        sub = points[points["model"] == model].sort_values("M0_mean_msun")
        yerr = [sub["zhalf"] - sub["zhalf_q16"], sub["zhalf_q84"] - sub["zhalf"]]
        ax.errorbar(
            sub["M0_mean_msun"],
            sub["zhalf"],
            yerr=yerr,
            fmt=info["marker"] + "-",
            color=info["color"],
            ecolor=info["color"],
            alpha=0.95,
            capsize=2,
            elinewidth=0.65,
            markerfacecolor="white",
            markeredgewidth=0.8,
            linewidth=1.15,
            label=info["label"],
        )
        rax.plot(
            sub["M0_mean_msun"],
            sub["dz_bk09_original"],
            info["marker"] + "-",
            color=info["color"],
            markerfacecolor="white",
            markeredgewidth=0.8,
            linewidth=1.05,
            label=info["label"],
        )

    ax.set_xscale("log")
    ax.set_ylabel(r"$z_{1/2}$")
    rax.set_ylabel(r"$\Delta z_{1/2}$")
    rax.set_xlabel(r"$M_{\rm FOF}(z=0)\,[M_\odot]$")
    ax.legend(loc="upper right", fontsize=6.6, ncol=1)
    for axis in (ax, rax):
        axis.set_xlim(9.0e7, 1.2e12)
        format_axes(axis, grid=True)
    save_publication_figure(fig, output_path)


def main() -> None:
    if LOCAL_PUBLIC_POINTS.exists() and os.environ.get("HALFMASS_USE_CATALOG", "0") != "1":
        points = pd.read_csv(LOCAL_PUBLIC_POINTS)
        plot(points, PORTABLE_OUTPUT_PATH)
        print(PORTABLE_OUTPUT_PATH)
        return

    if not all(info["dir"].exists() for info in MODELS.values()):
        if not LOCAL_PUBLIC_POINTS.exists():
            raise FileNotFoundError(
                "Neither the original HDF5 catalogs nor the public half-mass CSV are available."
            )
        points = pd.read_csv(LOCAL_PUBLIC_POINTS)
        plot(points, LOCAL_OUT_FIG)
        print(LOCAL_OUT_FIG)
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PAPERPLOT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    all_points = []
    for model, info in MODELS.items():
        all_points.append(model_points(model, info))
        gc.collect()
    points = pd.concat(all_points, ignore_index=True)
    summary = summarize(points)
    points.to_csv(OUT_POINTS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    plot(points)
    shutil.copyfile(OUT_FIG, OUT_CANONICAL)
    shutil.copyfile(OUT_FIG, OUT_PAPER)
    print(OUT_FIG)
    print(OUT_CANONICAL)
    print(OUT_PAPER)
    print(OUT_POINTS)
    print(OUT_SUMMARY)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
