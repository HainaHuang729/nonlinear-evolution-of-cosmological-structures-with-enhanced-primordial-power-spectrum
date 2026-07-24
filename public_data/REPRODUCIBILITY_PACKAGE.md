# Article Figure Reproducibility Package

This package contains the reduced numerical inputs and plotting code needed to
regenerate all 12 figures used by the manuscript. It also includes a compact
per-halo catalog for rebinning the main halo statistics.

## Quick Start

Create a Python environment, install the plotting dependencies, and run:

```bash
python -m pip install -r requirements.txt
python public_data/scripts/reproduce_all_figures.py
```

The second command writes the 12 PNG files to `reproduced_figures/` and writes
`figure_manifest_sha256.csv` with image dimensions, byte sizes, and SHA-256
checksums. Use `--overwrite` to replace a previous run.

## Included Inputs

- `public_data/figure_data/`: reduced figure-level CSV tables.
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

The projected-density input is a derived two-dimensional mosaic. It reproduces
the published projection and its labels, but it cannot be used to choose a new
line of sight or projection depth. The direct radial-profile caches retain the
published medians, bootstrap intervals, sample counts, and convergence radii;
the compact halo catalog retains the corresponding halo selection metadata.

See `public_data/CATALOG_RELEASE.md` for the per-halo schema and selection
rules. See `MANIFEST_SHA256.csv` for a checksum of every distributed file.
