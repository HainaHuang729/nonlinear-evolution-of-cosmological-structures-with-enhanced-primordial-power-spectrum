# Article Script Guide

This directory contains the complete set of 29 scripts retained with the
article. It stays flat because several scripts import the shared plotting
module or call neighboring scripts by filename. Classification is recorded
here and in `SCRIPT_MANIFEST.csv` without changing those stable paths.

## Reproduce the manuscript figures

From the root of the release, run:

```bash
python public_data/scripts/reproduce_all_figures.py
```

This command uses the released reduced data and regenerates all 12 manuscript
figures. It does not read the full SWIFT snapshots or complete halo catalogs.

## Current portable figure scripts

- `reproduce_all_figures.py`: runs and validates the complete 12-figure set.
- `plot_input_power_spectrum.py`: input linear matter spectra.
- `plot_projection_public.py`: projected-density mosaic labels.
- `plot_hmf_public_ratio.py`: FOF halo mass function.
- `plot_bocquet16_m200c_hmf.py`: M200c halo mass function.
- `plot_same_trackid_no_envelope_allmodels.py`: half-mass redshift.
- `plot_mass_assembly_history_correa.py`: median mass-assembly histories.
- `bt_plot_halo_density_radial_trial_png.py`: radial density profiles.
- `concentration_qc_kp10.py`: three concentration figures.
- `plot_power_spectrum_public_ratio.py`: nonlinear matter power spectrum.
- `plot_fof_hmf_resolution.py`: FOF resolution and volume appendix.

## Upstream cluster reductions

These scripts require project simulation products or complete catalogs. Run
them through Slurm in the project workspace; they are not part of the portable
one-command path.

- `halomass_fof_reed07.py`: derives FOF mass-function measurements.
- `compute_sim_power_spectrum.py`: measures simulation power spectra.
- `plot_power_spectrum_bt_over_pl.py`: builds the nonlinear power-spectrum
  comparison tables and project figure.
- `extract_article_halo_catalog.py`: builds the compact per-halo release.

## Validation and release workflow

- `validate_article_halo_catalog.py`: validates the compact catalog against
  released figure tables.
- `summarize_concentration_metrics.py`: regenerates concentration summaries.
- `build_reproducibility_release.py`: assembles the self-contained archive.
- `submit_extract_article_halo_catalog.sbatch`: catalog-extraction Slurm job.
- `bt_submit_halo_density_radial_n100_power.sh`: radial-profile Slurm job.
- `plot_mass_assembly_history_correa.sbatch`: MAH plotting Slurm job.
- `cosmology_plot_style.py`: shared plotting style.

## Archived revision scripts

These files document analyses or figures that were replaced during revision.
They are retained for provenance and are not called by
`reproduce_all_figures.py`.

- `bt_plot_halo_density_profile_png.py`
- `bt_plot_mass_fraction_trackid_png.py`
- `compute_m200c_main_branch_accretion.py`
- `plot_m200c_main_branch_accretion.py`
- `plot_fof_gamma_appendix.py`
- `plot_power_spectrum_halofit.py`
- `test_fof_gap_stitching_halfmass.py`

## Execution labels

- `portable`: uses released inputs and can run outside the cluster.
- `cluster`: expects full project data and must run through Slurm.
- `current`: supports a current figure or release workflow.
- `archived`: retained only for provenance.

Temporary diagnostics, failed release copies, version snapshots, and legacy
power-spectrum scripts are intentionally excluded because they do not produce
the current manuscript results.
