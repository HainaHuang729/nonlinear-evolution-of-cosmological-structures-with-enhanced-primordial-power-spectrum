#!/usr/bin/env python3
"""Regenerate and validate every manuscript figure from released inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageStat


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(
    (parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists()),
    SCRIPT_DIR.parents[1],
)

FIGURE_NAMES = [
    "input-power-spectrum.png",
    "projection.png",
    "mass-function.png",
    "mass-function-m200c-bocquet16.png",
    "halo-bias-soap-tinker10.pdf",
    "halfmass-redshift-trackid-no-envelope.png",
    "mass-assembly-history-correa.png",
    "halo-density-radial-mb-corrected.png",
    "concentration-qc-d19-relaxation.png",
    "power-spectrum-btpl.png",
    "fof-hmf-resolution-volume.png",
    "concentration-qc-i21-relaxed-fit-relaxation.png",
    "concentration-qc-l16-relaxation.png",
    "halo-bias-fof-st99.pdf",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ARTICLE_ROOT / "reproduced_figures",
        help="Directory for regenerated PNG and PDF figures.",
    )
    parser.add_argument(
        "--projection-dir",
        type=Path,
        default=None,
        help="Directory containing projection-clean.png and projection-panel-metadata.json.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing expected figures in the output directory.",
    )
    return parser.parse_args()


def resolve_projection_dir(cli_dir: Path | None) -> Path:
    env_dir = os.environ.get("PROJECTION_DATA_DIR")
    candidates: list[Path] = []
    if cli_dir is not None:
        candidates.append(cli_dir.expanduser().resolve())
    if env_dir:
        candidates.append(Path(env_dir).expanduser().resolve())
    candidates.append(ARTICLE_ROOT / "public_data" / "figure_data" / "projection")
    if len(ARTICLE_ROOT.parents) >= 2:
        candidates.append(
            ARTICLE_ROOT.parents[1]
            / "zenodo-release-20261030"
            / "complete-v1.1.0"
            / "public_data"
            / "figure_data"
            / "projection"
        )
    for candidate in candidates:
        if (candidate / "projection-clean.png").exists() and (
            candidate / "projection-panel-metadata.json"
        ).exists():
            return candidate
    return candidates[0]


def has_colossus_package() -> bool:
    local_colossus = ARTICLE_ROOT / "software" / "colossus" / "colossus" / "__init__.py"
    if local_colossus.exists():
        return True
    return importlib.util.find_spec("colossus") is not None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_inputs(projection_dir: Path) -> None:
    required = [
        ARTICLE_ROOT / "main.tex",
        projection_dir / "projection-clean.png",
        projection_dir / "projection-panel-metadata.json",
        ARTICLE_ROOT
        / "public_data"
        / "figure_data"
        / "halo_density_radial"
        / "cache_mb"
        / "PL_M1e+10_N100_B160_all.npz",
        ARTICLE_ROOT / "public_data" / "figure_data" / "halo_bias" / "halo_bias_measurements.csv",
        ARTICLE_ROOT
        / "public_data"
        / "figure_data"
        / "concentration_relaxation"
        / "prescription_comparison_by_mass_bin.csv",
    ]
    missing = [path for path in required if not path.exists()]
    if not has_colossus_package():
        missing.append(ARTICLE_ROOT / "software" / "colossus" / "colossus" / "__init__.py (or PYTHONPATH colossus)")
    if missing:
        joined = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(f"The release is incomplete; missing:\n{joined}")


def run_script(label: str, script_name: str, env: dict[str, str], *args: str) -> None:
    script_path = Path(script_name)
    if not script_path.is_absolute():
        script_path = SCRIPT_DIR / script_name
    command = [sys.executable, str(script_path), *args]
    print(f"[{label}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ARTICLE_ROOT, env=env, check=True)


def validate_figures(output_dir: Path) -> Path:
    manifest_path = output_dir / "figure_manifest_sha256.csv"
    rows = []
    for name in FIGURE_NAMES:
        path = output_dir / name
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty output figure: {path}")
        if path.suffix.lower() == ".pdf":
            with path.open("rb") as handle:
                header = handle.read(5)
            if header != b"%PDF-" or path.stat().st_size < 1024:
                raise RuntimeError(f"Output PDF appears invalid: {path}")
            width: int | str = ""
            height: int | str = ""
        else:
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
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return manifest_path


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    projection_dir = resolve_projection_dir(args.projection_dir)
    existing = [output_dir / name for name in FIGURE_NAMES if (output_dir / name).exists()]
    if existing and not args.overwrite:
        raise FileExistsError(
            f"{len(existing)} expected figures already exist in {output_dir}; use --overwrite"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.overwrite:
        for path in existing:
            path.unlink()

    require_inputs(projection_dir)
    cache_root = output_dir / ".cache"
    (cache_root / "matplotlib").mkdir(parents=True, exist_ok=True)
    (cache_root / "paperplot").mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    python_paths: list[str] = []
    local_colossus = ARTICLE_ROOT / "software" / "colossus"
    if local_colossus.exists():
        python_paths.append(str(local_colossus))
    python_paths.append(str(SCRIPT_DIR))
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
    run_script("1/11 input spectrum", "plot_input_power_spectrum.py", env)

    env["PROJECTION_CLEAN_INPUT"] = str(projection_dir / "projection-clean.png")
    env["PROJECTION_METADATA_INPUT"] = str(projection_dir / "projection-panel-metadata.json")
    env["PROJECTION_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[1])
    run_script("2/11 projection", "plot_projection_public.py", env)

    env["FOF_HMF_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[2])
    run_script("3/11 FOF HMF", "plot_hmf_public_ratio.py", env)

    env["M200C_HMF_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[3])
    env["M200C_HMF_PAPERPLOT_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[3])
    run_script("4/11 M200c HMF", "plot_bocquet16_m200c_hmf.py", env)

    run_script(
        "5/11 halo bias (SOAP+FOF split)",
        "plot_halo_bias.py",
        env,
        "--split",
        "--output",
        str(output_dir / "halo-bias.pdf"),
    )

    env["HALFMASS_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[5])
    run_script("6/11 half-mass redshift", "plot_same_trackid_no_envelope_allmodels.py", env)

    run_script(
        "7/11 mass assembly",
        "plot_mass_assembly_history_correa.py",
        env,
        "--output",
        str(output_dir / FIGURE_NAMES[6]),
    )

    env.update(
        {
            "RADIAL_PROFILE_CACHE_DIR": str(
                ARTICLE_ROOT / "public_data" / "figure_data" / "halo_density_radial" / "cache_mb"
            ),
            "RADIAL_MAX_HALOS_PER_BIN": "100",
            "RADIAL_BOOTSTRAPS": "160",
            "POWER_KAPPA_THRESHOLD": "0.6",
            "RADIAL_OUTPUT_BASENAME": FIGURE_NAMES[7],
            "RADIAL_OUTPUT_PATH": str(output_dir / FIGURE_NAMES[7]),
        }
    )
    run_script("8/11 radial profiles", "bt_plot_halo_density_radial_trial_png.py", env)

    run_script(
        "9/11 concentration (D19, I21R, L16)",
        "plot_concentration_relaxation.py",
        env,
        "--output-dir",
        str(output_dir),
        "--png-only",
    )

    run_script(
        "10/11 nonlinear power",
        str(ARTICLE_ROOT / "public_data" / "ps25-kp10-z0-20261026" / "plot_ps25_btpl.py"),
        env,
        "--output",
        str(output_dir / FIGURE_NAMES[9]),
    )

    env["FOF_HMF_RESOLUTION_OUTPUT_PATH"] = str(output_dir / FIGURE_NAMES[10])
    run_script("11/11 resolution appendix", "plot_fof_hmf_resolution.py", env)

    manifest = validate_figures(output_dir)
    print(f"Validated {len(FIGURE_NAMES)} figures")
    print(manifest)


if __name__ == "__main__":
    main()
