#!/usr/bin/env python3
from __future__ import annotations

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


WORKSPACE = Path("/project/tkcastrosim/HNHuang")
PROJECT = WORKSPACE / "project_big_sim"
PAPERPLOT = PROJECT / "analysis/_used_by_article_nonlinear_evolution_pps/paperplot"
HM_DIR = PAPERPLOT / "halfmass_redshift"
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))
TOOLS_DIR = WORKSPACE / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
if str(HM_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(HM_DIR / "scripts"))

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes, save_publication_figure  # noqa: E402
from compute_hbt_official_main_track_halfmass import (  # noqa: E402
    MASS_EDGES_CODE,
    MASS_UNIT_MSUN,
    MIN_HALOS,
    MODEL_DIR,
    SNAPS,
    bk09_original,
    coco_hellwing16,
    correct_mass,
    estimate_particle_mass,
    load_redshift,
    zhalf_raw_adjacent,
)


DATA_DIR = HM_DIR / "data/fof_gap_stitching"
FIG_DIR = HM_DIR / "figures"

GAP_LIMITS: list[int | None] = [0, 1, 2, 3, 5, None]
OUT_BYBIN = DATA_DIR / "PL_fof_gap_stitching_bybin.csv"
OUT_SUMMARY = DATA_DIR / "PL_fof_gap_stitching_summary.csv"
OUT_PER_HALO = DATA_DIR / "PL_fof_gap_stitching_per_halo.csv"
OUT_NOTES = DATA_DIR / "fof_gap_stitching_notes.md"
OUT_FIG = FIG_DIR / "halfmass-redshift-fof-gap-stitching.png"


def method_name(gap_limit: int | None) -> str:
    return "all_gaps" if gap_limit is None else f"gap_{gap_limit}"


def method_label(gap_limit: int | None) -> str:
    return "all gaps" if gap_limit is None else f"gap <= {gap_limit}"


def read_catalog(snap: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with h5py.File(MODEL_DIR / f"halo_properties_{snap}.hdf5", "r") as handle:
        track = handle["InputHalos/HBTplus/TrackId"][...].astype(np.uint64)
        mass = handle["InputHalos/FOF/Masses"][...].astype(np.float64)
        size = handle["InputHalos/FOF/Sizes"][...].astype(np.float64)
        is_central = handle["InputHalos/IsCentral"][...].astype(np.int16)
    return track, mass, size, is_central


def matched_rows(keys: np.ndarray, track: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(keys)
    sorted_keys = keys[order]
    pos = np.searchsorted(sorted_keys, track)
    in_range = pos < len(sorted_keys)
    hit = np.zeros(len(track), dtype=bool)
    hit[in_range] = sorted_keys[pos[in_range]] == track[in_range]
    rows = np.nonzero(hit)[0]
    labels = order[pos[hit]]
    return rows.astype(np.int64), labels.astype(np.int64)


def build_base_histories() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, float]:
    track56, mass56_raw, size56, _ = read_catalog("0056")
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
    n = len(selected_track)
    mass_history = np.full((n, len(SNAPS)), np.nan, dtype=np.float32)
    valid_fof = np.zeros((n, len(SNAPS)), dtype=bool)
    satellite_or_fof0 = np.zeros((n, len(SNAPS)), dtype=bool)
    seen_track = np.zeros((n, len(SNAPS)), dtype=bool)

    print("PL selected", n, "particle_mass_code", f"{particle_mass:.6e}", flush=True)
    for col, snap in enumerate(SNAPS):
        track, mass_raw, size, is_central = read_catalog(snap)
        mass = correct_mass(mass_raw, particle_mass)
        rows, labels = matched_rows(selected_track, track)
        if len(rows):
            seen_track[labels, col] = True
            good = (
                np.isfinite(mass[rows])
                & (mass[rows] > 0.0)
                & np.isfinite(size[rows])
                & (size[rows] > 0.0)
                & (is_central[rows] == 1)
            )
            valid_fof[labels[good], col] = True
            mass_history[labels[good], col] = mass[rows[good]].astype(np.float32)
            satellite_or_fof0[labels[~good], col] = True
        print(
            snap,
            "valid_fof",
            int(valid_fof[:, col].sum()),
            "track_seen",
            int(seen_track[:, col].sum()),
            "sat_or_fof0",
            int(satellite_or_fof0[:, col].sum()),
            flush=True,
        )

    mass_bin = np.searchsorted(MASS_EDGES_CODE, selected_mass, side="right").astype(np.int16)
    per_base = pd.DataFrame(
        {
            "TrackId_z0": selected_track.astype(np.uint64),
            "M0": selected_mass,
            "M0_Msun": selected_mass * MASS_UNIT_MSUN,
            "N_FOF0": selected_size,
            "mass_bin": mass_bin,
            "particle_mass_code": particle_mass,
        }
    )
    return per_base, mass_history, valid_fof, particle_mass


def apply_gap_limit(mass_history: np.ndarray, valid_fof: np.ndarray, gap_limit: int | None) -> tuple[np.ndarray, np.ndarray]:
    n, ns = valid_fof.shape
    allowed = np.zeros_like(valid_fof)
    gap = np.zeros(n, dtype=np.int16)
    active = np.ones(n, dtype=bool)
    allowed[:, -1] = valid_fof[:, -1]

    for col in range(ns - 2, -1, -1):
        valid = valid_fof[:, col]
        if gap_limit is None:
            active = active | valid
            allowed[:, col] = valid
            continue

        allowed[:, col] = active & valid
        active_next = active.copy()
        gap[active & valid] = 0
        missing = active & ~valid
        gap[missing] += 1
        active_next[missing & (gap > gap_limit)] = False
        active = active_next

    stitched = np.full_like(mass_history, np.nan, dtype=np.float32)
    stitched[allowed] = mass_history[allowed]
    return stitched, allowed


def first_present_snap(present: np.ndarray) -> np.ndarray:
    out = np.full(present.shape[0], "", dtype=object)
    has = present.any(axis=1)
    out[has] = np.array(SNAPS, dtype=object)[np.argmax(present[has], axis=1)]
    return out


def make_bybin(per_halo: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method, sub_method in per_halo.groupby("method", sort=False):
        for bin_id, (left, right) in enumerate(zip(MASS_EDGES_CODE[:-1], MASS_EDGES_CODE[1:]), start=1):
            sub_total = sub_method[sub_method["mass_bin"] == bin_id]
            sub = sub_total[np.isfinite(sub_total["HalfMassRedshift"])]
            if len(sub) < MIN_HALOS:
                continue
            zvals = sub["HalfMassRedshift"].to_numpy(dtype=float)
            mvals = sub["M0_Msun"].to_numpy(dtype=float)
            m_mean = float(np.mean(mvals))
            rows.append(
                {
                    "model": "PL",
                    "method": method,
                    "label": sub_method["label"].iloc[0],
                    "mass_bin": bin_id,
                    "left_msun": left * MASS_UNIT_MSUN,
                    "right_msun": right * MASS_UNIT_MSUN,
                    "M0_mean_msun": m_mean,
                    "M0_geomean_msun": float(10.0 ** np.mean(np.log10(mvals))),
                    "n_halos_total": int(len(sub_total)),
                    "n_halos": int(len(sub)),
                    "selected_fraction": float(len(sub) / len(sub_total)) if len(sub_total) else np.nan,
                    "zhalf": float(np.mean(zvals)),
                    "zhalf_median": float(np.median(zvals)),
                    "zhalf_q16": float(np.percentile(zvals, 16)),
                    "zhalf_q84": float(np.percentile(zvals, 84)),
                    "z_bk09_original": float(bk09_original(m_mean)),
                    "z_coco_hellwing16": float(coco_hellwing16(m_mean)),
                    "dz_bk09_original": float(np.mean(zvals) - bk09_original(m_mean)),
                    "dz_coco_hellwing16": float(np.mean(zvals) - coco_hellwing16(m_mean)),
                }
            )
    return pd.DataFrame(rows)


def summarize(bybin: pd.DataFrame, per_halo: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method, sub_per in per_halo.groupby("method", sort=False):
        finite = np.isfinite(sub_per["HalfMassRedshift"])
        rows.append(
            {
                "scope": "per_halo",
                "method": method,
                "label": sub_per["label"].iloc[0],
                "fit": "",
                "n_bins": np.nan,
                "n_halos": int(finite.sum()),
                "n_total": int(len(sub_per)),
                "selected_fraction": float(finite.mean()),
                "mean_dz": np.nan,
                "mae_dz": np.nan,
                "rms_dz": np.nan,
            }
        )
        sub = bybin[bybin["method"] == method]
        for fit, col in [("BK09 original", "dz_bk09_original"), ("COCO/Hellwing16", "dz_coco_hellwing16")]:
            dz = sub[col].to_numpy(dtype=float)
            rows.append(
                {
                    "scope": "bybin_mean",
                    "method": method,
                    "label": sub_per["label"].iloc[0],
                    "fit": fit,
                    "n_bins": int(len(sub)),
                    "n_halos": int(sub["n_halos"].sum()) if len(sub) else 0,
                    "n_total": int(sub["n_halos_total"].sum()) if len(sub) else 0,
                    "selected_fraction": float(sub["n_halos"].sum() / sub["n_halos_total"].sum()) if len(sub) else np.nan,
                    "mean_dz": float(np.mean(dz)) if len(dz) else np.nan,
                    "mae_dz": float(np.mean(np.abs(dz))) if len(dz) else np.nan,
                    "rms_dz": float(np.sqrt(np.mean(dz * dz))) if len(dz) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def plot(bybin: pd.DataFrame) -> None:
    apply_journal_style(base_fontsize=9.0)
    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(5.4, 5.2),
        sharex=True,
        gridspec_kw={"height_ratios": [2.1, 1.0], "hspace": 0.05},
    )
    mgrid = np.logspace(8, 12, 400)
    ax.plot(mgrid, bk09_original(mgrid), color=JOURNAL_COLORS["black"], lw=1.55, label="BK09 original")
    ax.plot(mgrid, coco_hellwing16(mgrid), color=JOURNAL_COLORS["green"], lw=1.35, ls="--", label="COCO/Hellwing16")
    rax.axhline(0.0, color="0.25", lw=0.9)

    colors = [
        JOURNAL_COLORS["orange"],
        JOURNAL_COLORS["yellow"],
        JOURNAL_COLORS["sky"],
        JOURNAL_COLORS["blue"],
        JOURNAL_COLORS["purple"],
        JOURNAL_COLORS["gray"],
    ]
    markers = ["s", "o", "^", "D", "v", "P"]
    for idx, method in enumerate(bybin["method"].drop_duplicates()):
        sub = bybin[bybin["method"] == method]
        label = sub["label"].iloc[0]
        color = colors[idx % len(colors)]
        marker = markers[idx % len(markers)]
        ax.plot(
            sub["M0_mean_msun"],
            sub["zhalf"],
            marker + "-",
            color=color,
            ms=3.2,
            lw=1.05,
            alpha=0.9,
            label=label,
        )
        rax.plot(
            sub["M0_mean_msun"],
            sub["dz_bk09_original"],
            marker + "-",
            color=color,
            ms=3.0,
            lw=1.0,
            alpha=0.9,
            label=label,
        )

    ax.set_xscale("log")
    ax.set_ylabel(r"$z_{1/2}$")
    ax.legend(frameon=False, fontsize=6.7, ncol=2)
    rax.set_ylabel(r"$\Delta z_{1/2}$")
    rax.set_xlabel(r"$M_{\rm FOF,0}\ [{\rm M_\odot}]$")
    rax.legend(frameon=False, fontsize=6.3, ncol=2)
    for axis in (ax, rax):
        axis.set_xlim(9.0e7, 1.2e12)
        format_axes(axis)
    save_publication_figure(fig, OUT_FIG)


def write_notes(summary: pd.DataFrame) -> None:
    lines = [
        "# FOF Gap Stitching Half-Mass Test",
        "",
        "Generated by `scripts/test_fof_gap_stitching_halfmass.py`.",
        "",
        "All versions use same-TrackId `InputHalos/FOF/Masses`; only the allowed length of consecutive non-FOF/satellite gaps differs.",
        "",
    ]
    for row in summary[(summary["scope"] == "bybin_mean") & (summary["fit"] == "BK09 original")].to_dict("records"):
        lines.append(
            f"- `{row['method']}` ({row['label']}): measurable `{int(row['n_halos'])}/{int(row['n_total'])}`, "
            f"BK09 MAE `{float(row['mae_dz']):.4f}`"
        )
    OUT_NOTES.write_text("\n".join(lines) + "\n")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    per_base, mass_history, valid_fof, _ = build_base_histories()
    redshift = load_redshift()

    per_rows = []
    for gap_limit in GAP_LIMITS:
        stitched, allowed = apply_gap_limit(mass_history, valid_fof, gap_limit)
        zhalf = zhalf_raw_adjacent(stitched.astype(np.float64), per_base["M0"].to_numpy(dtype=float), redshift)
        tmp = per_base.copy()
        tmp["method"] = method_name(gap_limit)
        tmp["label"] = method_label(gap_limit)
        tmp["HalfMassRedshift"] = zhalf
        tmp["n_present_snapshots"] = allowed.sum(axis=1).astype(np.int16)
        tmp["first_present_snap"] = first_present_snap(allowed)
        per_rows.append(tmp)
        print(method_name(gap_limit), int(np.isfinite(zhalf).sum()), flush=True)
    per_halo = pd.concat(per_rows, ignore_index=True)
    per_halo.to_csv(OUT_PER_HALO, index=False)
    bybin = make_bybin(per_halo)
    bybin.to_csv(OUT_BYBIN, index=False)
    summary = summarize(bybin, per_halo)
    summary.to_csv(OUT_SUMMARY, index=False)
    plot(bybin)
    write_notes(summary)
    del mass_history, valid_fof
    gc.collect()
    print(OUT_FIG)
    print(OUT_BYBIN)
    print(OUT_SUMMARY)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
