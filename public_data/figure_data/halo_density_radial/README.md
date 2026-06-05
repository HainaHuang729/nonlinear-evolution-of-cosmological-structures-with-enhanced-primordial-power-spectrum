# Direct Radial Halo Density Profiles

This directory supports `halo-density-radial-n100-ludlow177.png`.

- `radial_density_profiles_n100_ludlow177.csv` gives the direct particle-count radial density profiles used in the upper panels. Each row is one model, one target \(M_{200m}\) bin, and one radial bin.
- `radial_density_ratios_n100_ludlow177.csv` gives the BT/PL ratios used in the lower panels.

The profiles use at most \(N=100\) halos per model and mass bin. The plotted error intervals are bootstrap 16th--84th percentile intervals for the median stacks. The convergence marker uses \(\kappa=0.177\), matching the figure label. The dashed NFW curves in the figure are reference profiles, not fits to the particle stacks.

The provenance plotting script is `public_data/scripts/bt_plot_halo_density_radial_trial_png.py`. The Slurm wrapper `public_data/scripts/bt_submit_halo_density_radial_n100_ludlow177.sh` records the settings used for the manuscript figure.
