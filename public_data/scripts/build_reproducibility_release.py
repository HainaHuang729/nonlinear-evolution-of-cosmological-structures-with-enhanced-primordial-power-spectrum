#!/usr/bin/env python3
"""Assemble the self-contained article data and figure-reproduction archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import shutil
import tarfile


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists())
DEFAULT_ANALYSIS_ROOT = Path(
    "/oss06/data/project/tkcastrosim/HNHuang/project_big_sim/analysis/"
    "_used_by_article_nonlinear_evolution_pps"
)
DEFAULT_COLOSSUS_PACKAGE = Path(
    "/oss06/data/project/tkcastrosim/HNHuang/envs/Miniconda3/envs/21cmfast/"
    "lib/python3.10/site-packages/colossus"
)
DEFAULT_COLOSSUS_PATCH_ROOT = Path(
    "/oss06/data/project/tkcastrosim/HNHuang/project_big_sim/software/colossus"
)

PLOTTING_SCRIPTS = [
    "bt_plot_halo_density_profile_png.py",
    "bt_plot_halo_density_radial_trial_png.py",
    "concentration_qc_kp10.py",
    "cosmology_plot_style.py",
    "plot_bocquet16_m200c_hmf.py",
    "plot_fof_hmf_resolution.py",
    "plot_hmf_public_ratio.py",
    "plot_input_power_spectrum.py",
    "plot_mass_assembly_history_correa.py",
    "plot_power_spectrum_public_ratio.py",
    "plot_projection_public.py",
    "plot_same_trackid_no_envelope_allmodels.py",
    "reproduce_all_figures.py",
    "validate_article_halo_catalog.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_ROOT / "public_catalog_release_2026-07-23",
    )
    parser.add_argument(
        "--projection-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_ROOT / "paperplot" / "figures",
    )
    parser.add_argument(
        "--radial-cache-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_ROOT / "paperplot" / "cache" / "halo_density_radial_n100_power",
    )
    parser.add_argument(
        "--colossus-package",
        type=Path,
        default=DEFAULT_COLOSSUS_PACKAGE,
        help="Installed Colossus package containing the project PL/BT power-spectrum models.",
    )
    parser.add_argument(
        "--colossus-patch-root",
        type=Path,
        default=DEFAULT_COLOSSUS_PATCH_ROOT,
        help="Colossus source tree containing the local Ludlow16 interface patch and license.",
    )
    parser.add_argument("--no-archive", action="store_true")
    return parser.parse_args()


def ignore_generated(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in {"__pycache__", ".git", "build", "colossus.egg-info"}
        or name.endswith((".pyc", ".pyo"))
    }


def copy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(root: Path) -> Path:
    path = root / "MANIFEST_SHA256.csv"
    rows = []
    for item in sorted(root.rglob("*")):
        if item.is_file() and item != path:
            rows.append(
                {
                    "file": item.relative_to(root).as_posix(),
                    "bytes": item.stat().st_size,
                    "sha256": sha256(item),
                }
            )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    args = parse_args()
    output = args.output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to replace existing release directory: {output}")

    output.mkdir(parents=True)
    copy_file(ARTICLE_ROOT / "main.tex", output / "main.tex")
    for optional_name in ("main.bib", "aastex631.cls"):
        source = ARTICLE_ROOT / optional_name
        if source.exists():
            copy_file(source, output / optional_name)

    shutil.copytree(
        ARTICLE_ROOT / "public_data" / "figure_data",
        output / "public_data" / "figure_data",
        ignore=ignore_generated,
    )
    for name in ("README.md", "CATALOG_RELEASE.md", "MANIFEST.csv"):
        copy_file(ARTICLE_ROOT / "public_data" / name, output / "public_data" / name)
    copy_file(
        ARTICLE_ROOT / "public_data" / "REPRODUCIBILITY_PACKAGE.md",
        output / "README.md",
    )
    copy_file(
        ARTICLE_ROOT / "public_data" / "requirements-figures.txt",
        output / "requirements.txt",
    )
    for name in PLOTTING_SCRIPTS:
        copy_file(SCRIPT_DIR / name, output / "public_data" / "scripts" / name)

    projection_target = output / "public_data" / "figure_data" / "projection"
    copy_file(args.projection_dir / "projection-clean.png", projection_target / "projection-clean.png")
    copy_file(
        args.projection_dir / "projection-panel-metadata.json",
        projection_target / "projection-panel-metadata.json",
    )

    radial_target = output / "public_data" / "figure_data" / "halo_density_radial" / "cache"
    shutil.copytree(args.radial_cache_dir, radial_target, ignore=ignore_generated)

    catalog_target = output / "halo_catalog"
    catalog_target.mkdir()
    for source in sorted(args.catalog_dir.iterdir()):
        if source.is_file():
            copy_file(source, catalog_target / source.name)

    colossus_target = output / "software" / "colossus"
    shutil.copytree(args.colossus_package, colossus_target / "colossus", ignore=ignore_generated)
    copy_file(
        args.colossus_patch_root / "colossus" / "halo" / "concentration.py",
        colossus_target / "colossus" / "halo" / "concentration.py",
    )
    for name in ("LICENSE.txt", "README.rst"):
        copy_file(args.colossus_patch_root / name, colossus_target / name)
    (colossus_target / "PROJECT_PROVENANCE.txt").write_text(
        "The package is copied from the project's 21cmfast Python environment.\n"
        "Its power_spectrum.py contains the eisenstein98_pl, eisenstein98_bt, and "
        "eisenstein98_bt_soft models used by the manuscript.\n"
        "halo/concentration.py is taken from Colossus source commit "
        "e51408a3eaffef073da1df767160cb2441177cc0 with the local Ludlow16 "
        "ps_args/sigma_args working-tree patch.\n",
        encoding="utf-8",
    )
    (output / "data").mkdir()
    (output / "data" / ".keep").write_text("", encoding="utf-8")

    manifest = write_manifest(output)
    print(f"Wrote {manifest}")

    if not args.no_archive:
        archive = output.parent / f"{output.name}.tar.gz"
        if archive.exists():
            raise FileExistsError(f"Refusing to replace existing archive: {archive}")
        with tarfile.open(archive, "w:gz") as handle:
            handle.add(output, arcname=output.name)
        checksum_path = archive.with_suffix(archive.suffix + ".sha256")
        checksum_path.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")
        print(f"Wrote {archive}")
        print(f"Wrote {checksum_path}")


if __name__ == "__main__":
    main()
