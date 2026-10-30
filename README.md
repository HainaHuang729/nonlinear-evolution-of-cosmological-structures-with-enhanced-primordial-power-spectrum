# Dark Matter Halo Formation with Enhanced Small-Scale Primordial Power

This repository contains the manuscript source, manuscript figures, reduced
numerical data, and figure-regeneration scripts for the article *Dark Matter
Halo Formation with Enhanced Small-Scale Primordial Power*.

## Quick Start

Create a Python environment and install the figure dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The current simulation-only power-spectrum figure can be regenerated directly
from this checkout:

```bash
python public_data/ps25-kp10-z0-20261026/plot_ps25_btpl.py
```

This writes `power-spectrum-btpl.png` at the repository root.

The complete v1.1.0 reproduction package, including the compact halo catalog,
projection inputs, radial-profile caches, and project Colossus source, is
available on [Zenodo](https://doi.org/10.5281/zenodo.23788725). Download
`nonlinear-complete-v1.1.0.tar.gz` and its SHA-256 sidecar from that record.
After checking the archive checksum and extracting it, run inside the package:

```bash
python -m pip install -r requirements.txt
python public_data/scripts/validate_article_halo_catalog.py halo_catalog --article-root .
python public_data/scripts/reproduce_all_figures.py
```

The command writes 12 figures to `reproduced_figures/` and records dimensions,
byte sizes, and SHA-256 checksums in `figure_manifest_sha256.csv`. The archive
also includes the original manuscript figures and successful verification
outputs. See `verification/requirements-tested.txt` for the exact tested
dependency versions. The smaller GitHub checkout contains the reduced tables
and scripts; download the complete archive for all binary inputs.

## Repository Layout

- `main.tex` and `main.bib`: manuscript source and bibliography.
- Root-level PNG files: figures used by the manuscript.
- `public_data/figure_data/`: reduced numerical inputs for the figures and
  quoted comparisons.
- `public_data/scripts/`: figure-regeneration, reduction, extraction, and
  validation scripts.
- `public_data/MANIFEST.csv`: descriptions and provenance of the released
  reduced files.
- `public_data/CATALOG_RELEASE.md`: compact per-halo catalog schema,
  selections, checksums, and validation instructions.
- `public_data/REPRODUCIBILITY_PACKAGE.md`: scope and contents of the
  self-contained release.

## Data Release

The [complete v1.1.0 release](https://doi.org/10.5281/zenodo.23788725) contains
all figure inputs and a 74.2 MiB compact catalog: nine HDF5 files with FOF and
`M200c` halo inputs at snapshots 24, 27, 30, 32, 40, and 56, tracked mass
histories, and radial-profile selections. All catalog checksum and table
validation checks pass, and all 12 figures were regenerated from the package.

The [original v1.0.0 archive](https://doi.org/10.5281/zenodo.22007478) preserves
the source and reduced tables at commit `bb7891e`. It remains available as a
historical version; use v1.1.0 for the complete current reproduction package.

The full SWIFT snapshots and complete HBT-HERONS and SOAP catalogs are not
included because they are hundreds of gigabytes per model and are not required
to reproduce the manuscript measurements.

Once the compact catalog is available, validate the extracted `halo_catalog/`
directory against the reduced article data with:

```bash
python public_data/scripts/validate_article_halo_catalog.py \
    halo_catalog --article-root .
```

See `public_data/README.md` for the figure-level data inventory and
`public_data/CATALOG_RELEASE.md` for field definitions and selection rules.

## Manuscript

The manuscript entry point is `main.tex`. The repository also contains the
APS bibliography style required by the source. LaTeX compilation is separate
from the Python figure-regeneration workflow described above.
