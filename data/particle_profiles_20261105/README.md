# Particle-binned halo density profiles (2026-11-05)

## Relationship to the manuscript figure

The manuscript figure `halo-density-radial-n100-power.png` is **already a
particle-binned calculation**, produced by
`public_data/scripts/bt_plot_halo_density_radial_trial_png.py` with reduced
tables in `public_data/figure_data/halo_density_radial/`. An earlier progress
note in this repository described it as an analytic NFW stack; that statement
was wrong and is superseded.

This directory therefore contains an **independent candidate pipeline**, not a
replacement for the released one. It differs from the released pipeline in every
choice that matters:

| aspect | released pipeline | this candidate |
|---|---|---|
| mass bins | 1e10, 10^10.5, 1e11, 10^11.5 | 1e9, 1e10, 1e11, 1e12 |
| halo selection | 0.8-1.2 x M200m, <=100 halos, reproducible subset | within 0.2 dex, 5 closest |
| catalog entries | all entries | centrals only (`IsCentral == 1`) |
| centring | `SO/200_mean/CentreOfMass` | both that and `BoundSubhalo/CentreOfMass` |
| uncertainty band | 160 bootstrap resamples of the median | 16th-84th percentile of halos (halo-to-halo scatter) |
| convergence | Power03, kappa = 0.6 | shells with fewer than 10 particles masked |

Because every one of those choices differs, panel-to-panel differences between
this figure and the manuscript figure mix sample selection, binning and
statistics; they are not a physical effect.

## Candidate pipeline steps

1. read SOAP `halo_properties_0056.hdf5`; convert `SO/200_mean/TotalMass` with
   `U_M = 1e10 Msun` and `SORadius` with `U_L = 1 Mpc`;
2. keep central haloes within 0.2 dex of the target mass and take the 5 closest;
3. stream the snapshot in chunks of 4e6 particles; for each chunk compute the
   periodic-wrapped distance to every selected halo centre (box = 37.1 Mpc);
4. accumulate mass and particle count in 20 logarithmic shells of `r/R200m`
   between 0.01 and 1, then `rho = M_shell / V_shell` in Msun/kpc^3;
5. mask a shell when at least half of the haloes in the bin have fewer than ten
   particles in it (the earlier README described this as a median-count rule; the
   implemented rule is the "half of the haloes" rule);
6. optional NFW reference: amplitude-matched with the same M200 and c.

## Contents

- `profiles_PL.json`, `profiles_kp1.json`, `profiles_kp10.json`: per halo, per
  centre, the shell-averaged density `rho` and the particle `count` per shell.
- Source runs: `PL/PL_25_1024`, `bluetilted/kp_1_ms_1.5_25_1024`,
  `bluetilted/kp_10_ms_1.5_25_1024`; snapshot 0056.
- Mass bins: 1e9, 1e10, 1e11, 1e12 Msun; the 1e8 bin is omitted because
  `N200 ~ 50` particles only.
- DM particle mass: 1.89e6 Msun (confirms the 37.1 Mpc physical box).
- Figure: `halo-density-radial-particles-bt-pl.png` (PL black, BTKP1 blue,
  BTKP10 green; bottom panels show BT/PL).

## Caveats

- 1e12 Msun bins contain few haloes in a 37 Mpc box, so their scatter is large.
- Shells below the masking radius are still stored in the JSON; do not use them.
- The profiles use DM particles only; gas/baryonic effects are not included.
