# Reviewer Comments Record

Date: 2026-04-26

Role: journal reviewer / critical reader

Overall recommendation: Major Revision

The manuscript has a scientifically useful direction: it studies how enhanced small-scale primordial power is mapped into nonlinear dark-matter structure formation using controlled cosmological simulations. However, in its current form the paper would likely receive a major-revision decision because the numerical methodology, parameter definitions, convergence evidence, and quantitative support for the conclusions are not yet strong enough for a simulation paper.

## 1. Manuscript Still Looks Like a Draft

Issue:

- The manuscript still contains visible draft markup such as `\blue{...}`, `\yellow{...}`, `\color{red}`, and text such as "future revisions", "final manuscript", and "we plan".
- Examples occur in the theory, methods, numerical robustness, power-spectrum, acknowledgments, and appendix sections.

Why this matters:

- A reviewer will immediately read this as an unfinished manuscript.
- Draft markup weakens confidence in the completeness of the analysis.

Recommended action:

- Remove all color markup before submission.
- Replace planning language with completed analysis.
- If a result is not yet ready, either complete it or move it explicitly to future work.

## 2. Simulation Suite and Model Definitions Are Inconsistent

Issue:

- The text says that nine simulations are run, but the simulation table lists more runs.
- The manuscript mainly discusses PL, BT_soft, and BT_deep, while the table also includes `m_s=2.0` models and several box-size / resolution variants.
- It is not fully clear which runs are production runs, which are convergence tests, and which are unused.

Why this matters:

- The reader cannot reconstruct exactly which simulations support each figure.
- Reviewers may question whether unused simulations were omitted because they weaken the conclusions.

Recommended action:

- Create one clean simulation-suite table with columns such as model role, box size, particle number, particle mass, softening, `k_p`, `m_s`, number of snapshots, and figures using the run.
- State explicitly which three runs form the main comparison.
- State explicitly which runs are used only for convergence tests.

## 3. Blue-Tilted Parameters and Units Are Confusing

Issue:

- The manuscript uses multiple forms for the pivot scale:
  - `k_p \approx 1` and `10 Mpc^{-1}`;
  - `3.51` and `0.702 cMpc^{-1}`;
  - `h Mpc^{-1}` in figure captions.
- BT_soft and BT_deep are sometimes described by physical interpretation and sometimes by numerical values that do not obviously match.

Why this matters:

- The BT model is the central theoretical input of the paper. If its parameters are unclear, the whole result becomes hard to trust or reproduce.

Recommended action:

- Choose one unit convention for `k_p`, preferably `h\,\mathrm{Mpc}^{-1}` or `\mathrm{Mpc}^{-1}`, and use it everywhere.
- Add a short conversion note if values are inherited from papers using `cMpc^{-1}`.
- State whether `k_p=1` and `10` are approximate labels or exact simulation parameters.
- Make BT_soft and BT_deep definitions identical in the text, tables, captions, and code labels.

## 4. Low-Mass Halo Claims May Be Below the Resolution Limit

Issue:

- The fiducial particle mass is about `8.1e7 h^{-1} M_sun`.
- A 20-particle halo threshold implies a formal lower mass of about `1.6e9 h^{-1} M_sun`.
- The manuscript nevertheless discusses halos down to `10^8 M_sun` and even profile behavior near or below that mass.

Why this matters:

- Claims about low-mass halo abundance, profiles, and concentrations are central to the paper.
- If these claims use halos below the reliable particle-number limit, reviewers will treat them as numerical artifacts.

Recommended action:

- Compute and state the particle-number limit corresponding to 20, 50, 100, and 300 particles for each relevant run.
- Use a conservative scientific threshold, not just the catalog-detection threshold.
- Shade or cut unreliable mass ranges in figures.
- Do not interpret density profiles or concentrations for halos with insufficient particle counts.

## 5. Convergence Tests Are Mentioned But Not Demonstrated

Issue:

- The manuscript says convergence tests were performed, but the current text still says that limits will be quantified in future revisions.
- No explicit trusted mass, radius, or wavenumber range is currently given.

Why this matters:

- Simulation papers are judged heavily on numerical convergence.
- Without convergence figures or quantified cuts, the main results remain qualitative.

Recommended action:

- Add convergence plots for:
  - halo mass function versus mass resolution and box size;
  - density profiles versus softening and particle number;
  - concentration-mass relation versus resolution;
  - matter power spectrum versus mesh size / particle resolution / box size.
- Add a table of adopted trusted ranges:
  - mass range for HMF;
  - minimum radius for density profiles;
  - mass range for concentration;
  - usable `k` range for power spectra.

## 6. Power-Spectrum Estimator Is Not Reproducible Yet

Issue:

- The manuscript does not yet state the exact power-spectrum estimator settings.
- Missing details include mesh size, mass-assignment scheme, shot-noise treatment, window-function correction, FFT normalization, binning, and maximum trusted `k`.

Why this matters:

- The paper claims high-`k` enhancement, but high-`k` measurements are exactly where estimator choices, aliasing, force resolution, and shot noise matter most.
- Reviewers will not accept a high-`k` result unless the estimator is fully specified.

Recommended action:

- Add a methods paragraph specifying:
  - mesh size, e.g. `N_mesh^3`;
  - assignment scheme, e.g. CIC or TSC;
  - overdensity definition;
  - Fourier convention and normalization;
  - `k` binning scheme;
  - shot-noise subtraction, if used;
  - mass-assignment window deconvolution, if used;
  - aliasing treatment, if any;
  - maximum trusted `k`, such as a fraction of `k_Nyq`.

Suggested template, only if it matches the actual code:

```latex
The nonlinear matter power spectrum is estimated by assigning dark matter particles to a regular Cartesian mesh using the CIC mass-assignment scheme. We construct the overdensity field, $\delta(\mathbf{x})=\rho(\mathbf{x})/\bar{\rho}-1$, and Fourier transform it using an FFT. The isotropically averaged power spectrum is computed by binning Fourier modes in spherical shells in $k$-space. We subtract the Poisson shot-noise contribution, $P_{\rm shot}=1/\bar{n}$, where $\bar{n}$ is the mean particle number density. The CIC window function is deconvolved from the measured Fourier amplitudes before binning. To avoid modes strongly affected by grid assignment and discreteness, we restrict the interpretation to $k < 0.5 k_{\rm Nyq}$, where $k_{\rm Nyq}=\pi N_{\rm mesh}/L$.
```

Important caution:

- This text should only be inserted after checking the actual script that generated `power-spectrum.png`.

## 7. Sample Variance and Random Phases Are Not Addressed

Issue:

- The manuscript does not clearly state whether PL, BT_soft, and BT_deep use identical random phases.
- It also does not include multiple realizations.
- Halo mass-function errors are described mainly as Poisson errors.

Why this matters:

- A `25 h^{-1} Mpc` box can have significant cosmic variance.
- If different random phases are used, some differences between models may reflect realization variance rather than the PPS modification.

Recommended action:

- State whether matched phases are used across models.
- If matched phases are used, emphasize this as a strength.
- If not, either run matched-phase simulations or discuss sample variance more explicitly.
- Consider jackknife, bootstrap over subvolumes, or multiple random seeds if available.

## 8. Halo Mass Definitions Are Mixed

Issue:

- HBT+ / SOAP provides spherical-overdensity properties such as `M200c` and `R200c`.
- The halo mass function uses FOF masses.
- The concentration analysis uses `M200c`.
- The analytic comparison uses `mdef='fof'`.

Why this matters:

- FOF and SO masses are not interchangeable.
- The interpretation of abundance, profiles, and concentration depends on the mass definition.

Recommended action:

- Add a short mass-definition subsection.
- State which mass definition is used for each statistic.
- Avoid comparing or interpreting FOF and `M200c` results as though they were the same mass.
- Make captions and axis labels explicit.

## 9. Subhalo Claims Are Not Quantitatively Supported

Issue:

- The manuscript mentions subhalos and substructure several times.
- However, the Results section does not include a subhalo mass function, subhalo radial distribution, subhalo abundance ratio, or survival analysis.
- The claim that substructures are more centrally concentrated appears to be based mainly on projected maps.

Why this matters:

- A projected map is illustrative but not enough to support quantitative claims about subhalo abundance or radial concentration.

Recommended action:

- Either remove subhalo-specific claims from the main conclusions or add a quantitative subhalo analysis.
- If substructure is retained, add:
  - subhalo mass function;
  - radial number-density profile;
  - host-mass controlled comparison;
  - resolution cuts for subhalos.

## 10. Some Results Are Overstated Relative to Their Quantitative Support

Issue:

- The abstract and conclusion use strong phrases such as "substantial excess", "systematically denser", and "pronounced high-k enhancement".
- The text often does not give exact ratios, mass ranges, redshift ranges, or uncertainties.

Why this matters:

- Reviewers expect the main claims to be numerically anchored.

Recommended action:

- Convert qualitative statements into quantitative results.
- Example structure:
  - "At `z = ...`, BT_soft increases the HMF by a factor of `...` over `M = ...`."
  - "At fixed `M200c = ...`, the median concentration increases by `...` relative to PL."
  - "The nonlinear power ratio `P_BT/P_PL` reaches `...` at `k = ...`, within the trusted range."

## 11. Density-Profile Interpretation Needs More Caution

Issue:

- The manuscript interprets inner enhancement and outer suppression in density profiles as a meaningful radial anti-correlation.
- The low-mass and inner-radius profile measurements are exactly where particle number, force softening, centering, and stacking choices matter.

Why this matters:

- Density-profile conclusions can be fragile unless convergence cuts are explicit.

Recommended action:

- Apply a minimum particle-number threshold for profile stacks.
- Mark the force-softening scale and any adopted convergence radius in the profile figure.
- Report the number of halos in each profile stack.
- Avoid interpreting radii below the convergence radius.

## 12. Observational Claims Need a Clear Boundary

Issue:

- The manuscript connects results to JWST galaxies, 21 cm, strong lensing, dwarf galaxies, and weak lensing.
- This is useful, but the simulations are dark-matter-only and do not include baryons, star formation, radiative transfer, or survey selection.

Why this matters:

- Reviewers may think the manuscript overstates its observational reach.

Recommended action:

- Keep the observational discussion as motivation and implication, not as a direct constraint.
- Emphasize that this paper provides a dark-matter benchmark for future forward modeling.

## Priority Fix List Before Submission

Highest priority:

- Remove all draft markup and future-tense placeholder text.
- Fix BT model parameter and unit consistency.
- Define reliable mass, radius, and `k` ranges using convergence tests.
- Fully document the power-spectrum estimator.
- Correct low-mass halo claims that fall below the resolution limit.

Second priority:

- Clarify which simulations support each result.
- State whether random phases are matched.
- Clean up FOF versus `M200c` mass-definition usage.
- Quantify the main results with ratios and uncertainties.

Optional but valuable:

- Add a subhalo-specific section only if substructure is a central claim.
- Add a short table summarizing the main quantitative effects of BT_soft and BT_deep relative to PL.

## Suggested Editorial Verdict

The project has a clear scientific motivation and could make a useful contribution as a controlled dark-matter-only benchmark for enhanced small-scale primordial power. However, the current manuscript does not yet meet the methodological and numerical-robustness standards expected for a simulation paper. A reviewer would likely request major revision, focused on reproducibility, convergence, parameter consistency, and quantitative support for the main claims.
