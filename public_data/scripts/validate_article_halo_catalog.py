#!/usr/bin/env python3
"""Validate the compact halo catalog against the published reduced tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import h5py
import numpy as np


MODEL_TO_PUBLIC = {
    "PL": "PL",
    "BT_kp1": "BT_soft",
    "BT_kp10": "BT_deep",
}
MAH_PUBLIC_FILES = {
    "PL": "pl_warren_median_mah.csv",
    "BT_kp1": "bt_soft_warren_median_mah.csv",
}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    article_root = next(parent for parent in script_path.parents if (parent / "main.tex").exists())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog_dir", type=Path)
    parser.add_argument("--article-root", type=Path, default=article_root)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_checksums(catalog_dir: Path) -> None:
    rows = read_csv(catalog_dir / "catalog_manifest.csv")
    for row in rows:
        path = catalog_dir / row["file"]
        assert path.stat().st_size == int(row["size_bytes"]), path
        assert sha256sum(path) == row["sha256"], path
    print(f"PASS checksums: {len(rows)} files")


def validate_fof_hmf(catalog_dir: Path, article_root: Path) -> None:
    public_rows = read_csv(article_root / "public_data/figure_data/fof_hmf/fof_reed07_hmf_points.csv")
    grouped: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in public_rows:
        grouped[(row["model"], int(row["snapshot"]))].append(row)

    log_edges = np.arange(8.0, 13.0 + 1.0 / 6.0, 1.0 / 6.0)
    checked = 0
    for model, public_model in MODEL_TO_PUBLIC.items():
        path = catalog_dir / f"fof_hmf_source_{model}.hdf5"
        with h5py.File(path, "r") as handle:
            for group_name in sorted(handle.keys()):
                group = handle[group_name]
                snapshot = int(group.attrs["snapshot"])
                mass = np.asarray(group["mass_fof_warren_msun"], dtype=np.float64)
                log_mass = np.log10(mass)
                counts = np.histogram(log_mass, bins=log_edges)[0].astype(np.float64)
                mass_sum = np.histogram(log_mass, bins=log_edges, weights=mass)[0]
                box_size = float(np.asarray(group.attrs["box_size_mpc"]).reshape(-1)[0])
                dlog = np.diff(log_edges)
                dndlog = counts / (box_size**3 * dlog)
                error = np.sqrt(counts) / (box_size**3 * dlog)
                centers = 0.5 * (log_edges[:-1] + log_edges[1:])
                nonzero = counts > 0
                centers[nonzero] = np.log10(mass_sum[nonzero] / counts[nonzero])

                expected = sorted(
                    grouped[(public_model, snapshot)],
                    key=lambda row: float(row["log10_M_FOF_Msun"]),
                )
                expected_center = np.asarray(
                    [float(row["log10_M_FOF_Msun"]) for row in expected]
                )
                expected_hmf = np.asarray([float(row["dn_dlog10M"]) for row in expected])
                expected_error = np.asarray([float(row["poisson_err"]) for row in expected])
                np.testing.assert_allclose(centers, expected_center, rtol=2e-9, atol=2e-9)
                np.testing.assert_allclose(dndlog, expected_hmf, rtol=2e-9, atol=0.0)
                np.testing.assert_allclose(error, expected_error, rtol=2e-9, atol=0.0)
                checked += len(expected)
    print(f"PASS FOF HMF: {checked} published points")


def validate_so_counts(catalog_dir: Path, article_root: Path) -> None:
    public_rows = read_csv(
        article_root / "public_data/figure_data/m200c_hmf/m200c_bocquet16_hmf_points.csv"
    )
    expected_counts: dict[tuple[str, int], int] = {}
    for row in public_rows:
        expected_counts[(row["model"], int(row["snapshot"]))] = int(row["n_kept"])

    checked = 0
    for model, public_model in MODEL_TO_PUBLIC.items():
        path = catalog_dir / f"m200c_concentration_source_{model}.hdf5"
        with h5py.File(path, "r") as handle:
            for group_name in sorted(handle.keys()):
                group = handle[group_name]
                snapshot = int(group.attrs["snapshot"])
                mass = np.asarray(group["mass_m200c_msun"])
                particle_count = np.asarray(group["particle_count_m200c"])
                assert mass.size == expected_counts[(public_model, snapshot)]
                assert np.all(np.isfinite(mass) & (mass > 0.0))
                assert np.all(particle_count >= 100)
                checked += mass.size
    print(f"PASS M200c selection: {checked} per-halo rows")


def warren_correct(raw_mass: np.ndarray, particle_mass: float) -> np.ndarray:
    corrected = np.full(raw_mass.shape, np.nan, dtype=np.float64)
    valid = np.isfinite(raw_mass) & (raw_mass > 0.0)
    corrected[valid] = raw_mass[valid] * (
        1.0 - (raw_mass[valid] / particle_mass) ** (-0.6)
    )
    return corrected


def validate_mah(catalog_dir: Path, article_root: Path) -> None:
    public_dir = article_root / "public_data/figure_data/mass_assembly_history"
    checked = 0
    for model, filename in MAH_PUBLIC_FILES.items():
        expected_rows = read_csv(public_dir / filename)
        expected: dict[tuple[int, int], dict[str, str]] = {}
        path = catalog_dir / f"mah_track_source_{model}.hdf5"
        with h5py.File(path, "r") as handle:
            redshift = np.asarray(handle["redshift"], dtype=np.float64)
            bin_index = np.asarray(handle["mass_bin_index"], dtype=np.uint8)
            target_mass = np.asarray(handle["target_mass_msun"], dtype=np.float64)
            raw_history = np.asarray(handle["mass_fof_raw_msun"], dtype=np.float64)
            particle_mass = float(handle.attrs["particle_mass_msun"])
            corrected = warren_correct(raw_history, particle_mass)

            for row in expected_rows:
                bin_match = int(np.argmin(np.abs(target_mass - float(row["target_M0_msun"]))))
                redshift_match = int(np.argmin(np.abs(redshift - float(row["z"]))))
                assert np.isclose(redshift[redshift_match], float(row["z"]), rtol=0.0, atol=2e-6)
                expected[(bin_match, redshift_match)] = row

            for (mass_bin, snapshot_column), row in expected.items():
                selected = bin_index == mass_bin
                values = corrected[selected, snapshot_column]
                positive = np.isfinite(values) & (values > 0.0)
                assert int(np.count_nonzero(selected)) == int(row["n_halos"])
                assert int(np.count_nonzero(positive)) == int(row["n_positive_mass"])
                median = float(np.median(values[positive]))
                np.testing.assert_allclose(
                    median,
                    float(row["median_M_msun"]),
                    rtol=3e-7,
                    atol=100.0,
                )
                checked += 1
    print(f"PASS MAH medians: {checked} mass-bin/snapshot combinations")


def validate_radial_selection(catalog_dir: Path, article_root: Path) -> None:
    public_rows = read_csv(
        article_root
        / "public_data/figure_data/halo_density_radial/radial_density_profiles_n100_power03.csv"
    )
    expected_count: dict[tuple[str, float], int] = {}
    for row in public_rows:
        expected_count[(row["model"], float(row["target_mass_msun"]))] = int(row["nhalo"])
    public_name = {"PL": "PL", "BT_kp1": "BT_soft", "BT_kp10": "BT_deep"}
    checked = 0
    with h5py.File(catalog_dir / "radial_profile_selection.hdf5", "r") as handle:
        for model in public_name:
            for group_name in sorted(handle[model].keys()):
                group = handle[model][group_name]
                target = float(group.attrs["target_mass_msun"])
                count = len(group["source_row"])
                matches = [
                    expected
                    for (name, mass), expected in expected_count.items()
                    if name == public_name[model] and np.isclose(mass, target, rtol=2e-8)
                ]
                assert len(matches) == 1
                assert count == matches[0]
                assert group["center_of_mass_mpc"].shape == (count, 3)
                checked += count
    print(f"PASS radial selections: {checked} selected halos")


def main() -> None:
    args = parse_args()
    catalog_dir = args.catalog_dir.resolve()
    article_root = args.article_root.resolve()
    validate_checksums(catalog_dir)
    validate_fof_hmf(catalog_dir, article_root)
    validate_so_counts(catalog_dir, article_root)
    validate_mah(catalog_dir, article_root)
    validate_radial_selection(catalog_dir, article_root)
    print("ALL VALIDATIONS PASSED")


if __name__ == "__main__":
    main()
