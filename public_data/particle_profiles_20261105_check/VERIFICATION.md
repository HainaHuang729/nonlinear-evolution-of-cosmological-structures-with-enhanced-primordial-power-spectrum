# VERIFICATION — particle radial profiles (2026-11-06)

Scope: respond to `RADIAL_PROFILE_REMOTE_CHECKLIST_20261105.md`. This is a
verification record, not a replacement of the manuscript figure.

## 1. Correction to the earlier progress note

`PROGRESS_20261105.md` described the current manuscript figure as an
"analytic NFW stack". That was wrong. The released figure
`halo-density-radial-n100-power.png` is **already particle-binned**; its
provenance is `bt_plot_halo_density_radial_trial_png.py` driven by
`bt_submit_halo_density_radial_n100_power.sh`, with reduced tables in
`public_data/figure_data/halo_density_radial/`.

## 2. Reproduction of the released numbers

The released script was rerun with a fresh cache
(`paperplot/cache/halo_density_radial_recheck`) for the two common mass bins
(1e10, 1e11 Msun) and all three models, with the documented settings
(`RADIAL_MAX_HALOS_PER_BIN=100`, `RADIAL_BOOTSTRAPS=160`,
`POWER_KAPPA_THRESHOLD=0.6`).

| model | mass [Msun] | max rel. diff vs released CSV | median rel. diff | nhalo | r_conv/R200m |
|---|---|---:|---:|---:|---:|
| PL | 1e10 | 4.1e-10 | 6.3e-11 | 100 | 0.0673 |
| PL | 1e11 | 3.4e-10 | 5.9e-11 | 100 | 0.0274 |
| BTKP1 | 1e10 | 4.6e-10 | 1.1e-10 | 100 | 0.0655 |
| BTKP1 | 1e11 | 3.4e-10 | 5.1e-11 | 100 | 0.0282 |
| BTKP10 | 1e10 | 3.5e-10 | 6.9e-11 | 100 | 0.0616 |
| BTKP10 | 1e11 | 3.6e-10 | 3.7e-11 | 100 | 0.0255 |

All differences are floating-point round-off, so the released tables are
reproducible from the released code and the current cluster data.

Reduced comparison: `comparison_old_new.csv` (120 rows, columns
model / target_mass_msun / r_over_r200m / rho_recomputed / rho_released_csv /
rel_diff).

## 3. Where the candidate figure differs from the released one

The candidate `halo-density-radial-particles-bt-pl.png` (commit 3050f7f) was
produced by `analysis/particle_profiles_chunk.py`, which differs from the
released pipeline in every choice the checklist lists:

| aspect | released pipeline | candidate pipeline |
|---|---|---|
| mass bins | 1e10, 10^10.5, 1e11, 10^11.5 | 1e9, 1e10, 1e11, 1e12 |
| halo selection | 0.8–1.2 x M200m, <=100 halos, reproducible random subset | within 0.2 dex, 5 closest |
| centrals only? | no (all catalog entries) | yes (`IsCentral == 1`) |
| centring | SOAP `SO/200_mean/CentreOfMass` (per released code) | both SO COM and `BoundSubhalo` COM |
| uncertainty | 160 bootstrap resamples of the median | 16–84 percentile of halos |
| convergence | Power03, kappa = 0.6 | shells with <10 particles masked |
| ratio | as released (ratio of stacked medians) | median stack ratio BT/PL |

Consequently the candidate figure is **not** a controlled comparison with the
released one; differences in the panels mix sample selection, binning, and
statistics. In particular the missing kp1 curve and the empty BT/PL ratio panel
at 1e12 are consequences of the candidate sample (a few halos near 1e12), not of
physics.

## 4. Outstanding items (P1/P2) and recommendation

Not yet done, in checklist order:

1. rerun the candidate pipeline with the released selection (0.8–1.2 x M, <=100
   halos, all entries) at the two common bins, and compare shell counts before
   densities;
2. adopt the Power03 kappa = 0.6 convergence radius for the plotted radial
   limit, and state how per-halo radii are summarised;
3. define the shaded band explicitly (bootstrap of the median, 160 resamples)
   and the ratio uncertainty;
4. restore a complete figure (all model/bin combinations), fix the overlapping
   titles, include redshift, halo counts and centring in the caption;
5. only then decide whether to retain, supplement or replace the released
   figure.

Recommendation for now: **retain the released figure**; treat the candidate as a
diagnostic. No manuscript source or released table was modified by this check.
