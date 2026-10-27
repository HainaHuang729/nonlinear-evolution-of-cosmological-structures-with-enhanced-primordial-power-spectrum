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

Regenerating all 12 manuscript figures also requires the project Colossus
source under `software/colossus/`, the clean projection mosaic and its metadata,
and the radial-profile bootstrap caches. These inputs are not in the GitHub
checkout or the published Zenodo v1.0.0 archive. See
`public_data/REPRODUCIBILITY_PACKAGE.md` for the complete-package specification.
After those inputs have been assembled, run:

```bash
python public_data/scripts/reproduce_all_figures.py
```

The command writes the figures to `reproduced_figures/` and creates
`figure_manifest_sha256.csv` with their dimensions, sizes, and SHA-256
checksums. Add `--overwrite` to replace an existing output directory.

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

The v1.0.0 source and reduced-data archive is available on
[Zenodo](https://doi.org/10.5281/zenodo.22007478). It preserves the repository
at commit `bb7891e`; later manuscript changes and the October power-spectrum
tables are available in the current GitHub branch.

A 74.2 MiB compact catalog has been prepared separately, with FOF and `M200c`
halo inputs at snapshots 24, 27, 30, 32, 40, and 56, tracked mass histories,
and radial-profile selection metadata. It is not included in the current
Zenodo archive. Publication of that catalog and the complete figure inputs
remains pending.

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
