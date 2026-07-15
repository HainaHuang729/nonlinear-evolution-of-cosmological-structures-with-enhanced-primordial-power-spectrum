#!/usr/bin/env python3
"""Measure M200c accretion along the most-massive-progenitor branch."""

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


def match_most_massive_progenitor(
    previous: dict[str, np.ndarray | float],
    descendant_track_id: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return one resolved central progenitor for each descendant."""
    previous_mass = np.asarray(previous["m200c_msun"])
    previous_track_id = np.asarray(previous["track_id"])
    previous_descendant_id = np.asarray(previous["descendant_track_id"])
    valid_previous = (
        np.asarray(previous["is_central"])
        & np.isfinite(previous_mass)
        & (previous_mass > 0.0)
        & (np.asarray(previous["n_dm"]) >= MIN_PARTICLES)
        & (previous_descendant_id >= 0)
    )

    candidate_descendant_id = previous_descendant_id[valid_previous]
    candidate_mass = previous_mass[valid_previous]
    candidate_track_id = previous_track_id[valid_previous]
    if candidate_descendant_id.size == 0:
        return (
            np.full(descendant_track_id.size, np.nan, dtype=float),
            np.zeros(descendant_track_id.size, dtype=int),
            np.full(descendant_track_id.size, -1, dtype=previous_track_id.dtype),
        )

    # Sort each descendant group by decreasing progenitor mass. The first row
    # in each group is therefore its most massive resolved progenitor.
    order = np.lexsort((-candidate_mass, candidate_descendant_id))
    sorted_descendant_id = candidate_descendant_id[order]
    sorted_mass = candidate_mass[order]
    sorted_track_id = candidate_track_id[order]
    unique_descendant_id, first, counts = np.unique(
        sorted_descendant_id,
        return_index=True,
        return_counts=True,
    )
    most_massive_mass = sorted_mass[first]
    most_massive_track_id = sorted_track_id[first]

    positions = np.searchsorted(unique_descendant_id, descendant_track_id)
    in_range = positions < unique_descendant_id.size
    matched_mass = np.full(descendant_track_id.size, np.nan, dtype=float)
    matched_count = np.zeros(descendant_track_id.size, dtype=int)
    matched_track_id = np.full(
        descendant_track_id.size,
        -1,
        dtype=previous_track_id.dtype,
    )
    candidate_rows = np.flatnonzero(in_range)
    candidate_positions = positions[in_range]
    equal = unique_descendant_id[candidate_positions] == descendant_track_id[in_range]
    matched_rows = candidate_rows[equal]
    matched_positions = candidate_positions[equal]
    matched_mass[matched_rows] = most_massive_mass[matched_positions]
    matched_count[matched_rows] = counts[matched_positions]
    matched_track_id[matched_rows] = most_massive_track_id[matched_positions]
    return matched_mass, matched_count, matched_track_id


def summarize_pair(
    model: str,
    snap_progenitor: int,
    snap_descendant: int,
    previous: dict[str, np.ndarray | float],
    descendant: dict[str, np.ndarray | float],
) -> list[dict[str, float | int | str]]:
    z_progenitor = float(previous["redshift"])
    z_descendant = float(descendant["redshift"])
    dt_yr = cosmic_age_flat_lcdm_yr(z_descendant) - cosmic_age_flat_lcdm_yr(z_progenitor)
    if not np.isfinite(dt_yr) or dt_yr <= 0.0:
        return []

    mass_descendant = np.asarray(descendant["m200c_msun"])
    track_id_descendant = np.asarray(descendant["track_id"])
    valid_descendant = (
        np.asarray(descendant["is_central"])
        & np.isfinite(mass_descendant)
        & (mass_descendant > 0.0)
        & (np.asarray(descendant["n_dm"]) >= MIN_PARTICLES)
        & (track_id_descendant >= 0)
    )
    if not np.any(valid_descendant):
        return []

    mass_progenitor, progenitor_count, progenitor_track_id = match_most_massive_progenitor(
        previous,
        track_id_descendant[valid_descendant],
    )
    mass_now = mass_descendant[valid_descendant]
    descendant_track_id = track_id_descendant[valid_descendant]
    matched = np.isfinite(mass_progenitor) & (mass_progenitor > 0.0)
    mass_now = mass_now[matched]
    mass_progenitor = mass_progenitor[matched]
    progenitor_count = progenitor_count[matched]
    progenitor_track_id = progenitor_track_id[matched]
    descendant_track_id = descendant_track_id[matched]
    dmdt = (mass_now - mass_progenitor) / dt_yr

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
        progenitor_masses = mass_progenitor[selected]
        selected_progenitor_count = progenitor_count[selected]
        selected_same_track = progenitor_track_id[selected] == descendant_track_id[selected]
        mean_mass = float(np.mean(masses))
        standard_deviation = float(np.std(values, ddof=1)) if n_halos > 1 else np.nan
        rows.append(
            {
                "model": model,
                "model_label": MODEL_SPECS[model]["label"],
                "snap_progenitor": snap_progenitor,
                "snap_descendant": snap_descendant,
                "z_progenitor": z_progenitor,
                "z_descendant": z_descendant,
                "dt_yr": dt_yr,
                "mass_bin_left_msun": left,
                "mass_bin_right_msun": right,
                "mass_bin_center_msun": float(np.sqrt(left * right)),
                "n_halos": n_halos,
                "mean_mass_descendant_msun": mean_mass,
                "median_mass_descendant_msun": float(np.median(masses)),
                "mean_mass_main_progenitor_msun": float(np.mean(progenitor_masses)),
                "mean_dM200c_dt_msun_yr": float(np.mean(values)),
                "median_dM200c_dt_msun_yr": float(np.median(values)),
                "std_dM200c_dt_msun_yr": standard_deviation,
                "sem_dM200c_dt_msun_yr": standard_deviation / np.sqrt(n_halos),
                "p16_dM200c_dt_msun_yr": float(np.percentile(values, 16.0)),
                "p84_dM200c_dt_msun_yr": float(np.percentile(values, 84.0)),
                "negative_fraction": float(np.mean(values < 0.0)),
                "multiple_progenitor_fraction": float(np.mean(selected_progenitor_count > 1)),
                "same_track_main_progenitor_fraction": float(np.mean(selected_same_track)),
                "correa2015_mean_dMdt_msun_yr": float(
                    correa2015_mean_dmdt(z_descendant, mean_mass)
                ),
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
    previous = read_catalog(paths[0])
    for previous_path, descendant_path in zip(paths[:-1], paths[1:]):
        descendant = read_catalog(descendant_path)
        snap_progenitor = snapshot_number(previous_path)
        snap_descendant = snapshot_number(descendant_path)
        pair_rows = summarize_pair(
            model,
            snap_progenitor,
            snap_descendant,
            previous,
            descendant,
        )
        rows.extend(pair_rows)
        print(
            f"{model}: {snap_progenitor:04d}->{snap_descendant:04d}, "
            f"z={float(previous['redshift']):.3f}->{float(descendant['redshift']):.3f}, "
            f"rows={len(pair_rows)}",
            flush=True,
        )
        previous = descendant
        gc.collect()
    return pd.DataFrame(rows)


def make_summary(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["median_over_correa"] = (
        data["median_dM200c_dt_msun_yr"] / data["correa2015_mean_dMdt_msun_yr"]
    )
    return (
        data.groupby(
            ["model", "model_label", "mass_bin_left_msun", "mass_bin_right_msun"],
            observed=True,
        )
        .agg(
            mass_bin_center_msun=("mass_bin_center_msun", "median"),
            z_min=("z_descendant", "min"),
            z_max=("z_descendant", "max"),
            n_snapshot_pairs=("z_descendant", "size"),
            total_halo_pairs=("n_halos", "sum"),
            median_rate_over_correa=("median_over_correa", "median"),
            median_negative_fraction=("negative_fraction", "median"),
            median_multiple_progenitor_fraction=("multiple_progenitor_fraction", "median"),
            median_same_track_main_progenitor_fraction=(
                "same_track_main_progenitor_fraction",
                "median",
            ),
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
    data["median_over_correa"] = (
        data["median_dM200c_dt_msun_yr"] / data["correa2015_mean_dMdt_msun_yr"]
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data_path = args.output_dir / "m200c_main_branch_accretion.csv"
    summary_path = args.output_dir / "m200c_main_branch_accretion_summary.csv"
    data.to_csv(data_path, index=False)
    make_summary(data).to_csv(summary_path, index=False)
    print(f"Wrote {len(data)} rows to {data_path}", flush=True)
    print(f"Wrote summary to {summary_path}", flush=True)


if __name__ == "__main__":
    main()
