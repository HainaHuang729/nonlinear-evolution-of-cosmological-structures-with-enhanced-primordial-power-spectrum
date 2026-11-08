# Radial density profiles centred on the most-bound particle (2026-11-08)

Same measurement as `public_data/figure_data/halo_density_radial/`, with one
change: the profile centre is the HBTplus most-bound particle position
(`Subhalos/ComovingMostBoundPosition`, matched to SOAP halos through
`InputHalos/HBTplus/TrackId`) instead of `SO/200_mean/CentreOfMass`.

## Settings (identical to the released pipeline otherwise)

- snapshot 0056, z = 0; 25 h^-1 Mpc box; DM particles only
- mass bins, log10 M200m = 10.0, 10.5, 11.0, 11.5 (selection 0.8-1.2 x target)
- up to 100 central halos per bin, reproducible subset
- 20 logarithmic shells of r/R200m between 0.01 and 1
- rho = shell mass / shell volume, in Msun/kpc^3 (comoving)
- error band: 160 bootstrap resamples of the median, 16th-84th percentile
- convergence: Power03 with kappa = 0.6, median over halos
- SWIFT cell indexing: only cells intersecting the R200m sphere are read

## Contents

- `cache/`: per-bin reduced profiles (`x`, `rho_med`, `rho_lo`, `rho_hi`,
  `power_radius`, `nhalo`), 12 files, 3 models x 4 mass bins
- `profiles_mb_{PL,kp1,kp10}.json`: per-halo profiles for both centrings
  (`so` = R200m COM, `mb` = most-bound particle) from the candidate pipeline
- `figures/halo-density-radial-mb-n100_4rows.png`: 4 x 3 panels, one row per
  mass bin, columns PL / BT kp=1 / BT kp=10, NFW reference overlaid
- `figures/halo-density-radial-mb-n100_nfw.png`: two-row layout with BT/PL ratios

## Caveat

The NFW curve in the figures is anchored to the measured density at the
smallest plotted radius, so it compares shapes only, not amplitudes. The
absolute normalisation of the measured profiles is unaffected by this choice.
