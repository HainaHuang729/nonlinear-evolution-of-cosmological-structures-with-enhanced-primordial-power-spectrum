#!/usr/bin/env python3
"""Regenerate and validate every manuscript figure from released inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageStat


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(
    (parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists()),
    SCRIPT_DIR.parents[2],
)

FIGURE_NAMES = [
    "input-power-spectrum.png",
    "projection.png",
    "mass-function.png",
    "mass-function-m200c-bocquet16.png",
    "halfmass-redshift-trackid-no-envelope.png",
    "mass-assembly-history-correa-halfmass.png",
    "halo-density-radial-n100-power.png",
    "concentration-qc-i21-fit.png",
    "power-spectrum.png",
    "fof-hmf-resolution-volume.png",
    "concentration-qc-d19.png",
    "concentration-qc-l16.png",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ARTICLE_ROOT / "reproduced_figures",
        help="Directory for regenerated PNG files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing expected PNG files in the output directory.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_inputs() -> None:
    required = [
        ARTICLE_ROOT / "main.tex",
        ARTICLE_ROOT / "software" / "colossus" / "colossus" / "__init__.py",
        ARTICLE_ROOT / "public_data" / "figure_data" / "projection" / "projection-clean.png",
        ARTICLE_ROOT
        / "public_data"
        / "figure_data"
        / "projection"
        / "projection-panel-metadata.json",
        ARTICLE_ROOT
        / "public_data"
        / "figure_data"
        / "halo_density_radial"
        / "cache"
        / "PL_M1e+10_N100_B160_all.npz",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        joined = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(f"The release is incomplete; missing:\n{joined}")


def run_script(label: str, script_name: str, env: dict[str, str], *args: str) -> None:
    command = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    print(f"[{label}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ARTICLE_ROOT, env=env, check=True)


def validate_figures(output_dir: Path) -> Path:
    manifest_path = output_dir / "figure_manifest_sha256.csv"
    rows = []
    for name in FIGURE_NAMES:
        path = output_dir / name
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty output figure: {path}")
        with Image.open(path) as image:
            width, height = image.size
            sample = image.convert("RGB").resize((128, 128))
            channel_std = ImageStat.Stat(sample).stddev
        if width < 300 or height < 300 or max(channel_std) < 1.0:
            raise RuntimeError(f"Output figure appears invalid or blank: {path}")
        rows.append(
            {
                "figure": name,
                "width_px": width,
                "height_px": height,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return manifest_path


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    existing = [output_dir / name for name in FIGURE_NAMES if (output_dir / name).exists()]
    if existing and not args.overwrite:
        raise FileExistsError(
            f"{len(existing)} expected figures already exist in {output_dir}; use --overwrite"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.overwrite:
        for path in existing:
            path.unlink()

    require_inputs()
    cache_root = output_dir / ".cache"
    (cache_root / "matplotlib").mkdir(parents=True, exist_ok=True)
    (cache_root / "paperplot").mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    python_paths = [
        str(ARTICLE_ROOT / "software" / "colossus"),
        str(SCRIPT_DIR),
    ]
    if env.get("PYTHONPATH"):
        python_paths.append(env["PYTHONPATH"])
    env.update(
        {
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(cache_root / "matplotlib"),
            "PYTHONPATH": os.pathsep.join(python_paths),
            "COLOSSUS_CACHE_DIR": str(cache_root / "colossus"),
            "PAPERPLOT_ROOT": str(cache_root / "paperplot"),
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )

    env["INPUT_POWER_SPECTRUM_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[0])
    run_script("1/10 input spectrum", "plot_input_power_spectrum.py", env)

    env["PROJECTION_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[1])
    run_script("2/10 projection", "plot_projection_public.py", env)

    env["FOF_HMF_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[2])
    run_script("3/10 FOF HMF", "plot_hmf_public_ratio.py", env)

    env["M200C_HMF_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[3])
    env["M200C_HMF_PAPERPLOT_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[3])
    run_script("4/10 M200c HMF", "plot_bocquet16_m200c_hmf.py", env)

    env["HALFMASS_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[4])
    run_script("5/10 half-mass redshift", "plot_same_trackid_no_envelope_allmodels.py", env)

    run_script(
        "6/10 mass assembly",
        "plot_mass_assembly_history_correa.py",
        env,
        "--output",
        str(output_dir / FIGURE_NAMES[5]),
    )

    env.update(
        {
            "RADIAL_PROFILE_CACHE_DIR": str(
                ARTICLE_ROOT / "public_data" / "figure_data" / "halo_density_radial" / "cache"
            ),
            "RADIAL_MAX_HALOS_PER_BIN": "100",
            "RADIAL_BOOTSTRAPS": "160",
            "POWER_KAPPA_THRESHOLD": "0.6",
            "RADIAL_OUTPUT_BASENAME": FIGURE_NAMES[6],
            "RADIAL_OUTPUT_PATH": str(output_dir / FIGURE_NAMES[6]),
        }
    )
    run_script("7/10 radial profiles", "bt_plot_halo_density_radial_trial_png.py", env)

    env.update(
        {
            "CONCENTRATION_THEORY_KEYS": "diemer19,ishiyama21_fit,ludlow16",
            "CONCENTRATION_OUTPUT_PATH_D19": str(output_dir / FIGURE_NAMES[10]),
            "CONCENTRATION_OUTPUT_PATH_I21_FIT": str(output_dir / FIGURE_NAMES[7]),
            "CONCENTRATION_OUTPUT_PATH_L16": str(output_dir / FIGURE_NAMES[11]),
            "CONCENTRATION_RESIDUAL_CSV_PATH": str(output_dir / "concentration_theory_ratios.csv"),
            "CONCENTRATION_SCATTER_CSV_PATH": str(output_dir / "concentration_scatter.csv"),
        }
    )
    run_script("8/10 concentration", "concentration_qc_kp10.py", env)

    env["POWER_SPECTRUM_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[8])
    run_script("9/10 nonlinear power", "plot_power_spectrum_public_ratio.py", env)

    env["FOF_HMF_RESOLUTION_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[9])
    run_script("10/10 resolution appendix", "plot_fof_hmf_resolution.py", env)

    manifest = validate_figures(output_dir)
    print(f"Validated {len(FIGURE_NAMES)} figures")
    print(manifest)


if __name__ == "__main__":
    main()
