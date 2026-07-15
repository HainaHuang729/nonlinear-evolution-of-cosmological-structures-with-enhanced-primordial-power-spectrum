#!/usr/bin/env python3
"""Reduce SOAP catalogs to current-M200c population accretion statistics."""

from __future__ import annotations

import argparse
import gc
import os
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


SCRIPT_PATH = Path(__file__).resolve()
ARTICLE_ROOT = next((p for p in SCRIPT_PATH.parents if (p / "main.tex").exists()), SCRIPT_PATH.parents[2])
PROJECT_BIG_SIM_ROOT = Path(
    os.environ.get("PROJECT_BIG_SIM_ROOT", "/project/tkcastrosim/HNHuang/project_big_sim")
).expanduser()

MASS_UNIT_MSUN = 1.0e10
MASS_BINS_MSUN = np.array(
    [1.0e8, 3.16e8, 1.0e9, 3.16e9, 1.0e10, 3.16e10, 1.0e11, 3.16e11, 1.0e12]
)
MIN_PARTICLES = 100
MIN_HALOS = 50

OMEGA_M = 0.3153
OMEGA_LAMBDA = 1.0 - OMEGA_M
H0_KM_S_MPC = 67.36
MPC_KM = 3.0856775814913673e19
SECONDS_PER_YEAR = 365.25 * 24.0 * 3600.0
H0_PER_YEAR = H0_KM_S_MPC / MPC_KM * SECONDS_PER_YEAR
H_0P7 = H0_KM_S_MPC / 70.0

MODEL_SPECS = {
    "PL": {
        "label": "PL",
        "relative_dir": "PL/PL_25_1024",
    },
    "BT_soft": {
        "label": "BT kp=1",
        "relative_dir": "bluetilted/kp_1_ms_1.5_25_1024",
    },
    "BT_deep": {
        "label": "BT kp=10",
        "relative_dir": "bluetilted/kp_10_ms_1.5_25_1024",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", default="PL,BT_soft,BT_deep")
    parser.add_argument("--snap-start", type=int, default=0)
    parser.add_argument("--snap-end", type=int, default=56)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ARTICLE_ROOT / "public_data/figure_data/mass_accretion",
    )
    return parser.parse_args()


def cosmic_age_flat_lcdm_yr(z: float) -> float:
    a = 1.0 / (1.0 + z)
    prefactor = 2.0 / (3.0 * H0_PER_YEAR * np.sqrt(OMEGA_LAMBDA))
    argument = np.sqrt(OMEGA_LAMBDA / OMEGA_M) * a**1.5
    return float(prefactor * np.arcsinh(argument))


def e_z(z: np.ndarray | float) -> np.ndarray:
    z_array = np.asarray(z, dtype=float)
    return np.sqrt(OMEGA_M * (1.0 + z_array) ** 3 + OMEGA_LAMBDA)


def correa2015_mean_dmdt(z: np.ndarray | float, mass_msun: np.ndarray | float) -> np.ndarray:
    """Correa et al. (2015b), Eq. (23), in solar masses per year."""
    z_array = np.asarray(z, dtype=float)
    mass_array = np.asarray(mass_msun, dtype=float)
    redshift_factor = -0.24 + 0.75 * (1.0 + z_array)
    return 71.6 * (mass_array / 1.0e12) * H_0P7 * redshift_factor * e_z(z_array)


def snapshot_number(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[-1])


def catalog_directory(model: str) -> Path:
    return (
        PROJECT_BIG_SIM_ROOT
        / "data"
        / MODEL_SPECS[model]["relative_dir"]
        / "SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus"
    )


def read_catalog(path: Path) -> dict[str, np.ndarray | float]:
    with h5py.File(path, "r") as handle:
        redshift = float(np.asarray(handle["Header"].attrs["Redshift"]).reshape(-1)[0])
        return {
            "redshift": redshift,
            "track_id": handle["InputHalos/HBTplus/TrackId"][...],
            "descendant_track_id": handle["InputHalos/HBTplus/DescendantTrackId"][...],
            "is_central": handle["InputHalos/IsCentral"][...].astype(bool, copy=False),
            "m200c_msun": handle["SO/200_crit/TotalMass"][...].astype(float, copy=False)
            * MASS_UNIT_MSUN,
            "n_dm": handle["SO/200_crit/NumberOfDarkMatterParticles"][...],
        }


def match_descendant_mass(
    descendant_track_id: np.ndarray,
    next_track_id: np.ndarray,
    next_mass_msun: np.ndarray,
) -> np.ndarray:
    order = np.argsort(next_track_id)
    sorted_track_id = next_track_id[order]
    positions = np.searchsorted(sorted_track_id, descendant_track_id)
    in_range = positions < sorted_track_id.size
    matched = np.full(descendant_track_id.size, np.nan, dtype=float)
    candidate_rows = np.flatnonzero(in_range)
    candidate_positions = positions[in_range]
    equal = sorted_track_id[candidate_positions] == descendant_track_id[in_range]
    matched[candidate_rows[equal]] = next_mass_msun[order[candidate_positions[equal]]]
    return matched


def summarize_pair(
    model: str,
    snap_current: int,
    snap_next: int,
    current: dict[str, np.ndarray | float],
    nxt: dict[str, np.ndarray | float],
) -> list[dict[str, float | int | str]]:
    z_current = float(current["redshift"])
    z_next = float(nxt["redshift"])
    dt_yr = cosmic_age_flat_lcdm_yr(z_next) - cosmic_age_flat_lcdm_yr(z_current)
    if not np.isfinite(dt_yr) or dt_yr <= 0.0:
        return []

    mass_current = np.asarray(current["m200c_msun"])
    descendant_id = np.asarray(current["descendant_track_id"])
    valid_current = (
        np.asarray(current["is_central"])
        & np.isfinite(mass_current)
        & (mass_current > 0.0)
        & (np.asarray(current["n_dm"]) >= MIN_PARTICLES)
        & (descendant_id >= 0)
    )
    if not np.any(valid_current):
        return []

    mass_next = match_descendant_mass(
        descendant_id[valid_current],
        np.asarray(nxt["track_id"]),
        np.asarray(nxt["m200c_msun"]),
    )
    mass_now = mass_current[valid_current]
    matched = np.isfinite(mass_next) & (mass_next > 0.0)
    mass_now = mass_now[matched]
    mass_next = mass_next[matched]
    dmdt = (mass_next - mass_now) / dt_yr
    z_mid = 0.5 * (z_current + z_next)

    rows: list[dict[str, float | int | str]] = []
    for left, right in zip(MASS_BINS_MSUN[:-1], MASS_BINS_MSUN[1:]):
        selected = (
            (mass_now >= left)
            & (mass_now < right)
            & np.isfinite(dmdt)
        )
        n_halos = int(np.count_nonzero(selected))
        if n_halos < MIN_HALOS:
            continue
        values = dmdt[selected]
        masses = mass_now[selected]
        mean_mass = float(np.mean(masses))
        standard_deviation = float(np.std(values, ddof=1)) if n_halos > 1 else np.nan
        rows.append(
            {
                "model": model,
                "model_label": MODEL_SPECS[model]["label"],
                "snap_current": snap_current,
                "snap_next": snap_next,
                "z_current": z_current,
                "z_next": z_next,
                "z_mid": z_mid,
                "dt_yr": dt_yr,
                "mass_bin_left_msun": left,
                "mass_bin_right_msun": right,
                "mass_bin_center_msun": float(np.sqrt(left * right)),
                "n_halos": n_halos,
                "mean_mass_current_msun": mean_mass,
                "median_mass_current_msun": float(np.median(masses)),
                "mean_dM200c_dt_msun_yr": float(np.mean(values)),
                "median_dM200c_dt_msun_yr": float(np.median(values)),
                "std_dM200c_dt_msun_yr": standard_deviation,
                "sem_dM200c_dt_msun_yr": standard_deviation / np.sqrt(n_halos),
                "p16_dM200c_dt_msun_yr": float(np.percentile(values, 16.0)),
                "p84_dM200c_dt_msun_yr": float(np.percentile(values, 84.0)),
                "negative_fraction": float(np.mean(values < 0.0)),
                "correa2015_mean_dMdt_msun_yr": float(correa2015_mean_dmdt(z_mid, mean_mass)),
            }
        )
    return rows


def compute_model(model: str, snap_start: int, snap_end: int) -> pd.DataFrame:
    paths = [
        path
        for path in catalog_directory(model).glob("halo_properties_*.hdf5")
        if snap_start <= snapshot_number(path) <= snap_end
    ]
    paths.sort(key=snapshot_number)
    if len(paths) < 2:
        raise FileNotFoundError(f"{model}: fewer than two catalogs found in {catalog_directory(model)}")

    rows: list[dict[str, float | int | str]] = []
    current = read_catalog(paths[0])
    for current_path, next_path in zip(paths[:-1], paths[1:]):
        nxt = read_catalog(next_path)
        snap_current = snapshot_number(current_path)
        snap_next = snapshot_number(next_path)
        pair_rows = summarize_pair(model, snap_current, snap_next, current, nxt)
        rows.extend(pair_rows)
        print(
            f"{model}: {snap_current:04d}->{snap_next:04d}, "
            f"z={float(current['redshift']):.3f}->{float(nxt['redshift']):.3f}, rows={len(pair_rows)}",
            flush=True,
        )
        current = nxt
        gc.collect()
    return pd.DataFrame(rows)


def make_summary(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["mean_over_correa"] = (
        data["mean_dM200c_dt_msun_yr"] / data["correa2015_mean_dMdt_msun_yr"]
    )
    return (
        data.groupby(
            ["model", "model_label", "mass_bin_left_msun", "mass_bin_right_msun"],
            observed=True,
        )
        .agg(
            mass_bin_center_msun=("mass_bin_center_msun", "median"),
            z_min=("z_mid", "min"),
            z_max=("z_mid", "max"),
            n_snapshot_pairs=("z_mid", "size"),
            total_halo_pairs=("n_halos", "sum"),
            median_mean_over_correa=("mean_over_correa", "median"),
            median_negative_fraction=("negative_fraction", "median"),
        )
        .reset_index()
    )


def main() -> None:
    args = parse_args()
    models = [model.strip() for model in args.models.split(",") if model.strip()]
    unknown = sorted(set(models).difference(MODEL_SPECS))
    if unknown:
        raise ValueError(f"Unknown model keys: {unknown}")

    frames = [compute_model(model, args.snap_start, args.snap_end) for model in models]
    data = pd.concat(frames, ignore_index=True)
    data["mean_over_correa"] = (
        data["mean_dM200c_dt_msun_yr"] / data["correa2015_mean_dMdt_msun_yr"]
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data_path = args.output_dir / "m200c_population_accretion.csv"
    summary_path = args.output_dir / "m200c_population_accretion_summary.csv"
    data.to_csv(data_path, index=False)
    make_summary(data).to_csv(summary_path, index=False)
    print(f"Wrote {len(data)} rows to {data_path}", flush=True)
    print(f"Wrote summary to {summary_path}", flush=True)


if __name__ == "__main__":
    main()
