# Overleaf review comment audit

Scope: checked against the current local blue-revision manuscript in `main.tex`.

Important limitation: the exported Review text does not include the original highlighted spans. When the target sentence is ambiguous, I mark the item as `NEEDS ANCHOR` rather than guessing too aggressively.

Status legend:

- `DONE`: current local draft appears to address the comment.
- `PARTIAL`: current draft addresses part of it, but wording, consistency, or evidence still needs work.
- `OPEN`: not addressed in the current local draft.
- `DATA/FIGURE`: requires new analysis, figure changes, or additional data products.
- `NOTE`: no action, positive comment, or superseded by a later instruction.
- `NEEDS ANCHOR`: exact target sentence is unclear without Overleaf's highlighted span.

## One-by-one audit

1. `DONE` -- "primordial matter power spectrum"
   The draft now defines a terminology rule: "primordial power spectrum" is the early-Universe phenomenological template, "primordial matter power spectrum" may be used sparingly when emphasizing seeded matter fluctuations, and "input linear matter power spectrum at \(z_i=200\)" is reserved for the spectrum passed to MonofonIC.
   Current location: `main.tex` around line 160.

2. `DONE` -- "primordial power spectrum"
   The terminology pass now uses "primordial power spectrum" and "primordial power-spectrum template" for the model-level physical signal, while preserving "input linear matter power spectrum at \(z_i=200\)" for implementation-specific MonofonIC inputs.
   Current locations: `main.tex` around lines 151, 159-185, 247, 285, 326-355, 390-409, and 438-460.

3. `NOTE` -- "I think these can be more qualitative in the abstract"
   This seems partly superseded by later comments requesting clearer quantitative statements. Current abstract is quantitative.
   Next action: do not remove numbers automatically; instead make the first abstract sentence more qualitative and keep only the most important benchmark numbers.

4. `DONE` -- "these are obsoletes. But there are new higher redshift tensions."
   The introduction now mentions early JWST high-redshift galaxy candidates and avoids relying only on older small-scale-CDM tensions.
   Current location: `main.tex` around line 122.

5. `DONE` -- "Add more relevant reference."
   Several relevant references were added for JWST, blue-tilted/modified PPS work, baryonic caveats, PBHs, and observational probes.
   Current locations include `main.tex` around lines 122, 129, 134, and 143.

6. `PARTIAL` -- "need rewrite"
   Some introduction paragraphs were rewritten, but several later sentences remain awkward or flagged again by later comments.
   Next action: handle together with comments 13, 17, 47, 49, 50, 51, 55, 61, 62, and 77.

7. `DONE` -- "We haven't shown these in our paper"
   Anchor supplied by user: the sentence about observational probes highlighting degeneracies. Rewrote it so the text says those studies motivate complementary probes, but those probes require astrophysical/observational modeling and do not by themselves isolate the dark-matter halo response.
   Current location: `main.tex` around line 149.

8. `DONE` -- "Not quite true. Because we need to pass through the monofonic IC, then the matter power spectrum is not linear. Also, it depends also on the seed."
   Current draft now states that the BT template is passed through MonofonIC, that the MonofonIC random seed is kept identical across matched PL and BT runs, and that the matched simulations share the same initial phases.
   Current location: `main.tex` around lines 185, 225, and 247.

9. `DONE` -- "need rewrite"
   The initial-condition paragraph has been rewritten more directly around the MonofonIC transfer-function plugin, shared normalization, identical random seed, and matched initial phases.

10. `DONE` -- sigma8 question
   Current draft now states that PL and BT use the same target `sigma_8=0.8111`, that BT spectra are not assigned separately fitted `sigma_8` values, and that MonofonIC applies the required global normalization to each generated spectrum.
   Current location: `main.tex` around lines 210, 238, and 245.

11. `DONE` -- keep same sigma8
   Same as comment 10. The revised cosmology and initial-condition text explicitly says the target normalization is held fixed across PL and BT.

12. `DONE` -- combine table with simulation table, follow arXiv:1112.0330v2
   The separate input-power model table has been removed as a structural table, and its `k_p`/`m_s` information is now folded into the combined simulation summary table.
   Current location: `main.tex` around lines 216-217 and 247-275.

13. `PARTIAL` -- clumsy sentence
   Several clumsy sentences remain, especially in Discussion and Conclusions.
   Next action: treat as a prose-polish item after structural comments are addressed.

14. `DONE` -- "First, we modify, instead of implementation modify"
   The live revision now uses first-person active wording: "we modify the MonofonIC transfer-function plugin above \(k_p\)". The old passive wording only remains in the deleted/struck text for revision tracking.
   Current location: `main.tex` around line 225.

15. `DONE` -- inconsistent "input matter power spectrum"
   A terminology pass was completed. Most model-level uses of "input matter power" were replaced by "primordial power spectrum" or "primordial power-spectrum template"; "input linear matter power spectrum at \(z_i=200\)" remains where the text specifically refers to the MonofonIC input or the plotted input spectra.
   Note: older wording still appears inside struck/deleted revision text and commented-out draft text.
   Current locations: `main.tex` around lines 151, 159-185, 225-250, 285, 326-355, 390-409, 438-460, 499, and 505.

16. `DONE` -- use "the shape of primordial power spectrum"
   The theoretical framing now uses "the shape of the primordial power spectrum" and defines how that model-level template differs from the MonofonIC input linear matter power spectrum.
   Current location: `main.tex` around lines 159-160.

17. `PARTIAL` -- "This sentence is also strange. We can be more direct:"
   Current draft is more direct in places, but the specific sentence cannot be identified without the anchor.
   Next action: likely merge with comment 18 wording.

18. `DONE` -- "Therefore, we can test the effect of enhanced primordial power spectrum, given the same initial phases."
   Current draft now says the matched simulations share the same initial phases and that this lets us test the effect of enhancing the small-scale primordial-power template after it is passed through MonofonIC, rather than comparing different random realizations.
   Current location: `main.tex` around line 225.

19. `DONE` -- compare particle scale with enhancement scale
   Current draft now compares the BT pivot scales directly with the fiducial particle grid: \(L_{\rm box}/1024=0.0244\,h^{-1}{\rm Mpc}\), \(k_{\rm Ny}\simeq128.7\,h\,{\rm Mpc}^{-1}\), \(k_{\rm Ny}/k_p\simeq129\) for BT\_soft and \(12.9\) for BT\_deep, with pivot wavelengths corresponding to about 257 and 26 inter-particle spacings. The text also states that this is an input-spectrum placement check, not a full nonlinear convergence test.
   Current locations: `main.tex` around lines 227 and 232.

20. `DONE` -- "You also use other definitions later on."
   A mass-definition paragraph was added.
   Current location: `main.tex` around line 285.

21. `DONE` -- discuss binning
   The nonlinear power-spectrum measurement now describes mesh deposition and log-binning.
   Current location: `main.tex` around line 425.

22. `DONE` -- "No need to mention"
   Anchor supplied by user: repeated fiducial particle-mass / 20-particle threshold sentence in the HMF section. Removed it from the live HMF text and referred instead to the conservative cut summarized in Table~\ref{tab:trusted_ranges}.
   Current location: `main.tex` around line 324.

23. `DONE` -- "Since you have shown the particle mass in the table already."
   Same anchor as comment 22. The HMF section no longer repeats the fiducial particle mass; it uses the table and the adopted mass cut.
   Current location: `main.tex` around line 324.

24. `DONE` -- "This is mentioned already"
   Anchor supplied by user: the analytic-curve sentence about using the same FOF mass definition and same linear spectra. Replaced the live text with a shorter statement that separate PL, BT_soft, and BT_deep reference predictions are computed from the corresponding linear matter power spectra.
   Current location: `main.tex` around line 326.

25. `DONE` -- "This is mentioned already, and the wording is strange"
   Anchor supplied by user: the model-matched comparison sentence. Replaced it with a direct statement that the analytic curves are reference HMF predictions and the simulation points plus BT/PL ratios are the measured nonlinear response.
   Current location: `main.tex` around line 326.

26. `DONE` -- define M200c
   `M_{200c}`, `R_{200c}`, and `c_{200c}` are now defined.
   Current locations: `main.tex` around lines 285, 355, and 397-412.

27. `DONE` -- ratio between PL and BT; "Direct model response" unclear
   The live text now calls the lower panels the "BT/PL abundance ratio", and both HMF captions describe the lower panels as BT\_soft/PL and BT\_deep/PL mass-function ratios. The plotted axis label already uses \(f_{\rm BT}/f_{\rm PL}\); the old phrase only remains in struck/deleted revision text.
   Current locations: `main.tex` around lines 328, 346, and 355.

28. `DONE` -- define B16 in text
   B16 is now defined as Bocquet et al. fitting function.
   Current location: `main.tex` around line 331.

29. `DONE` -- "Not defined yet"
   Likely the same B16/M200c issue. Both are now defined before use.

30. `DATA/FIGURE` -- add mass accretion rate study
   No mass-accretion-rate study is present.
   Next action: requires new diagnostic, likely `dM/dz` or `d ln M / d ln a` from merger histories, plus figure/table or appendix.

31. `PARTIAL` -- detailed material can go in text or appendix
   Current draft moved/added detailed method text, and Appendix is referenced for FOF gap-stitching.
   Remaining issue: some method details may still crowd captions and main text.

32. `DONE` -- "between what and BK09"
   The caption now defines the lower-panel quantity explicitly as \(\Delta z_{1/2}=z_{1/2}^{\rm sim}-z_{1/2}^{\rm BK09}\), using the same binned simulation points as the upper panel.
   Current location: `main.tex` around line 367.

33. `DONE` -- why compare to BK09
   The text now states that BK09 and COCO/Hellwing16 are external \(\Lambda\)CDM reference relations used only to check that the PL catalog-level diagnostic lies in a plausible range, not the main target of the paper.
   Current location: `main.tex` around line 362.

34. `DONE` -- compare BT to PL
   The text now identifies the matched BT--PL difference as the main comparison and gives direct shifts in representative bins: at \(M_{z=0}\simeq1.25\times10^9\,M_\odot\), BT\_soft and BT\_deep form earlier than PL by \(\Delta z_{1/2}=1.96\) and \(0.33\), respectively; at \(7.9\times10^9\,M_\odot\), the shifts are \(1.17\) and \(0.10\).
   Current location: `main.tex` around line 362.

35. `DONE` -- shaded region for too few particles
   HMF caption includes a gray band for the 20-particle to adopted cut range.
   Current location: `main.tex` around line 351.

36. `DONE` -- "It is just dark matter halo density profile and NFW profile."
   The live draft now frames this diagnostic as concentration-derived NFW density profiles reconstructed from catalog masses, radii, and concentrations.
   Current locations: `main.tex` around lines 373-383.

37. `DONE` -- "NFW-equivalent compactness curves" is strange
   The live text now uses plainer names such as "Concentration-derived NFW density profiles", "NFW density-profile reconstruction", and "concentration-derived NFW profile summaries".
   Note: the old phrase still appears inside `\revisionreplace{new}{old}` deleted text so it will be visible as struck-through redline markup.
   Current locations: `main.tex` around lines 280, 300, 373-383, 495, and 505.

38. `DONE` -- not radial profiles, but NFW profile from fitted concentration
   The current text explicitly says these are reconstructed from catalog concentrations rather than direct particle-count radial stacks.
   Current locations: `main.tex` around lines 379 and 388.

39. `DONE` -- misleading markers/lines
   The caption states that markers do not denote individual halos and that both line and marker curves are reconstructed from catalog concentrations.
   The figure legend itself uses "mean-c NFW" and "median-c NFW", which is consistent with the caption and does not call them direct particle stacks.
   Current location: `main.tex` around line 383.

40. `DONE` -- "how accurate can NFW profile describes BT"
   The draft now explicitly states that this diagnostic does not test NFW fit residuals for BT halo particle profiles; doing so would require direct particle-profile stacks and is outside the present comparison.
   Current locations: `main.tex` around lines 374 and 383.

41. `DONE` -- add error bars
   HMF has Poisson error bars; half-mass and concentration use 16th-84th percentile scatter.
   Current locations: `main.tex` around lines 329, 365, 395, and figure captions.
   Caveat: the NFW reconstructed-profile figure may still lack uncertainty bands.

42. `DONE` -- add scatter in concentration
   Concentration figure uses 16th-84th percentile scatter, and the text now notes the substantial halo-to-halo scatter and explains that the analysis relies on median trends and quoted bin ratios rather than individual-halo concentration fits.
   Current locations: `main.tex` around lines 390 and 394.

43. `DONE` -- define D19 and I21
   The current draft avoids D19/I21 abbreviations in the main description and uses full names Diemer & Joyce (2019) and Ishiyama et al. (2021).
   Current location: `main.tex` around line 395.

44. `DONE` -- explain shaded region
   The power-spectrum caption explains the gray high-k region and the shaded band around unity.
   Current location: `main.tex` around line 434.

45. `DONE` -- change most "input matter power" to "primordial power spectrum"
   The terminology pass changes most model-level "input matter power" wording to "primordial power spectrum" / "primordial power-spectrum template", while retaining "input linear matter power spectrum at \(z_i=200\)" for actual initial-condition spectra and public data products.
   Current locations: `main.tex` around lines 151, 159-185, 225-250, 285, 326-355, 390-409, 438-460, 499, and 505.

46. `NOTE` -- "This is right."
   No action needed.

47. `DONE` -- sentences seem unnatural
   Rewrote the physical-interpretation opening with simpler wording: the results are "consistent with" a physical picture rather than pointing to a single proved picture.
   Current location: `main.tex` around line 438.

48. `DONE` -- issue is not direct
   Softened the causal chain through the primordial spectrum, initial density fluctuations, and earlier collapse; the text now uses "tend to collapse earlier" instead of a direct proof-like statement.
   Current location: `main.tex` around line 438.

49. `DONE` -- clumsy "This earlier collapse first appears..."
   Removed the clumsy phrase from the live text and replaced it with a direct high-redshift-to-late-time sequence.
   Current location: `main.tex` around line 438.

50. `DONE` -- suggested clearer wording about early density fluctuations
   Added clear wording that enhancing the small-scale primordial power spectrum raises the corresponding small-scale density fluctuations in the initial conditions.
   Current location: `main.tex` around line 438.

51. `DONE` -- unclear "rescaling of all nonlinear statistics"
   Replaced the live text with a concrete statement that the BT response varies with pivot scale, redshift, halo mass, and statistic.
   Current location: `main.tex` around line 440.

52. `DONE` -- "This is not proved?"
   Changed the live text from "supports the interpretation" to "is consistent with" a common response, avoiding proof-like wording.
   Current location: `main.tex` around line 442.

53. `DONE` -- "You meant power spectrum? Power spectrum is not field-level."
   The live text now describes the nonlinear matter power spectrum as a matter power-spectrum statistic or summary statistic, not as "field-level".
   Note: "field-level" still appears inside `\revisionreplace{new}{old}` deleted text so it remains visible as struck-through redline markup.
   Current locations: `main.tex` around lines 285, 302, 420, 429, 442, 448, 458, and 496.

54. `DONE` -- power spectrum is summary statistics
   The power-spectrum section, caption, limitations, and conclusion now frame \(P(k)\) as a summary statistic measured from the particle density field, with high-\(k\) points treated as estimator-sensitive checks rather than a calibrated fitting formula.
   Current locations: `main.tex` around lines 420, 429, 442, 458, and 496.

55. `PARTIAL` -- "It is true but strange."
   Likely about observational-connection wording. Current text is improved but still cautious and somewhat indirect.
   Current locations: `main.tex` around lines 451-471 and 506.

56. `PARTIAL` -- priority should be effect of enhanced PPS
   Current draft discusses the dark-matter response, but observational paragraphs still diffuse the priority across JWST, dwarf galaxies, lensing, and 21 cm.
   Next action: make the first priority the effect of enhanced PPS on dark matter halo statistics.

57. `PARTIAL` -- "on dark matter halo"
   The manuscript now emphasizes halo abundance, assembly, and concentration, but conclusion/observational framing can make this priority clearer.

58. `PARTIAL` -- baryonic physics etc. only at very end of conclusion
   Baryonic caveats appear in the introduction, discussion, limitations, observations, and conclusion.
   Next action: keep necessary caveats but avoid letting them dominate the main result statements.

59. `PARTIAL` -- dark matter halos are dominant effect
   Current text says the strongest responses are halo abundance, assembly, and concentrations.
   Current location: `main.tex` around line 471.
   Remaining issue: the conclusion could state this more directly.

60. `DONE` -- put response table into bullet points in conclusion
   Removed the separate response-summary table and folded its BT_deep HMF and nonlinear-power values into the conclusion bullets.
   Current location: `main.tex` around lines 475-480.

61. `DONE` -- "collects representative response amplitudes..." not clear
   Removed the live transition phrase and replaced it with the simpler "The main conclusions are as follows."
   Current location: `main.tex` around line 475.

62. `DONE` -- clumsy wording
   Same fix as comment 61: table removed and the transition sentence shortened.

63. `NOTE` -- "This is a good paragraph."
   No action needed.

64. `DONE` -- use bullet points here
   Conclusion now uses an enumerated list.
   Current location: `main.tex` around lines 497-502.

65. `PARTIAL` -- definition, not result
   The conclusion still includes an "analytic ingredients" paragraph that mixes definitions and recommendations.
   Current location: `main.tex` around line 504.
   Next action: shorten or move definition-like material out of conclusions.

66. `DONE` -- no bracket needed for all equation
   The live analytic-ingredients paragraph now uses `Eq.~\ref{...}` style. The commented old draft line was also normalized.
   Current location: `main.tex` around line 483.

67. `DONE` -- cite reference again here
   Added repeated citations in the conclusion analytic-ingredients paragraph for Reed et al. (2007), Bocquet et al. (2016), Diemer & Joyce (2019), and Ishiyama et al. (2021). The exact Overleaf anchor was unavailable, so this addresses the likely target.
   Current location: `main.tex` around line 483.

68. `DONE` -- use full name
   Live text now uses Reed et al. (2007), Bocquet et al. (2016), Diemer & Joyce (2019), and Ishiyama et al. (2021). Old shorthand remains only inside struck/deleted revision text.
   Current locations: `main.tex` around lines 326-355, 400, and 483.

69. `DONE` -- inconsistent Reed07, B16, D19
   Standardized the live notation across the HMF text, HMF captions, concentration-model equation text, and conclusion.
   Current locations: `main.tex` around lines 326-355, 400, and 483.

70. `DONE` -- need absolute clarity
   The fitting-function names are now explicit and tied to their mass definitions: Reed et al. (2007) for FOF and Bocquet et al. (2016) for \(M_{200c}\).
   Current locations: `main.tex` around lines 326 and 350.

71. `DONE` -- define consistent notation early in each section
   The HMF section and captions now avoid Reed07/B16 shorthand in the live text; the concentration section uses full Diemer & Joyce (2019) and Ishiyama et al. (2021) names.
   Current locations: `main.tex` around lines 326-355 and 390-400.

72. `DONE` -- cite reference again here
   Same fix as comment 67: citations are repeated in the conclusion analytic-ingredients paragraph. The exact Overleaf anchor was unavailable.
   Current location: `main.tex` around line 483.

73. `DONE` -- "Don't understand. You meant not using your counting halos from your project plots?"
   Anchor supplied by user: the conclusion sentence about projected maps and nonlinear-power fitting. Rewrote it to say projected maps are qualitative visualizations and should not be used to infer subhalo counts; also states that no calibrated nonlinear-power fitting formula is provided.
   Current location: `main.tex` around line 483.

74. `DONE` -- no nonlinear power fitting formula
   Current conclusion states not to adopt a standalone nonlinear-power fitting formula from this work.
   Current location: `main.tex` around line 504.

75. `DONE` -- no analytic model for nonlinear power spectrum
   Current draft says nonlinear theory curves are for orientation and no calibrated nonlinear-power fitting formula is provided.
   Current locations: `main.tex` around lines 427, 434, and 504.

76. `PARTIAL` -- mention earlier in conclusions
   Current conclusion mentions no standalone nonlinear-power fitting formula in the analytic-ingredients paragraph.
   Current location: `main.tex` around line 504.
   Remaining issue: if the professor wants this earlier in the conclusion bullets, move it into the nonlinear-power bullet.

77. `DONE` -- "It sounds strange."
   Anchor supplied by user: the conclusion sentence about resolved-range, single-realization benchmarks. Rewrote it as "These measurements are single-realization simulation benchmarks over the resolved mass and wavenumber ranges; they are not direct observational constraints."
   Current location: `main.tex` around line 485.

78. `DONE` -- one simulation, no cosmic variance
   Current limitations section says there is one matched-seed realization per model and no cosmic variance/realization-to-realization scatter.
   Current location: `main.tex` around line 461.

79. `PARTIAL` -- cannot provide direct observational constraints; mostly not cosmic variance
   Current conclusion states these are not direct observational constraints and require baryonic/selection/survey modeling.
   Current location: `main.tex` around line 506.
   Remaining issue: it should avoid implying the main barrier is box/cosmic variance for Milky-Way-scale and smaller halo statistics.

80. `OPEN` -- final sentence too weak
   The final conclusion sentence remains cautious and ends on requirements for additional modeling.
   Current location: `main.tex` around line 506.
   Next action: rewrite to a more positive future-work statement while preserving caveats.

81. `OPEN` -- give GitHub address
   Data Availability does not include a GitHub URL.
   Current location: `main.tex` around line 510.

82. `OPEN` -- consider Zenodo for halo catalogs and SOAP output
   Data Availability does not mention Zenodo or a DOI.
   Current location: `main.tex` around line 510.
   Next action: add placeholder if no DOI exists, or add final DOI/URL if available.

83. `DONE` -- full snapshots are not possible
   Data Availability says full raw snapshots and complete HBT-HERONS/SOAP catalogs are too large for the manuscript package.
   Current location: `main.tex` around line 510.

84. `DONE` -- add resolution study too
   Added Appendix `FOF Mass-Function Resolution and Volume Check` with a PL FOF HMF comparison across PL-25-1024, PL-25-512, PL-25-256, and PL-50-512 at z=0 and z=8.52.
   Current locations: `main.tex` trusted-range table/HMF section and Appendix `app:fof_hmf_resolution`.
   Reduced data/script/figure: `public_data/figure_data/fof_hmf_resolution/`, `public_data/scripts/plot_fof_hmf_resolution.py`, and `fof-hmf-resolution-volume.png`.

85. `OPEN` -- "Need to mention what theory lines are. I suppose ``halomodel''. Need to describe it in some details in the main text."
   Newly found in the live Overleaf Review panel on 2026-06-04; it was not present in the local 84-comment export.
   Current location: current-file Review panel near the nonlinear matter power-spectrum section and Fig.~\ref{fig:power_spectra_ratio_z0}.
   Current draft says "corresponding nonlinear theory curves for orientation" and "BT-theory/PL-theory ratios" but does not define what theory calculation produced those curves.
   Next action: identify the actual theory-line source from the plotting script/data products, then add a short main-text description and update the caption. Do not call it "halomodel" unless the plotted curves really come from a halo-model/Halofit calculation.

## Highest-priority open items

1. Add or explicitly defer mass-accretion-rate and resolution studies: comments 30 and 84.
2. Define the nonlinear power-spectrum theory lines: comment 85.
3. Add Data Availability links/placeholders: comments 81-83.
