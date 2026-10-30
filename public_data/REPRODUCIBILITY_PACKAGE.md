# Article Figure Reproducibility Package

The complete v1.1.0 package is available on
[Zenodo](https://doi.org/10.5281/zenodo.23788725) as
`nonlinear-complete-v1.1.0.tar.gz`, with a SHA-256 sidecar and validation report.
It includes all nine compact catalogs, clean projection inputs, radial-profile
caches, and the project Colossus source. The smaller GitHub checkout and the
original v1.0.0 archive do not include all of these binary inputs.

Catalog checksums and comparisons with the current article tables pass. All
12 figures were regenerated from an isolated package directory. The archive
contains original manuscript images and verification outputs, validation logs,
and exact tested dependency versions under `verification/`. Small image-bound
and font-rendering differences can occur across environments. The package
also contains the manuscript TeX source, original figures, and required
bibliography style. The compiled PDF and duplicate validation images are
kept outside the archive to reduce download size.

The commands below apply inside the extracted complete archive. The current
simulation-only power spectrum can also be regenerated directly from GitHub.

## Quick Start

Create a Python environment, install the plotting dependencies, and run:

```bash
python -m pip install -r requirements.txt
python public_data/scripts/reproduce_all_figures.py
```

The second command writes the 12 PNG files to `reproduced_figures/` and writes
`figure_manifest_sha256.csv` with image dimensions, byte sizes, and SHA-256
checksums. Use `--overwrite` to replace a previous run.

See `public_data/scripts/README.md` for the script groups and
`public_data/scripts/SCRIPT_MANIFEST.csv` for the complete file-level index.
The one-command driver uses only the current portable plotting scripts.

## Included Inputs

- `public_data/figure_data/`: reduced figure-level CSV tables.
- `public_data/ps25-kp10-z0-20261026/`: current phase-pair spectra, BT/PL
  ratios, and the simulation-only plotting script.
- `public_data/figure_data/projection/projection-clean.png`: the unlabeled 3 by
  3 projected-density mosaic used to regenerate `projection.png`.
- `public_data/figure_data/halo_density_radial/cache/`: compact bootstrap
  profile caches used to regenerate the direct radial-density figure.
- `halo_catalog/`: nine compressed HDF5 files containing the individual halo
  inputs used for the main FOF, M200c, concentration, assembly-history, and
  radial-profile selections.
- `software/colossus/`: the Colossus source used for the PL and BT analytic
  reference curves, including the project power-spectrum extensions.

For the Diemer--Joyce and Ishiyama concentration panels, the plotted discrete
theory values and simulation-to-theory ratios are read directly from the
released table. The smooth reference lines use shape-preserving interpolation
through those values. This prevents changes in Colossus cache state from
changing the published comparison. The Ludlow curves are evaluated with the
included project Colossus source.

## Scope

The package reproduces every plotted figure without access to the original
cluster paths. The full SWIFT snapshots, particle coordinates, and complete
HBT-HERONS/SOAP catalogs are not included because they are hundreds of
gigabytes per model.

The article scripts are included in the assembled archive. This set
contains the portable figure scripts, upstream cluster reductions, validation
tools, Slurm wrappers, and archived scripts kept for revision provenance.
Archived scripts are identified in `SCRIPT_MANIFEST.csv` and are not called by
the one-command figure driver.

The projected-density input is a derived two-dimensional mosaic. It reproduces
the published projection and its labels, but it cannot be used to choose a new
line of sight or projection depth. The direct radial-profile caches retain the
published medians, bootstrap intervals, sample counts, and convergence radii;
the compact halo catalog retains the corresponding halo selection metadata.

See `public_data/CATALOG_RELEASE.md` for the per-halo schema and selection
rules. See `MANIFEST_SHA256.csv` for a checksum of every distributed file.
