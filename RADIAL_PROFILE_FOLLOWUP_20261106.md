# Follow-up review of the particle-profile verification bundle

Date: 2026-11-06
Reviewed commit: `52b2c47`
Scope: remaining work from `RADIAL_PROFILE_REMOTE_CHECKLIST_20261105.md`.

## What is now available

- Three per-halo profile JSON files, including shell particle counts and both
  centering choices; copies under `data/` and the verification bundle agree.
- The candidate analysis and plotting scripts.
- A 120-row comparison of a rerun of the released pipeline with released tables.
- A verification report and an updated candidate PNG.
- Each model now has five halos at each of the four target masses for each
  centering choice. The updated PNG includes kp1 and both ratios at 1e12 Msun.

These are useful additions. They do not yet complete the controlled comparison
requested in the original checklist. Retain the current manuscript figure.

## P0: Correct inconsistent documentation

1. `data/particle_profiles_20261105/README.md` still incorrectly describes the
   manuscript figure as an analytic NFW stack. The released figure is already
   particle-binned, as correctly acknowledged in `VERIFICATION.md`. Correct the
   README and mark the corresponding historical progress-note claim as superseded.
2. `VERIFICATION.md` describes the missing kp1 curve and empty 1e12 ratio panel
   using the original candidate. Identify that as historical: the current PNG
   and JSON files have those outputs. Do not attribute the old blank panel to
   sparse sampling without evidence. The committed plotter gates *both* ratios
   on the presence of PL and BTKP1; an absent BTKP1 therefore also suppresses an
   otherwise available BTKP10/PL curve. Gate each ratio independently.
3. Record the exact script versions, commands, arguments and output provenance.
   The analysis script defaults to ten halos whereas the supplied files contain
   five per model/mass/center. Document the actual invocation.

## P1: Complete the controlled comparison

The new comparison table checks a fresh run of the **released** pipeline against
released CSV values. It does not compare the candidate pipeline to the released
pipeline under identical settings.

- Run both calculations at 1e10 and 1e11 Msun with identical halo IDs, all-entry
  selection, 0.8–1.2 mass windows, reproducible subsets of at most 100 halos,
  SO/200_mean COM centers, R200m, shell edges, particles and periodic wrapping.
- Compare per-halo shell counts before densities and median stacks. Supply the
  selected IDs, actual masses/radii, contributor counts and declared tolerance.
- Keep the alternative central-only, five-closest selection and bound-subhalo
  centering as separately identified diagnostics.
- Include sample counts and convergence status in the comparison outputs.

The reported relative differences (~1e-10) are consistent with the supplied
comparison table's stored `rel_diff` magnitudes. Its density columns are rounded,
so recomputing those differences from the displayed columns cannot reproduce all
reported digits. Preserve sufficient precision and define `rel_diff` (signed or
absolute). Provide the script/command that generated the comparison table.

## P1: Convergence, uncertainty and provenance

- Compute Power03 kappa=0.6 diagnostics for the actual candidate selections.
  A shell-count cutoff is not a replacement for this convergence check. Record
  softening, per-halo convergence radii and how the displayed limit is summarized.
- Define the displayed 16th–84th percentile bands as halo-to-halo scatter. They
  are not bootstrap intervals of the median. If bootstrap intervals are adopted,
  record resampling count/seed and provide uncertainty on BT/PL itself.
- State the low-count masking rule precisely. The plotter currently masks when
  at least `max(1, int(0.5*N))` halos have fewer than ten particles. For N=5 this
  masks at two low-count halos; this is not the same as masking where the median
  count is below ten, as the README claims. Choose and document one definition.
- Supply snapshot redshift/scale factor, units, box size provenance, source/run
  identifiers, job exit status and relevant logs. Clarify physical/comoving
  lengths and ensure the periodic box uses the same units as particle positions
  and halo centers. Do not infer coordinate conventions from particle mass.
- Record completion of job 2354384 or its replacement; the periodic status file
  gives JSON sizes and unrelated running jobs, not its exit status.

## P2: Make the bundle portable and finish the figure

- Replace hard-coded cluster input/output and style-module paths with CLI options
  or documented configurable defaults. Include a local reproduction command that
  uses only the committed reduced JSON files and the existing shared style file.
- Add a lightweight manifest of source/run identifiers and input/output hashes;
  do not upload raw particle coordinates, full snapshots or credentials.
- Fix the second-row mass titles overlapping the preceding ratio x-axis labels.
- Include redshift, five-halo sample counts, plotted SO COM centering and band
  definition in the caption/metadata. Mark convergence limits once computed.
- Include ratio uncertainty and explain missing/untrusted radial intervals.
- Keep PL black, kp1 blue and kp10 green, using the shared plotting style.

## Requested next delivery

Update the existing verification bundle with the controlled-comparison outputs,
selection/provenance manifest, portable reproduction instructions, corrected
documentation and corrected diagnostic figure. Revise `VERIFICATION.md` so that
completed, historical and outstanding items are distinguished accurately.

Do not replace the manuscript figure or released tables until this evidence has
been reviewed. Do not overwrite the published Zenodo archive. O30 (quantitative
NFW-fit accuracy) and O33 (mass-accretion additions) remain deferred.
