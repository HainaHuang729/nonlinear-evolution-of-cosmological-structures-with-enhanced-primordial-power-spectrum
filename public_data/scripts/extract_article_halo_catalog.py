#!/usr/bin/env python3
"""Extract compact per-halo inputs used by the article analyses."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

import h5py
import numpy as np


MASS_UNIT_MSUN = 1.0e10
HMF_SNAPSHOTS = (24, 27, 30, 32, 40, 56)
ASSEMBLY_SNAPSHOTS = tuple(range(21, 57))
ASSEMBLY_TARGET_MASSES_MSUN = np.asarray(
    [3.0e8, 1.0e9, 3.0e9, 1.0e10, 3.0e10, 1.0e11, 3.0e11],
    dtype=np.float64,
)
ASSEMBLY_HALF_WIDTH_DEX = 0.1
RADIAL_TARGET_MASSES_MSUN = np.asarray(
    [1.0e10, 10.0**10.5, 1.0e11, 10.0**11.5],
    dtype=np.float64,
)
RADIAL_MAX_HALOS_PER_BIN = 100
FOF_HMF_MIN_MSUN = 1.0e8
FOF_HMF_MAX_MSUN = 1.0e13
SO_MIN_DM_PARTICLES = 100
FOF_CHUNK_SIZE = 2_000_000
GZIP_LEVEL = 4

MODEL_SPECS = {
    "PL": {
        "label": "PL",
        "relative_dir": "PL/PL_25_1024",
        "kp_h_mpc": np.nan,
        "ms": np.nan,
    },
    "BT_kp1": {
        "label": "BT kp=1",
        "relative_dir": "bluetilted/kp_1_ms_1.5_25_1024",
        "kp_h_mpc": 1.0,
        "ms": 1.5,
    },
    "BT_kp10": {
        "label": "BT kp=10",
        "relative_dir": "bluetilted/kp_10_ms_1.5_25_1024",
        "kp_h_mpc": 10.0,
        "ms": 1.5,
    },
}


def parse_args() -> argparse.Namespace:
    project_root = Path(
        os.environ.get("PROJECT_BIG_SIM_ROOT", "/project/tkcastrosim/HNHuang/project_big_sim")
    )
    default_output = (
        project_root
        / "analysis/_used_by_article_nonlinear_evolution_pps"
        / "public_catalog_release_2026-07-23"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--output-dir", type=Path, default=default_output)
    parser.add_argument(
        "--components",
        default="fof_hmf,so,mah,radial",
        help="Comma-separated subset of fof_hmf,so,mah,radial",
    )
    return parser.parse_args()


def soap_path(project_root: Path, model: str, snapshot: int) -> Path:
    return (
        project_root
        / "data"
        / MODEL_SPECS[model]["relative_dir"]
        / "SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus"
        / f"halo_properties_{snapshot:04d}.hdf5"
    )


def fof_path(project_root: Path, model: str, snapshot: int) -> Path:
    return (
        project_root
        / "data"
        / MODEL_SPECS[model]["relative_dir"]
        / f"fof_output_{snapshot:04d}.hdf5"
    )


def root_attributes(handle: h5py.File, component: str, model: str | None = None) -> None:
    handle.attrs["schema_version"] = "1.0"
    handle.attrs["component"] = component
    handle.attrs["created_utc"] = datetime.now(timezone.utc).isoformat()
    handle.attrs["description"] = "Compact per-halo source catalog for article analyses"
    handle.attrs["mass_unit"] = "Msun"
    handle.attrs["length_unit"] = "Mpc"
    if model is not None:
        spec = MODEL_SPECS[model]
        handle.attrs["model"] = model
        handle.attrs["model_label"] = spec["label"]
        handle.attrs["kp_h_mpc"] = spec["kp_h_mpc"]
        handle.attrs["ms"] = spec["ms"]


def compressed_dataset(
    group: h5py.Group,
    name: str,
    data: np.ndarray,
    *,
    description: str,
    chunks: tuple[int, ...] | None = None,
) -> h5py.Dataset:
    array = np.asarray(data)
    kwargs: dict[str, object] = {}
    if array.size > 0:
        kwargs.update(compression="gzip", compression_opts=GZIP_LEVEL, shuffle=True)
        if chunks is not None:
            kwargs["chunks"] = chunks
    dataset = group.create_dataset(name, data=array, **kwargs)
    dataset.attrs["description"] = description
    return dataset


def warren_corrected_mass(raw_mass_msun: np.ndarray, particle_mass_msun: float) -> np.ndarray:
    raw = np.asarray(raw_mass_msun, dtype=np.float64)
    corrected = np.full(raw.shape, np.nan, dtype=np.float64)
    valid = np.isfinite(raw) & (raw > 0.0)
    corrected[valid] = raw[valid] * (
        1.0 - (raw[valid] / float(particle_mass_msun)) ** (-0.6)
    )
    return corrected


def write_atomic(path: Path, writer) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        with h5py.File(temporary, "w") as handle:
            writer(handle)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def extract_fof_hmf(project_root: Path, output_dir: Path, model: str) -> Path:
    output = output_dir / f"fof_hmf_source_{model}.hdf5"

    def writer(handle: h5py.File) -> None:
        root_attributes(handle, "fof_hmf_source", model)
        handle.attrs["selection"] = (
            "Warren-corrected mass between 1e8 and 1e13 Msun, inclusive"
        )
        handle.attrs["warren_correction"] = "M_corr=M_raw*[1-(M_raw/m_DM)^(-0.6)]"

        for snapshot in HMF_SNAPSHOTS:
            source = fof_path(project_root, model, snapshot)
            print(f"FOF {model} snapshot {snapshot:04d}: {source}", flush=True)
            mass_parts: list[np.ndarray] = []
            corrected_parts: list[np.ndarray] = []
            size_parts: list[np.ndarray] = []
            row_parts: list[np.ndarray] = []
            id_parts: list[np.ndarray] = []

            with h5py.File(source, "r") as source_handle:
                masses = source_handle["Groups/Masses"]
                sizes = source_handle["Groups/Sizes"]
                group_ids = source_handle["Groups/GroupIDs"]
                header = source_handle["Header"].attrs
                particle_mass_msun = float(np.asarray(header["InitialMassTable"])[1]) * MASS_UNIT_MSUN
                redshift = float(np.asarray(header["Redshift"]).reshape(-1)[0])
                box_size_mpc = np.asarray(header["BoxSize"], dtype=np.float64)

                for start in range(0, len(masses), FOF_CHUNK_SIZE):
                    stop = min(start + FOF_CHUNK_SIZE, len(masses))
                    raw = np.asarray(masses[start:stop], dtype=np.float64) * MASS_UNIT_MSUN
                    corrected = warren_corrected_mass(raw, particle_mass_msun)
                    selected = (
                        np.isfinite(corrected)
                        & (corrected >= FOF_HMF_MIN_MSUN)
                        & (corrected <= FOF_HMF_MAX_MSUN)
                    )
                    if not np.any(selected):
                        continue
                    local_rows = np.flatnonzero(selected)
                    mass_parts.append(raw[selected])
                    corrected_parts.append(corrected[selected])
                    size_parts.append(
                        np.asarray(sizes[start:stop], dtype=np.uint32)[selected]
                    )
                    row_parts.append((local_rows + start).astype(np.uint64, copy=False))
                    id_parts.append(
                        np.asarray(group_ids[start:stop], dtype=np.uint64)[selected]
                    )

            group = handle.create_group(f"snapshot_{snapshot:04d}")
            group.attrs["source_file"] = str(source)
            group.attrs["snapshot"] = snapshot
            group.attrs["redshift"] = 0.0 if abs(redshift) < 1.0e-12 else redshift
            group.attrs["box_size_mpc"] = box_size_mpc
            group.attrs["particle_mass_msun"] = particle_mass_msun

            raw_out = np.concatenate(mass_parts) if mass_parts else np.empty(0, dtype=np.float64)
            corrected_out = (
                np.concatenate(corrected_parts) if corrected_parts else np.empty(0, dtype=np.float64)
            )
            size_out = np.concatenate(size_parts) if size_parts else np.empty(0, dtype=np.uint32)
            row_out = np.concatenate(row_parts) if row_parts else np.empty(0, dtype=np.uint64)
            id_out = np.concatenate(id_parts) if id_parts else np.empty(0, dtype=np.uint64)
            compressed_dataset(group, "source_row", row_out, description="Zero-based row in source FOF group catalog")
            compressed_dataset(group, "group_id", id_out, description="SWIFT FOF GroupID")
            compressed_dataset(group, "mass_fof_raw_msun", raw_out, description="Raw FOF group mass")
            compressed_dataset(
                group,
                "mass_fof_warren_msun",
                corrected_out,
                description="FOF mass after the Warren et al. low-particle correction",
            )
            compressed_dataset(group, "particle_count", size_out, description="FOF group particle count")
            print(f"  selected {raw_out.size:,} groups", flush=True)

    write_atomic(output, writer)
    return output


def extract_so_catalog(project_root: Path, output_dir: Path, model: str) -> Path:
    output = output_dir / f"m200c_concentration_source_{model}.hdf5"

    def writer(handle: h5py.File) -> None:
        root_attributes(handle, "m200c_concentration_source", model)
        handle.attrs["selection"] = "finite positive M200c and N_DM>=100"
        for snapshot in HMF_SNAPSHOTS:
            source = soap_path(project_root, model, snapshot)
            print(f"SO {model} snapshot {snapshot:04d}: {source}", flush=True)
            with h5py.File(source, "r") as source_handle:
                mass = np.asarray(source_handle["SO/200_crit/TotalMass"], dtype=np.float64) * MASS_UNIT_MSUN
                concentration = np.asarray(source_handle["SO/200_crit/Concentration"], dtype=np.float32)
                particle_count = np.asarray(
                    source_handle["SO/200_crit/NumberOfDarkMatterParticles"], dtype=np.uint32
                )
                track_id = np.asarray(source_handle["InputHalos/HBTplus/TrackId"], dtype=np.uint64)
                is_central = np.asarray(source_handle["InputHalos/IsCentral"], dtype=np.uint8)
                redshift = float(np.asarray(source_handle["Header"].attrs["Redshift"]).reshape(-1)[0])
                box_size_mpc = np.asarray(source_handle["Header"].attrs["BoxSize"], dtype=np.float64)

            selected = np.isfinite(mass) & (mass > 0.0) & (particle_count >= SO_MIN_DM_PARTICLES)
            source_row = np.flatnonzero(selected).astype(np.uint32, copy=False)
            group = handle.create_group(f"snapshot_{snapshot:04d}")
            group.attrs["source_file"] = str(source)
            group.attrs["snapshot"] = snapshot
            group.attrs["redshift"] = 0.0 if abs(redshift) < 1.0e-12 else redshift
            group.attrs["box_size_mpc"] = box_size_mpc
            compressed_dataset(group, "source_row", source_row, description="Zero-based row in source SOAP catalog")
            compressed_dataset(group, "track_id", track_id[selected], description="HBT-HERONS persistent TrackId")
            compressed_dataset(group, "is_central", is_central[selected], description="SOAP InputHalos/IsCentral flag")
            compressed_dataset(group, "mass_m200c_msun", mass[selected], description="SOAP SO/200_crit TotalMass")
            compressed_dataset(
                group,
                "concentration_c200c",
                concentration[selected],
                description="SOAP SO/200_crit Concentration; invalid values are retained",
            )
            compressed_dataset(
                group,
                "particle_count_m200c",
                particle_count[selected],
                description="Dark matter particle count inside R200c",
            )
            print(f"  selected {source_row.size:,} halos", flush=True)

    write_atomic(output, writer)
    return output


def estimate_particle_mass_msun(raw_mass_msun: np.ndarray, particle_count: np.ndarray) -> float:
    valid = (
        np.isfinite(raw_mass_msun)
        & (raw_mass_msun > 0.0)
        & np.isfinite(particle_count)
        & (particle_count > 0)
    )
    return float(np.median(raw_mass_msun[valid] / particle_count[valid]))


def assembly_selection(project_root: Path, model: str) -> dict[str, np.ndarray | float | str]:
    source = soap_path(project_root, model, 56)
    with h5py.File(source, "r") as handle:
        track_id = np.asarray(handle["InputHalos/HBTplus/TrackId"], dtype=np.uint64)
        raw_mass_msun = np.asarray(handle["InputHalos/FOF/Masses"], dtype=np.float64) * MASS_UNIT_MSUN
        particle_count = np.asarray(handle["InputHalos/FOF/Sizes"], dtype=np.uint64)

    particle_mass_msun = estimate_particle_mass_msun(raw_mass_msun, particle_count)
    corrected = warren_corrected_mass(raw_mass_msun, particle_mass_msun)
    selected_rows: list[np.ndarray] = []
    selected_bins: list[np.ndarray] = []
    for bin_index, target in enumerate(ASSEMBLY_TARGET_MASSES_MSUN):
        selected = np.flatnonzero(
            np.isfinite(corrected)
            & (np.abs(np.log10(corrected / target)) <= ASSEMBLY_HALF_WIDTH_DEX)
        )
        selected_rows.append(selected)
        selected_bins.append(np.full(selected.size, bin_index, dtype=np.uint8))
    rows = np.concatenate(selected_rows).astype(np.uint32, copy=False)
    bins = np.concatenate(selected_bins)
    return {
        "source": str(source),
        "rows": rows,
        "bins": bins,
        "track_id": track_id[rows],
        "raw_mass_msun": raw_mass_msun[rows],
        "corrected_mass_msun": corrected[rows],
        "particle_count": particle_count[rows].astype(np.uint32, copy=False),
        "particle_mass_msun": particle_mass_msun,
    }


def extract_mah(project_root: Path, output_dir: Path, model: str) -> Path:
    output = output_dir / f"mah_track_source_{model}.hdf5"
    selection = assembly_selection(project_root, model)
    track_id = np.asarray(selection["track_id"], dtype=np.uint64)
    n_halos = track_id.size
    n_snapshots = len(ASSEMBLY_SNAPSHOTS)
    raw_history = np.full((n_halos, n_snapshots), np.nan, dtype=np.float32)
    count_history = np.zeros((n_halos, n_snapshots), dtype=np.uint32)
    redshift = np.full(n_snapshots, np.nan, dtype=np.float32)

    order = np.argsort(track_id)
    sorted_track_id = track_id[order]
    for column, snapshot in enumerate(ASSEMBLY_SNAPSHOTS):
        source = soap_path(project_root, model, snapshot)
        print(f"MAH {model} snapshot {snapshot:04d}: {source}", flush=True)
        with h5py.File(source, "r") as handle:
            source_track = np.asarray(handle["InputHalos/HBTplus/TrackId"], dtype=np.uint64)
            source_mass = np.asarray(handle["InputHalos/FOF/Masses"], dtype=np.float32)
            source_count = np.asarray(handle["InputHalos/FOF/Sizes"], dtype=np.uint64)
            redshift[column] = float(np.asarray(handle["Header"].attrs["Redshift"]).reshape(-1)[0])

        position = np.searchsorted(sorted_track_id, source_track)
        in_range = position < sorted_track_id.size
        source_rows = np.flatnonzero(in_range)
        matched_position = position[in_range]
        equal = sorted_track_id[matched_position] == source_track[in_range]
        source_rows = source_rows[equal]
        output_rows = order[matched_position[equal]]
        raw_history[output_rows, column] = source_mass[source_rows] * MASS_UNIT_MSUN
        count_history[output_rows, column] = np.minimum(
            source_count[source_rows], np.iinfo(np.uint32).max
        ).astype(np.uint32)
        print(f"  matched {output_rows.size:,}/{n_halos:,}", flush=True)

    def writer(handle: h5py.File) -> None:
        root_attributes(handle, "mah_track_source", model)
        handle.attrs["source_z0"] = str(selection["source"])
        handle.attrs["selection_half_width_dex"] = ASSEMBLY_HALF_WIDTH_DEX
        handle.attrs["particle_mass_msun"] = float(selection["particle_mass_msun"])
        handle.attrs["warren_correction"] = "M_corr=M_raw*[1-(M_raw/m_DM)^(-0.6)]"
        compressed_dataset(handle, "snapshot", np.asarray(ASSEMBLY_SNAPSHOTS, dtype=np.uint16), description="Snapshot number")
        compressed_dataset(handle, "redshift", redshift, description="Snapshot redshift")
        compressed_dataset(handle, "track_id", track_id, description="Selected z=0 HBT-HERONS TrackId")
        compressed_dataset(handle, "source_row_z0", selection["rows"], description="Zero-based row in z=0 SOAP catalog")
        compressed_dataset(handle, "mass_bin_index", selection["bins"], description="Index into target_mass_msun")
        compressed_dataset(
            handle,
            "target_mass_msun",
            ASSEMBLY_TARGET_MASSES_MSUN,
            description="Centers of the seven z=0 selection windows",
        )
        compressed_dataset(
            handle,
            "final_mass_fof_raw_msun",
            selection["raw_mass_msun"],
            description="Raw z=0 FOF mass",
        )
        compressed_dataset(
            handle,
            "final_mass_fof_warren_msun",
            selection["corrected_mass_msun"],
            description="Warren-corrected z=0 FOF mass used for selection",
        )
        matrix_chunks = (min(max(n_halos, 1), 8192), n_snapshots)
        compressed_dataset(
            handle,
            "mass_fof_raw_msun",
            raw_history,
            description="Raw same-TrackId FOF mass; NaN marks a missing detection",
            chunks=matrix_chunks,
        )
        compressed_dataset(
            handle,
            "fof_particle_count",
            count_history,
            description="Same-TrackId FOF particle count; zero marks a missing detection",
            chunks=matrix_chunks,
        )

    write_atomic(output, writer)
    print(f"MAH {model}: selected {n_halos:,} z=0 halos", flush=True)
    return output


def extract_radial_selection(project_root: Path, output_dir: Path) -> Path:
    output = output_dir / "radial_profile_selection.hdf5"

    def writer(handle: h5py.File) -> None:
        root_attributes(handle, "radial_profile_selection")
        handle.attrs["snapshot"] = 56
        handle.attrs["selection_window"] = "0.8*target_mass <= M200m <= 1.2*target_mass"
        handle.attrs["max_halos_per_bin"] = RADIAL_MAX_HALOS_PER_BIN
        handle.attrs["centrals_only"] = False
        compressed_dataset(
            handle,
            "target_mass_msun",
            RADIAL_TARGET_MASSES_MSUN,
            description="Centers of radial-profile selection windows",
        )

        for model in MODEL_SPECS:
            source = soap_path(project_root, model, 56)
            print(f"Radial selection {model}: {source}", flush=True)
            with h5py.File(source, "r") as source_handle:
                mass = np.asarray(source_handle["SO/200_mean/TotalMass"], dtype=np.float64) * MASS_UNIT_MSUN
                radius = np.asarray(source_handle["SO/200_mean/SORadius"], dtype=np.float32)
                center = np.asarray(source_handle["SO/200_mean/CentreOfMass"], dtype=np.float64)
                particle_count = np.asarray(
                    source_handle["SO/200_mean/NumberOfDarkMatterParticles"], dtype=np.uint32
                )
                is_central = np.asarray(source_handle["InputHalos/IsCentral"], dtype=np.uint8)
                track_id = np.asarray(source_handle["InputHalos/HBTplus/TrackId"], dtype=np.uint64)

            model_group = handle.create_group(model)
            model_group.attrs["source_file"] = str(source)
            for bin_index, target in enumerate(RADIAL_TARGET_MASSES_MSUN):
                selected = np.flatnonzero(
                    (mass >= 0.8 * target)
                    & (mass <= 1.2 * target)
                    & np.isfinite(radius)
                    & (radius > 0.0)
                    & (particle_count >= 20)
                )
                seed = int(np.log10(target) * 1000) + 2026
                if selected.size > RADIAL_MAX_HALOS_PER_BIN:
                    rng = np.random.default_rng(seed)
                    selected = np.sort(
                        rng.choice(selected, size=RADIAL_MAX_HALOS_PER_BIN, replace=False)
                    )
                group = model_group.create_group(f"mass_bin_{bin_index}")
                group.attrs["target_mass_msun"] = target
                group.attrs["random_seed"] = seed
                compressed_dataset(group, "source_row", selected.astype(np.uint32), description="Zero-based row in z=0 SOAP catalog")
                compressed_dataset(group, "track_id", track_id[selected], description="HBT-HERONS TrackId")
                compressed_dataset(group, "is_central", is_central[selected], description="SOAP InputHalos/IsCentral flag")
                compressed_dataset(group, "mass_m200m_msun", mass[selected], description="SOAP SO/200_mean TotalMass")
                compressed_dataset(group, "radius_r200m_mpc", radius[selected], description="SOAP SO/200_mean SORadius")
                compressed_dataset(
                    group,
                    "center_of_mass_mpc",
                    center[selected],
                    description="SOAP SO/200_mean CentreOfMass used to center particle profiles",
                )
                compressed_dataset(
                    group,
                    "particle_count_m200m",
                    particle_count[selected],
                    description="Dark matter particle count inside R200m",
                )
                print(f"  {model} bin {bin_index}: selected {selected.size}", flush=True)

    write_atomic(output, writer)
    return output


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(output_dir: Path) -> Path:
    manifest = output_dir / "catalog_manifest.csv"
    rows = []
    for path in sorted(output_dir.glob("*.hdf5")):
        rows.append(
            {
                "file": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256sum(path),
            }
        )
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)
    return manifest


def write_readme(output_dir: Path) -> Path:
    readme = output_dir / "README.md"
    readme.write_text(
        "# Compact Article Halo Catalog\n\n"
        "This release contains only the per-halo inputs needed to reproduce the article's main halo statistics.\n\n"
        "- `fof_hmf_source_*.hdf5`: individual FOF groups used by the six-redshift HMF analysis after the article mass cut.\n"
        "- `m200c_concentration_source_*.hdf5`: individual SOAP M200c, c200c, and particle-count inputs after the 100-particle cut.\n"
        "- `mah_track_source_*.hdf5`: same-TrackId raw FOF histories for the PL and BT kp=1 z=0 mass-window samples.\n"
        "- `radial_profile_selection.hdf5`: metadata for the halos selected for the direct radial profiles.\n"
        "- `catalog_manifest.csv`: byte sizes and SHA-256 checksums.\n\n"
        "Full snapshots, SOAP membership files, and complete HBT-HERONS/SOAP catalogs are intentionally excluded. "
        "The article's `public_data/figure_data` directory supplies the reduced radial profiles, half-mass summaries, "
        "power spectra, and other plotted products.\n",
        encoding="utf-8",
    )
    return readme


def validate_release(paths: list[Path]) -> None:
    for path in paths:
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty output: {path}")
        with h5py.File(path, "r") as handle:
            if handle.attrs.get("schema_version") != "1.0":
                raise RuntimeError(f"Unexpected schema in {path}")
            if len(handle.keys()) == 0:
                raise RuntimeError(f"No datasets or groups in {path}")


def main() -> None:
    args = parse_args()
    components = {item.strip() for item in args.components.split(",") if item.strip()}
    allowed = {"fof_hmf", "so", "mah", "radial"}
    unknown = components - allowed
    if unknown:
        raise ValueError(f"Unknown components: {sorted(unknown)}")

    project_root = args.project_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    if "fof_hmf" in components:
        for model in MODEL_SPECS:
            outputs.append(extract_fof_hmf(project_root, output_dir, model))
    if "so" in components:
        for model in MODEL_SPECS:
            outputs.append(extract_so_catalog(project_root, output_dir, model))
    if "mah" in components:
        for model in ("PL", "BT_kp1"):
            outputs.append(extract_mah(project_root, output_dir, model))
    if "radial" in components:
        outputs.append(extract_radial_selection(project_root, output_dir))

    validate_release(outputs)
    write_readme(output_dir)
    manifest = write_manifest(output_dir)
    total_size = sum(path.stat().st_size for path in output_dir.glob("*.hdf5"))
    print(f"Wrote {len(outputs)} HDF5 files ({total_size / 1024**2:.1f} MiB)", flush=True)
    print(f"Manifest: {manifest}", flush=True)


if __name__ == "__main__":
    main()
