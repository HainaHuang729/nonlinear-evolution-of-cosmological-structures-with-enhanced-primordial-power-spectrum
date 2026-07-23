# Public Data Package

This directory contains reduced data products supporting the manuscript figures
and quantitative comparisons. The files are organized by figure-level analysis
product rather than by raw simulation output.

## Contents

- `MANIFEST.csv`: file-by-file inventory with descriptions and source paths.
- `CATALOG_RELEASE.md`: schema, selections, and validation for the separately distributed compact per-halo catalog.
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
- `scripts/`: provenance copies of the plotting and reduction scripts used to generate the figure products.

## Scope

The package is intended to make the plotted trends and quoted figure-level
statistics reproducible without requiring the full raw simulation snapshots.
The raw SWIFT snapshots and complete HBT+/SOAP catalogs are much larger than
the manuscript source package; the reduced files here are the data products
used for the manuscript figures and numerical comparisons.

A separate 74.2 MiB compact catalog provides the individual halo inputs used
for the FOF and `M200c` mass functions, concentration relation, mass-assembly
histories, and radial-profile sample. See `CATALOG_RELEASE.md` for its contents,
selection rules, checksums, and validation procedure. The HDF5 files are kept
outside the manuscript Git repository.

Paths recorded in `MANIFEST.csv` point to the local project locations from
which the reduced products were assembled. The copied scripts in `scripts/`
preserve the analysis logic, but some hard-coded paths may need adaptation if
the package is moved outside the original project workspace.
