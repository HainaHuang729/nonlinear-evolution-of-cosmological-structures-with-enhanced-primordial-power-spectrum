# Public Data Package

This directory contains reduced data products supporting the manuscript figures
and quantitative comparisons. The files are organized by figure-level analysis
product rather than by raw simulation output.

## Contents

- `MANIFEST.csv`: file-by-file inventory with descriptions and source paths.
- `CATALOG_RELEASE.md`: schema, selections, and validation for the separately distributed compact per-halo catalog.
- `REPRODUCIBILITY_PACKAGE.md`: quick-start instructions and the scope of the self-contained archive.
- `requirements-figures.txt`: Python dependencies for regenerating the manuscript figures.
- `figure_data/metadata/`: simulation-suite and figure-file manifests.
- `figure_data/input_power_spectra/`: input linear matter spectra.
- `figure_data/fof_hmf/`: binned FoF halo mass-function points.
- `figure_data/m200c_hmf/`: binned `M200c` halo mass-function points.
- `figure_data/halfmass_redshift/`: same-TrackId half-mass redshift points and summaries.
- `figure_data/mass_assembly_history/`: same-TrackId median FOF mass histories for PL and the `kp=1` BT model, together with the fixed and half-mass-closure Correa curves used in `mass-assembly-history-correa-halfmass.png`.
- `figure_data/mass_accretion/`: archived accretion diagnostics retained for revision traceability. They are not used by the current manuscript figures.
- `figure_data/halo_density/`: concentration-derived NFW density-profile curves and mass-bin summaries.
- `figure_data/halo_density_radial/`: direct particle-count radial density profiles and BT/PL ratios used in `halo-density-radial-n100-power.png`.
- `figure_data/concentration/`: binned `c200c` concentration-mass data.
- `figure_data/nonlinear_power_spectrum/`: nonlinear matter power spectra and BT/PL ratios.
- `figure_data/appendix_fof_gap_stitching/`: appendix gap-stitching data and notes.
- `figure_data/fof_hmf_resolution/`: appendix FOF mass-function resolution and volume check data.
- `scripts/reproduce_all_figures.py`: one-command regeneration and validation of all 12 manuscript figures.
- `scripts/build_reproducibility_release.py`: project-side assembler for the self-contained archive.
- `scripts/`: plotting, reduction, catalog-extraction, and validation scripts.

## Scope

The package is intended to make the plotted trends and quoted figure-level
statistics reproducible without requiring the full raw simulation snapshots.
The raw SWIFT snapshots and complete HBT+/SOAP catalogs are much larger than
the manuscript source package; the reduced files here are the data products
used for the manuscript figures and numerical comparisons.

A separate 74.2 MiB compact catalog provides the individual halo inputs used
for the FOF and `M200c` mass functions, concentration relation, mass-assembly
histories, and radial-profile sample. The self-contained archive combines this
catalog with `figure_data/`, the clean projection mosaic, radial-profile
bootstrap caches, and the project Colossus source. See `CATALOG_RELEASE.md` for
the catalog contents, selection rules, checksums, and validation procedure. The
large binary files are kept outside the manuscript Git repository.

Paths recorded in `MANIFEST.csv` point to the local project locations from
which the reduced products were assembled. In the assembled archive, run
`python public_data/scripts/reproduce_all_figures.py` from any location to
write and validate all 12 figures under `reproduced_figures/`. Raw-data
reduction scripts retain project path defaults because the full snapshots are
not distributed; the figure-regeneration path does not use those paths.
