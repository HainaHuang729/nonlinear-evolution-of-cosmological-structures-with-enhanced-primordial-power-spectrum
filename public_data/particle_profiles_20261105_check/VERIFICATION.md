# VERIFICATION — particle radial profiles

Status: partially complete. This file distinguishes **completed**, **historical**
and **outstanding** items from `RADIAL_PROFILE_REMOTE_CHECKLIST_20261105.md` and
`RADIAL_PROFILE_FOLLOWUP_20261106.md`.

## 1. Correction of an earlier claim (historical)

An earlier progress note in this repository described the manuscript figure
`halo-density-radial-n100-power.png` as an "analytic NFW stack". That was wrong.
The released figure is **already particle-binned**; its provenance is
`public_data/scripts/bt_plot_halo_density_radial_trial_png.py`, driven by
`bt_submit_halo_density_radial_n100_power.sh`, with reduced tables in
`public_data/figure_data/halo_density_radial/`. The claim is superseded and the
`data/particle_profiles_20261105/README.md` has been corrected.

## 2. Reproduction of the released numbers (completed)

The released script was rerun with a fresh cache
(`paperplot/cache/halo_density_radial_recheck`) for the two common mass bins and
all three models, using the documented settings
(`RADIAL_MAX_HALOS_PER_BIN=100`, `RADIAL_BOOTSTRAPS=160`,
`POWER_KAPPA_THRESHOLD=0.6`, `RADIAL_PARTICLE_CHUNK=250000`).

| model | mass [Msun] | max rel. diff | median rel. diff | nhalo | r_conv/R200m |
|---|---|---:|---:|---:|---:|
| PL | 1e10 | 4.1e-10 | 6.3e-11 | 100 | 0.0673 |
| PL | 1e11 | 3.4e-10 | 5.9e-11 | 100 | 0.0274 |
| BTKP1 | 1e10 | 4.6e-10 | 1.1e-10 | 100 | 0.0655 |
| BTKP1 | 1e11 | 3.4e-10 | 5.1e-11 | 100 | 0.0282 |
| BTKP10 | 1e10 | 3.5e-10 | 6.9e-11 | 100 | 0.0616 |
| BTKP10 | 1e11 | 3.6e-10 | 3.7e-11 | 100 | 0.0255 |

Differences are floating-point round-off, so the released tables are reproducible.
Reduced comparison: `comparison_old_new.csv` (120 rows). The `rel_diff` column is
the **absolute** relative difference, `|rho_new - rho_ref| / |rho_ref|`, computed
from full-precision arrays and not from the rounded columns.

Generating command (released pipeline, one model/bin per invocation):

```
export PROJECT_BIG_SIM_ROOT=/project/tkcastrosim/HNHuang/project_big_sim
export PAPERPLOT_ROOT=$PROJECT_BIG_SIM_ROOT/analysis/_used_by_article_nonlinear_evolution_pps/paperplot
export RADIAL_PROFILE_CACHE_DIR=$PAPERPLOT_ROOT/cache/halo_density_radial_recheck
export RADIAL_MAX_HALOS_PER_BIN=100 RADIAL_BOOTSTRAPS=160 RADIAL_PARTICLE_CHUNK=250000
export POWER_KAPPA_THRESHOLD=0.6
for label in PL BTKP1 BTKP10; do for mass in 1e10 1e11; do
  RADIAL_ONLY_LABELS=$label RADIAL_ONLY_MASSES=$mass python bt_plot_halo_density_radial_trial_png.py
done; done
```

## 3. Candidate pipeline: what it is and what it is not (historical, then current)

The candidate figure in `halo-density-radial-particles-bt-pl.png` comes from
`particle_profiles_chunk.py`. It uses different mass bins, a different halo
selection (centrals only, five closest), both centrings, percentile bands instead
of bootstraps, and a shell-count mask instead of a Power03 convergence radius.
It is therefore **not** a controlled comparison with the released figure; this is
a property of the design, not a result.

The earlier candidate PNG did lack a kp1 curve and had an empty 1e12 ratio panel.
That has since been fixed: the current files contain five halos per model, mass
and centring, and the current PNG shows kp1 and both ratios at 1e12. The plotter
bug responsible for the empty panel -- both ratios gated on the simultaneous
presence of PL and BTKP1 -- has been fixed and each ratio is now gated
independently on the PL denominator.

## 4. Outstanding items

- P1 controlled comparison: rerun the candidate pipeline with the released
  selection (identical halo IDs, all catalog entries, 0.8-1.2 mass window, <=100
  halos, `SO/200_mean` centres) at 1e10 and 1e11; compare shell counts first;
  keep the central-only and bound-subhalo variants as labelled diagnostics.
- P1 Power03 kappa = 0.6 convergence radii for the candidate selections, with the
  softening scale and the way per-halo radii are summarised.
- P1 explicit definition of the bands (halo-to-halo scatter, 16th-84th) and, if
  adopted, bootstrap uncertainty on BT/PL itself.
- P1 provenance: snapshot redshift/scale factor, physical versus comoving units,
  box-size provenance, run identifiers, and the completion status of job 2354384.
  That job (kp1/kp10 with the 1e12 bin) finished COMPLETED 0:0 in 3h32m; its
  outputs are `profiles_kp1.json` and `profiles_kp10.json`.
- P2 portability: replace hard-coded paths with CLI options; add a manifest of
  input/output hashes; fix the overlapping row titles; add redshift, halo counts,
  centring and band definition to the caption; include ratio uncertainty.

## 5. Recommendation

Retain the released manuscript figure and the released tables. The candidate
remains a diagnostic until the controlled comparison above is delivered. No
manuscript source, released table or archive was modified.
