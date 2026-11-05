# Remote checks for the new particle radial profiles

Date: 2026-11-05

## Purpose and scope

Review the new `halo-density-radial-particles-bt-pl.png` introduced in commit
`3050f7f` before deciding whether it should replace or supplement the manuscript
figure. This is a verification request, not authorization to replace the paper
figure with an incomplete result.

The current manuscript figure is `halo-density-radial-n100-power.png`. It already
uses direct particle-binned profiles, not profiles reconstructed from fitted
concentrations. Its provenance is:

- `public_data/scripts/bt_plot_halo_density_radial_trial_png.py`
- `public_data/scripts/bt_submit_halo_density_radial_n100_power.sh`
- `public_data/figure_data/halo_density_radial/README.md`
- `public_data/figure_data/halo_density_radial/radial_density_profiles_n100_power03.csv`
- `public_data/figure_data/halo_density_radial/radial_density_ratios_n100_power03.csv`

The author's deferred tasks remain deferred: O30 (a quantitative NFW fitting
accuracy study) and O33 (adding mass-accretion-rate results to the article).
Neither is a prerequisite for completing the comparisons requested here.

## Findings from the committed materials

1. The new mass bins are approximately 1e9, 1e10, 1e11 and 1e12 Msun. The existing
   figure uses 1e10, 10^10.5, 1e11 and 10^11.5 Msun. These are different samples.
2. The new 1e12 Msun panel has no kp1 curve, and its entire BT/PL panel is empty,
   although PL and kp10 density curves are visible above it.
3. The new figure does not identify convergence radii, halo sample counts,
   redshift, the plotted centering choice, or the meaning of its shaded bands.
4. The second-row mass titles overlap the preceding row's horizontal-axis labels.
5. Commit 3050f7f contains only the new PNG and a progress note. The new script,
   numerical outputs and selection metadata are not included in that commit.
6. The progress note says kp1/kp10 are rerunning with the 1e12 Msun bin. This is
   a historical status report, not confirmation of completed outputs. Local SSH
   checks through both the direct host and VPN jump host timed out during review.

## P0: Recover provenance and check run completeness

- Locate the script reported as `analysis/particle_profiles_chunk.py`, the
  `profiles_PL.json` and corresponding kp1/kp10 outputs, and the actual plotting
  script used for the uploaded PNG. Preserve these exact versions.
- Report the current state of job 2354384 and any replacement jobs, including
  exit status, logs and which model/mass-bin outputs are complete. Do not assume
  that a finished PL calculation means the other models are complete.
- Record snapshot/redshift, simulation identifiers, particle mass, coordinate
  units, box length, scale factor and conversions to the plotted density units.
  Distinguish comoving and physical lengths; the note's 25 h^-1 Mpc = 37.1 Mpc
  conversion alone does not specify that distinction at a general redshift.
- Record input paths and lightweight identifiers/checksums where practical.
  Do not upload simulation snapshots or particle coordinates to GitHub.

## P1: Reconcile the common mass bins before interpreting differences

Use the common 1e10 and 1e11 Msun bins first. Produce a controlled comparison of
the old and new calculations with identical inputs and choices:

- M200m mass definition, units and mass-window edges. The existing selection uses
  0.8 to 1.2 times the target mass, at most 100 halos per model/bin, and a
  reproducible random subset. Check the actual run wrapper for all overrides.
- Halo IDs and sample counts; whether centrals only or all catalog entries were
  used. Do not silently change the sample to centrals only.
- The center used for each calculation: `SO/200_mean/CentreOfMass` versus
  `BoundSubhalo/CentreOfMass`. Identify which is plotted in the new PNG and show
  their effect separately. Keep the mass/radius aperture definition explicit.
- The same per-halo R200m normalization, radial edges and periodic wrapping.
- Which particles enter each shell: all dark matter particles or a bound subset.
- Per-halo shell counts, shell volumes, density conversion, and the aggregation
  rule (median of individual profiles versus a pooled/mean stack).
- Treatment of empty shells and nonfinite values. Report the number of
  contributing halos per radial bin, especially where the model curves start
  at different radii. Do not infer that missing bins imply physical zero density.
- The ratio definition and interpolation grid. State whether it is the ratio of
  median stacks or an average of individually matched ratios; do not assume a
  cross-model halo correspondence without demonstrating it.

Provide an old/new comparison table for each common model and mass bin. Include
radius, density, fractional difference, sample count and convergence status.
If all inputs and selections are matched, compare shell counts directly before
comparing stacked densities. Explain any discrepancy rather than choosing the
more visually appealing result. Use a declared numerical tolerance and identify
boundary/rounding effects where relevant.

## P1: Establish the usable radial ranges and uncertainties

- Compute convergence diagnostics from the new per-halo enclosed counts and
  densities using the documented Power03 convention and kappa=0.6. State how
  per-halo convergence radii are summarized into a displayed mass-bin limit.
- For reference only, the current figure's largest model-median r_conv/R200m is
  about 0.06726 at 1e10 Msun and 0.02817 at 1e11 Msun. These values come from the
  current released CSV; they are not convergence limits for a new sample.
- The 1e9 Msun bin contains roughly 530 particles at the quoted particle mass
  of 1.89e6 Msun. Total halo particle count does not validate its innermost shells.
  Report shell occupancy, softening scale and convergence before interpreting
  apparent inner enhancement or flattening.
- Define the shaded bands: halo-to-halo scatter, bootstrap confidence intervals
  of the median, or another statistic. Include the resampling count and seed.
- Define how uncertainties of BT/PL are constructed. The current product labels
  its ratio bounds as derived from bootstrap profile bounds; distinguish that
  from a bootstrap distribution of the ratio itself.
- Show uncertainty information in the ratio panels, or explain why it cannot
  yet be provided. Avoid significance claims based solely on curve separation.

## P2: Complete and clean the candidate figure

- Include all completed model/mass-bin combinations. For missing combinations,
  give an explicit missing-data explanation rather than an unexplained blank.
- Investigate why the 1e12 Msun ratio panel is entirely empty even though PL and
  kp10 appear above it. Check common valid radii, denominator masks and plotting
  logic. If there is no common usable radial interval, document that fact.
- Mark unresolved radii and explain the marks in the caption.
- Add redshift, halo counts, centering definition and the band interpretation to
  the figure/caption or accompanying metadata.
- Correct overlapping labels. Use the shared `cosmology_plot_style.py`, retain
  PL black, kp1 blue and kp10 green, and use readable physical model labels.
- Make comparisons to the current figure at common mass bins and common trusted
  radii. Do not describe changing mass bins or centers as a new physical effect.

## Deliverables to commit

Put a portable verification bundle in
`public_data/particle_profiles_20261105_check/`:

1. The actual analysis/plotting scripts, with configurable input paths and a
   documented reproduction command; no cluster credentials.
2. Reduced profile and ratio CSV/JSON files, per-shell counts where compact,
   halo-selection metadata, and a manifest of source/run identifiers.
3. `comparison_old_new.csv` for the common 1e10 and 1e11 Msun bins.
4. A concise `VERIFICATION.md` recording completed checks, discrepancies,
   convergence/uncertainty definitions, missing outputs and the recommendation
   to retain, supplement or replace the current figure.
5. A corrected candidate PNG with complete metadata and explained missing data.

Leave the current manuscript source and figure in place until this evidence is
reviewed. Do not overwrite the existing released tables or Zenodo archive.

## Separate BTemu progress items

The 10-D 21cm power-spectrum dataset and BTemu draft described in
`PROGRESS_20261105.md` are a separate project. Keep their verification/results in
the BTemu repository. The note's statement that MS<1.5 is invalid is not supported
by diagnostic evidence in this commit: investigate configuration, failed runs,
zero-signal definitions and parameter coverage before making it a scientific
domain restriction. Batch counts and chain status should be verified from their
outputs rather than copied from this historical note into either paper.
