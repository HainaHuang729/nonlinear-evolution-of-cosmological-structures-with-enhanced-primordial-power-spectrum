#!/usr/bin/env python3
"""Remeasure COM and most-bound profiles on the published halo selections."""
import argparse
import os
from pathlib import Path

import h5py
import numpy as np

MODELS = {"PL": "PL", "BTKP1": "BT_kp1", "BTKP10": "BT_kp10"}


def match_most_bound(paths, wanted):
    positions = {}
    for path in paths:
        with h5py.File(path, "r") as handle:
            subhalos = handle["Subhalos"]
            ids = np.asarray(subhalos["TrackId"], dtype=np.uint64).reshape(-1)
            rows = np.flatnonzero(np.isin(ids, wanted))
            if isinstance(subhalos, h5py.Group):
                xyz = subhalos["ComovingMostBoundPosition"][rows]
            else:
                xyz = subhalos.fields("ComovingMostBoundPosition")[rows]
            for track_id, position in zip(ids[rows], xyz):
                if track_id in positions:
                    raise ValueError(f"Duplicate HBT TrackId {track_id} in {path}")
                positions[track_id] = position
    missing = set(wanted) - positions.keys()
    if missing:
        raise ValueError(f"{len(missing)} selected TrackIds missing from supplied HBT files")
    return positions


def measure(radial, snap, centers, radii, cells):
    measurements = [
        radial.halo_particle_profile(snap, center, radius, *cells, return_counts=True)
        for center, radius in zip(centers, radii)
    ]
    rho, power, counts = map(np.asarray, zip(*measurements))
    return rho, power, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--soap", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--hbt", type=Path, nargs="+", required=True)
    parser.add_argument("--mb-to-mpc", type=float, required=True,
                        help="Conversion of HBT coordinates to snapshot Mpc at z=0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--selection", type=Path, default=(
        Path(__file__).resolve().parents[1] / "particle_profiles_paired/radial_profile_selection.hdf5"
    ))
    args = parser.parse_args()
    if not np.isfinite(args.mb_to_mpc) or args.mb_to_mpc <= 0:
        parser.error("--mb-to-mpc must be finite and positive")
    args.output.mkdir(parents=True, exist_ok=True)
    os.environ["POWER_KAPPA_THRESHOLD"] = "0.6"
    os.environ["POWER_REFERENCE_OVERDENSITY_CRIT"] = "63"
    os.environ.setdefault("PAPERPLOT_ROOT", str(args.output.resolve() / ".runtime"))
    import bt_plot_halo_density_radial_trial_png as radial

    with h5py.File(args.selection, "r") as selection:
        targets = selection["target_mass_msun"][:]
        group = selection[MODELS[args.model]]
        bins = [
            {key: value[:] for key, value in group[f"mass_bin_{i}"].items()}
            for i in range(len(targets))
        ]
    wanted = np.unique(np.concatenate([b["track_id"] for b in bins]))
    mb_positions = match_most_bound(args.hbt, wanted)
    with h5py.File(args.soap, "r") as soap, h5py.File(args.snapshot, "r") as snap:
        box = np.broadcast_to(np.asarray(snap["Header"].attrs["BoxSize"], float), (3,))
        if not np.allclose(box, 25 / 0.6736, rtol=0.01):
            raise ValueError(f"Unexpected snapshot box size in Mpc: {box}")
        cells = tuple(
            snap[f"Cells/{key}/PartType1"][:]
            for key in ("MinPositions", "MaxPositions", "OffsetsInFile", "Counts")
        )
        for i, (target, selected) in enumerate(zip(targets, bins)):
            rows, ids = selected["source_row"], selected["track_id"]
            actual_ids = soap["InputHalos/HBTplus/TrackId"][rows].reshape(-1)
            np.testing.assert_array_equal(actual_ids, ids)
            radii = soap["SO/200_mean/SORadius"][rows]
            com = soap["SO/200_mean/CentreOfMass"][rows]
            np.testing.assert_allclose(radii, selected["radius_r200m_mpc"], rtol=1e-6)
            np.testing.assert_allclose(com, selected["center_of_mass_mpc"], atol=1e-8)
            mb = args.mb_to_mpc * np.asarray([mb_positions[track_id] for track_id in ids])
            if mb.shape != com.shape or not np.isfinite(mb).all():
                raise ValueError("Invalid most-bound position array")
            mb %= box
            delta = mb - com
            delta -= box * np.rint(delta / box)
            displacement = np.linalg.norm(delta, axis=1) / radii
            result = {"track_id": ids, "source_row": rows, "target_mass": target,
                      "r_over_r200m": radial.RADIAL_X, "r200m_mpc": radii,
                      "com_mpc": com, "mb_mpc": mb, "offset_over_r200m": displacement,
                      "is_central": selected["is_central"], "mb_to_mpc": args.mb_to_mpc,
                      "snapshot_path": str(args.snapshot), "soap_path": str(args.soap),
                      "hbt_paths": [str(path) for path in args.hbt]}
            for name, centers in (("com", com), ("mb", mb)):
                rho, power, counts = measure(radial, snap, centers, radii, cells)
                result.update({f"{name}_rho": rho, f"{name}_power_radius": power,
                               f"{name}_counts": counts, f"{name}_median": np.nanmedian(rho, axis=0)})
            output = args.output / f"{args.model}_bin{i}.npz"
            tmp = output.with_suffix(".tmp.npz")
            np.savez_compressed(tmp, **result)
            tmp.replace(output)
            print(f"{output}: {len(ids)} matched, median offset/R200m "
                  f"{np.median(displacement):.4g}, max {np.max(displacement):.4g}", flush=True)


if __name__ == "__main__":
    main()
