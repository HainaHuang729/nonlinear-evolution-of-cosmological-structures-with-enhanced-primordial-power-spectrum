# Manuscript Revision Record

This document records requested manuscript changes and the corresponding revisions.

## 2026-10-27. Full-Manuscript Language Audit

**Source:** main.tex at commit ae359b0. Line references below refer to that version.

**Status:** Implemented at the author's request. The 32 audit items and eight overlapping terminology recommendations have been addressed. The current redline uses the changes package: removed wording is struck through in black and added wording is blue; unchanged wording remains black. The original excerpts and recommendations below document the audit against ae359b0. Numerical measurements, equations, citation keys, labels, and model names were retained. Summary statements were narrowed where the measured range or compared model set required it. The pending catalog release remains a separate task.

**Method:** Read the abstract, introduction, theory, numerical methods, results, discussion, conclusions, data availability, acknowledgments, every caption, and all appendices using academic-humanizer and the local cosmology-manuscript requirements. Commented-out revision history was excluded from prose findings. This is an editorial and internal-consistency audit, not an independent numerical reanalysis or a fresh literature survey.

**Findings:** Nine scope or method-description checks (C01--C09), twenty language-edit candidates (S01--S20), and three optional edits (O01--O03). The second pass added C08 and S15--S19; the third added C09, S20, and O03 and independently checked the statistical terminology against the plotting scripts. Scope checks should be resolved before polishing the affected statements. Not every repeated technical definition or negative statement needs removal.

### Coverage

| Part | Assessment |
| --- | --- |
| Abstract | Generally direct; clarify the redshift scope of the power-spectrum comparison. |
| Introduction | Mostly natural; one unnecessary negative opening and repeated setup descriptions. |
| Theory | Two residual uses of template; the section opener can begin with definitions. |
| Numerical methods and simulation table | Core definitions are useful; update the role of the 256-box runs and explain phase-pair averaging. |
| Projection and HMF | Projection prose is clear; remove one HMF tautology and a repeated threshold warning. |
| Half-mass assembly and MAH | Preserve the formation-time distinctions; simplify reference-model framing and one sample-description sentence. |
| Density profiles and concentration | Some duplicated result statements and empty framing remain; retain uncertainty and mass-cut definitions. |
| Matter power spectrum | The revised results paragraph is direct; the phase-pair construction still needs a methods definition. |
| Discussion and limitations | The main remaining defensive sentence repeats the stated dark-matter-only scope. |
| Conclusions | Correct the scope of the full-history comparison and state the D19 comparison selection precisely. |
| Availability and acknowledgments | Keep the verified archive status; remove the generic acknowledgment before the specific credits. |
| Numerical-range and other appendices | Most detail is necessary; review the strength of the lowest-mass resolution statement and shorten repeated scatter disclaimers. |

### C01. Update the stated role of the 256-box simulations

**Location:** main.tex:226, Simulation Suite and Terminology.

**Original:** "The 256 h^-1 Mpc PL and BT runs are used only for the nonlinear matter power spectrum."

**Issue:** The displayed power-spectrum figure, quantitative range table, and conclusion now use only the 25 h^-1 Mpc phase-pair spectra. The simulation-suite text still reads as though both boxes contribute to the current analysis.

**Proposed action:** State whether the 256-box runs remain an auxiliary numerical check or are retained only in the released historical products. Align the sentence and the table description with that verified role. Keep the simulation parameters and table rows until their intended role is confirmed.

### C02. Limit the full-history conclusion to the models actually plotted

**Location:** main.tex:602, Conclusions; compare main.tex:379 and 433.

**Original:** "The full mass-assembly histories show the same ordering."

**Issue:** This follows numerical half-mass results for three models, but the full-history figure contains only PL and BT kp=1. It cannot independently establish the three-model ordering.

**Proposed wording:** "The full mass-assembly histories also show earlier assembly in the kp=1 model than in PL (Sec. ...)."

**Preserve:** All three half-mass redshifts and their model assignments. Use the existing BT macro in the actual TeX edit.

### C03. Qualify the abstract's power-spectrum comparison by epoch

**Location:** main.tex:110; related framing at main.tex:528.

**Original:** "The nonlinear matter power spectrum changes more modestly."

**Issue:** The current results report BT/PL approximately 4.21 at z=8.52 near k=20 h Mpc^-1, compared with approximately 1.16 at z=0. The unqualified sentence does not say which epoch or halo statistic supplies the comparison.

**Proposed wording:** "The nonlinear matter power enhancement grows toward higher redshift and higher wavenumber."

**Alternative:** Retain the comparison with halo statistics only after specifying its mass, scale, and redshift. Do not introduce a universal ordering among different statistics.

### C04. Define phase-pair averaging in the methods

**Location:** main.tex:197--199, 506, and 565.

**Original:** "We use the released phase-pair-averaged spectra ..."

**Issue:** The methods describe a shared seed, while the current power-spectrum section introduces phase-pair averages without explaining the pair. The averaging procedure is a methodological fact, not optional reproducibility jargon.

**Proposed action:** Add a short definition based on the measurement metadata: identify the original and phase-inverted runs, the equal-epoch averaging rule, and the outputs to which it applies. Keep the single-realization statement explicitly scoped to the halo measurements. Do not call the pairs independent or amplitude-fixed unless that is verified.

### C05. Retain the actual D19 accuracy selection in the conclusion

**Location:** main.tex:609; compare main.tex:482.

**Original:** "In Sec. ..., for the resolved mass bins, the Diemer & Joyce (2019) relation agrees with the simulation medians within 20% ..."

**Issue:** "Resolved mass bins" is less specific than the selection used to establish this accuracy: 0.25-dex bins wholly above 1.89 x 10^9 solar masses and containing at least 20 halos. The figure also displays lower-mass points, so an unqualified reference to resolved bins can obscure the stricter accuracy test.

**Proposed action:** Lead with the result and identify the strict selection, or explicitly refer to the selection defined in the concentration subsection. Preserve the 20% result, all three models, four redshifts, and the Diemer2019 citation.

### C06. Specify which external half-mass reference uses a different mass definition

**Location:** main.tex:360.

**Original:** "The external simulations differ from all of our runs, including PL, in their background cosmologies and halo-mass definitions."

**Issue:** The same paragraph says that COCO/Hellwing16 uses FOF masses. The blanket statement about different mass definitions is broader than the preceding description supports.

**Proposed wording:** "The background cosmologies differ from ours, and BK09 uses virial rather than FOF masses. We therefore use these relations as qualitative comparisons with PL."

**Preserve:** The two source citations, their stated methods, and the restriction to comparisons with PL. The next sentence need not repeat that these are not BT predictions once this scope is clear.

### C07. Check the strength of the lowest-mass resolution claim

**Location:** main.tex:694; compare main.tex:318 and 688--692.

**Original:** "The fiducial 1024^3 HMF has substantial resolution margin above 10^8 solar masses."

**Issue:** "Substantial resolution margin" is vague and reassuring. The lower-resolution numerical comparisons quoted in this appendix start at higher masses, for example 10^8.92 solar masses for the 512^3 run. They do not directly demonstrate convergence at the adopted 10^8-solar-mass threshold.

**Proposed action:** Distinguish the approximately 50-particle catalog threshold from the mass ranges over which cross-resolution agreement has been tested. Keep every measured ratio and mass interval. Do not replace this sentence with a stronger claim of convergence without additional evidence.

### C08. Restrict the earlier-assembly statement to low-mass halos

**Location:** main.tex:364--366.

**Original:** "At fixed final mass, halos in both blue-tilted models form earlier than PL halos, with the largest shift in ..."

**Issue:** The next paragraph gives z_1/2 = 1.43, 1.78, and 1.39 for PL, BT kp=1, and BT kp=10 near a final mass of 2.0 x 10^11 solar masses. The kp=10 value is slightly lower than PL, so the opening is not a valid statement for every mass bin. This small difference should not be called statistically significant without an appropriate test.

**Proposed wording:** "At low final halo masses, both BT models assemble earlier than PL, with the largest shift in BT kp=1."

**Preserve:** All quoted half-mass redshifts and mass bins. This change narrows the summary to the range where the stated ordering is observed; it does not change the measurements.

### C09. State how the half-mass crossing redshift is interpolated

**Location:** main.tex:356 and 371.

**Original:** "We assign z_1/2 when two consecutive snapshots lie on opposite sides of M0/2."

**Source check:** zhalf_raw_adjacent in public_data/scripts/plot_same_trackid_no_envelope_allmodels.py selects the first valid increasing-mass crossing and linearly interpolates the crossing redshift between the two recorded masses. It does not just assign either snapshot's redshift or fill a missing snapshot.

**Proposed wording:** "We determine z_1/2 by linear interpolation between the first pair of consecutive snapshots in which the recorded FOF mass increases through M0/2."

**Reason:** Specify the measured quantity in ordinary numerical-cosmology language. Preserve the existing mass correction, tracking selection, and rule against filling missing snapshots. This is clarification of the existing calculation, not a request to recompute it.

### S01. Correct the power-spectrum interval's subject--verb agreement

**Location:** main.tex:571.

**Original:** "The power-spectrum interval used for quantitative interpretation are ..."

**Proposed wording:** "The power-spectrum interval used for quantitative interpretation is ..."

**Reason:** Direct grammar correction. This mismatch was introduced when the two-box wording was shortened in the preceding revision.

### S02. Replace the two remaining uses of template

**Location:** main.tex:142.

**Original excerpts:** "primordial power-spectrum templates"; "a PL or BT template".

**Proposed wording:** "primordial power-spectrum models"; "a PL or BT model".

**Reason:** Restore the established terminology preference. No model definition changes.

### S03. Start the early-universe model paragraph with the adopted approach

**Location:** main.tex:126.

**Original:** "We do not model these mechanisms explicitly. Instead, we use broken-power-law blue-tilted spectra as examples for testing how enhanced small-scale primordial power changes nonlinear structure formation."

**Proposed wording:** "We use broken-power-law blue-tilted spectra to study how enhanced small-scale primordial power changes nonlinear structure formation."

**Reason:** The surrounding paragraphs already distinguish possible early-universe mechanisms from the adopted PL/BT models. Keep the following definition of BT and every attached citation.

### S04. Open the theory section with the terminology it defines

**Location:** main.tex:142.

**Original:** "We define ... We also relate ... Throughout the paper ..."

**Proposed action:** Remove the two roadmap sentences and begin with the existing definitions of primordial and input linear matter power spectra. Apply S02 to those definitions. The pivot-mass calculation is already introduced immediately before its equation.

**Reason:** The section headings and equations provide the structure; the opening can deliver information directly. Keep the transfer-function, normalization, and zi=200 distinction.

### S05. Remove the repeated initial-redshift sentence from the input-spectrum caption

**Location:** main.tex:206.

**Original:** "The spectra are evaluated at the initial redshift, zi=200."

**Proposed action:** Delete this sentence only. The caption already opens with "Input linear matter power spectra at zi=200 ...".

**Reason:** Remove a literal repetition while retaining the value in the caption's first sentence.

### S06. Consolidate the adjacent simulation-suite setup descriptions

**Location:** main.tex:224--226.

**Original:** One paragraph lists matching numerical settings and initial phases; the next again introduces three matching 25 h^-1 Mpc, 1024^3 runs.

**Proposed action:** Introduce the three runs and their common settings once. Retain the two BT parameter definitions because this subsection should be readable independently. Resolve C01 before describing auxiliary runs.

**Reason:** Reduce repetition within a single subsection. The initial-condition explanation and standalone table caption can still state the shared phases where useful.

### S07. Delete the HMF paragraph's explanation of what its points and ratios mean

**Location:** main.tex:322.

**Original:** "The simulation points are the measured nonlinear abundances, and the BT/PL ratios quantify changes relative to PL."

**Proposed action:** Delete this sentence. Retain the preceding Reed07 prescription, its citation, and the model-specific input spectra.

**Reason:** The measurement procedure and figure already define the plotted points and ratios.

### S08. Remove the second statement of the same HMF lower cut

**Location:** main.tex:328; compare main.tex:318.

**Original:** "This interpretation is restricted to the bins above the plotted catalog cut, M_FOF >= 10^8 solar masses."

**Proposed action:** Delete this closing sentence while retaining the explicit adopted cut at the beginning of the subsection and in the figure caption.

**Reason:** Keep the numerical limit where the sample is defined instead of repeating it as a warning after the results.

### S09. Describe the MAH sample without an ambiguous adjective or filler justification

**Location:** main.tex:379.

**Original excerpts:** "the central final FOF mass of a selection window"; "For simplicity, we only consider the PL and ... models."

**Proposed wording:** "the final FOF mass at the center of a selection window"; "This comparison includes PL and BT kp=1."

**Reason:** "Central" can be confused with central-halo status, and "for simplicity" gives no methodological explanation. Preserve the six window centers, 0.1-dex selection, tracking method, and actual model scope.

### S10. Remove a repeated non-fitting disclaimer from the MAH caption

**Location:** main.tex:433; compare main.tex:412.

**Original:** "The analytic curves are not fitted to the plotted histories."

**Proposed action:** Delete this caption sentence. The caption already identifies published parameter relations, and the text explicitly states that the parameters are not fitted to these simulations.

**Reason:** The origin of the curves is clear from the positive description. Retain the one explicit methodological statement in the text.

### S11. Merge repeated radial-profile trends

**Location:** main.tex:454.

**Original:** "The BT models differ most from PL in the resolved inner profiles. ... The lower ratio panels show that the ... enhancement is strongest ... while ... remains closer to PL."

**Proposed wording:** "The largest resolved inner-density enhancement occurs in BT kp=1, particularly in the low- and intermediate-mass bins. BT kp=10 remains closer to PL, and both enhancements weaken toward larger r/R200m."

**Reason:** The paragraph states the same model ordering twice. Preserve the mass dependence, radial dependence, resolved-radius qualifier, and model notation.

### S12. Remove two empty concentration-result framing sentences

**Location:** main.tex:474.

**Original:** "The measured medians vary with mass and redshift." / "We therefore compare the models using binned medians and percentile ranges."

**Proposed action:** Begin directly with the existing z=0 concentration ratios. Retain the following statement about low-mass halo-to-halo scatter. Remove the closing sentence, since the preceding methods paragraph already defines the binned medians and percentiles.

**Reason:** The actual numbers and scatter are the content; the framing adds no new result.

### S13. Delete the repeated instruction on how readers should interpret the simulations

**Location:** main.tex:563.

**Original:** "The results should therefore be interpreted as predictions for the underlying dark matter distribution, not as direct predictions for observed galaxies or lensing samples without further modeling."

**Proposed action:** Delete this standalone sentence. Keep the preceding list of omitted gas, stellar, AGN, and reionization processes and their effects. Keep the galaxy-formation requirement in the observations subsection.

**Reason:** The scope is already explicit. This is the clearest remaining repeated defensive statement.

### S14. Remove the generic acknowledgment before the specific credits

**Location:** main.tex:628.

**Original:** "The authors acknowledge the computational resources and software infrastructure used to carry out the simulations and analyses presented in this work."

**Proposed action:** Delete this sentence only. Keep every software citation, version, funding statement, institution, and named acknowledgment below it.

**Reason:** The following paragraphs already supply the specific credits.

### S15. Specify the shared normalization target

**Location:** main.tex:142 and 159; compare main.tex:197 and 206.

**Original excerpts:** "the common normalization"; "The transfer function and common normalization are applied ..."

**Issue:** The initial-condition methods correctly describe a common sigma8 target reached through small model-dependent global factors. "Common normalization" alone can be read as the same amplitude factor for all spectra.

**Proposed wording:** "normalization to the common sigma8 target".

**Preserve:** The shared target sigma8 = 0.8111 and the model-dependent normalization factors. Keep the distinction between the primordial spectrum and the linear matter spectrum at zi = 200.

### S16. Name the dimensionless power instead of an input value

**Location:** main.tex:201.

**Original:** "The largest BT input value over this range is ..."

**Proposed wording:** "The largest dimensionless linear power over this range is Delta squared(k, zi) approximately 5.8 x 10^-5 for BT kp=1."

**Reason:** The sentence refers to a defined physical quantity, not a generic software input. Keep the original mathematical notation, number, redshift, and restriction to the stated wavenumber range in the TeX revision.

### S17. Separate sparse-bin deviations from an asserted cause

**Location:** main.tex:346.

**Original:** "Individual high-mass bins show larger deviations because they contain fewer halos."

**Proposed wording:** "Larger deviations occur in sparsely populated high-mass bins."

**Reason:** This states the observed association directly. Fewer halos increase counting uncertainty, but this alone does not identify the cause of every simulation-to-model residual. A stronger causal explanation should be retained only with supporting analysis. No error bar or quoted residual is changed.

### S18. Describe evaluation of the B16 mass function directly

**Location:** main.tex:342.

**Original:** "The analytic curves use the Bocquet et al. (2016) M200c halo mass function ... given the PL, ... linear matter power spectra."

**Proposed wording:** "We evaluate the Bocquet et al. (2016) M200c mass function using the linear matter power spectrum of each PL or BT model."

**Reason:** This is a direct description of an analytic calculation. Keep the Bocquet2016 citation, the M200c definition, and all sample cuts in the preceding sentence. Do not call this training, optimization, or model performance.

### S19. Identify the high-mass trend in the concentration appendix

**Location:** main.tex:712.

**Original:** "The I21 and D19 predictions show a similar trend."

**Proposed wording:** "The I21 and D19 predictions also show an upturn at high mass."

**Reason:** "A similar trend" has an uncertain antecedent after sentences about rising simulated concentrations, declining L16 concentrations, and small halo counts. State which curve behavior is meant. Retain the warning about the sparsely populated highest-mass bins and the restriction to z = 8.52.

### S20. Replace a stacked noun phrase in the radial-profile caption

**Location:** main.tex:459.

**Original:** "Direct particle radial density profiles ..."

**Proposed wording:** "Spherically averaged halo density profiles measured from simulation particles ..."

**Reason:** Name the physical measurement and geometry rather than stacking implementation-oriented modifiers. The method already specifies spherical shells. Keep the model names, M200m bins, bootstrap intervals, and convergence-radius definition in the rest of the caption.

### O01. Describe concentration scatter positively in the three captions

**Location:** main.tex:500, 717, and 724.

**Original excerpts:** "not model uncertainty"; "not model-uncertainty bands".

**Proposed wording:** "The lower row shows the halo-to-halo scatter of log10 c in each mass bin."

**Decision:** Optional caption compression. Keep the precise percentile formula, units, and distinction between scatter and bootstrap uncertainty. If a reader could otherwise confuse the quantities, retain one clear explanatory sentence in the main text.

### O02. Reduce repeated adversarial contrasts in the previous-work subsection

**Location:** main.tex:536 and 540.

**Original excerpts:** "We instead measure ... without refitting ..."; "We instead analyze ... rather than only around ...".

**Proposed approach:** Describe what each previous study measured, then state the present contribution positively: "Our periodic-box simulations measure halo abundance and structure across the simulation volume." Retain the actual difference from host-centered zoom-in studies, the comparisons with analytic prescriptions, and every citation.

**Decision:** Optional tone edit. The literature comparisons themselves are relevant and should remain; contrasts are not automatically a writing defect.

### O03. Give local mass ranges rather than one universal definition of low mass

**Location:** main.tex:110, 454, 474, and 606.

**Issue:** The concentration enhancement is quoted in M200c = 10^9--10^9.5 solar-mass bins, while the direct density-profile figure uses M200m bins centered on 10^10--10^11.5 solar masses. These are different measurements and mass definitions. A universal replacement of every low-mass phrase by a cutoff of 10^10 solar masses would misdescribe part of the profile sample.

**Proposed action:** Use the applicable mass definition and measured range at the first discussion of each result. In the profile paragraph, refer to the lower-mass bins of that figure when that is what is meant. In the conclusion, distinguish the resolved inner-density result from the concentration result instead of implying that both were measured in the same low-mass bin. Keep the abstract qualitative unless a specific verified range is selected.

**Decision:** Optional clarification of the summary, not a new halo classification or a change in the reported data.

### Third-Pass Checks That Do Not Require a Correction

- **Half-mass redshift:** The plotting script and released fields distinguish the mean zhalf, the median, and the 16th--84th percentile interval. The current caption correctly describes a mean and halo-to-halo range. Do not relabel those bars as uncertainty on the mean.
- **Concentration:** plot_simulation in concentration_qc_kp10.py plots logc_median, with percentile offsets in log10 c, and labels the vertical axis log10(c200c). The manuscript's statement that these points show the median log10 c is correct. The residual calculation converts these values back to c before forming the simulation-to-prediction ratio.
- **Radial profiles:** The released profile table labels its interval columns as bootstrap percentiles of the median density. This supports the caption's distinction between uncertainty on a median profile and halo-to-halo concentration scatter. Do not use a single generic error description for both figures.
- **Filter and bin terminology:** A spherical top-hat filter is a physical smoothing operation, whereas a mass-selection window or a mass bin defines a sample. Window is not inherently computer jargon; any replacement must keep these meanings distinct.

### Wording and qualifications to retain

- The model-specific use of primordial power spectrum and enhanced small-scale power is accurate; no global synonym replacement is proposed.
- The distinction between the primordial spectrum and the input linear matter spectrum is necessary.
- The initial-condition linearity check does not establish nonlinear convergence. That qualification should remain.
- The FOF, M200c, and M200m definitions, different centering choices, particle thresholds, and concentration selection must remain distinct.
- The Correa formation parameter is not the measured half-mass redshift. The new distinction should remain.
- The sigma definition and the stated origin of q and a are useful; they should not be shortened merely because they are technical.
- The 90 per cent MAH completeness statement, the strict D19 accuracy selection, and the small high-mass sample warning affect interpretation and should remain.
- Phase-pair averaging does not establish box-size convergence. Keep the methodological limitation without repeating it in every result paragraph.
- The Maccio comparison requires its mass-definition and scatter-estimator qualifier.
- The current Zenodo archive does not contain the catalog. Keep the accurate availability statement until the release changes.
- Existing numerical results in the Results and Conclusions are intentionally repeated for different reading contexts; no wholesale deletion of conclusion numbers is proposed.

### Original Review Order and Implementation Authorization

The audit originally proposed resolving C01--C09 before applying S01--S20 and O01--O03. The author subsequently requested that the complete set be applied and marked blue. That request superseded the earlier one-item-at-a-time workflow for this pass.

### Terminology Addendum: Prefer Physics and Cosmology Usage

The author's additional requirement is to reduce terminology borrowed from software engineering and machine learning and use the conventional vocabulary of physics and cosmology. This requirement has also been added to the local academic-humanizer reference. The eight candidates below supplement the 32 audit findings and have now been applied to main.tex. The two uses of template were addressed under S02.

| ID | Location | Current wording | Suggested wording or action |
| --- | --- | --- | --- |
| T01 | main.tex:110 and 206 | dark-matter baseline; standard power-law baseline | dark-matter-only simulation results; standard power-law reference spectrum. Choose the expression matching the object being described. |
| T02 | main.tex:197 | modify the transfer-function plugin | Describe the modification to the transfer function above kp. Keep the plugin implementation details in methods documentation where needed for reproduction. |
| T03 | main.tex:540 | population-level trends across halo mass | halo statistics as functions of mass across the simulation volume. Do not replace this with field-halo statistics unless the halo selection supports that restriction. |
| T04 | main.tex:482 | For the strict comparison | For the comparison with D19. Retain the full particle-count and mass-bin selection immediately afterward. |
| T05 | main.tex:500 | the model-accuracy statement in the text | the quoted agreement with D19. This states the actual comparison rather than sounding like a model-evaluation score. |
| T06 | main.tex:644 and 651 | Numerical Interpretation Ranges; adopted numerical interpretation ranges | Numerical Limits; mass, redshift, and wavenumber ranges used for the comparisons. Preserve the existing labels and all numerical limits. |
| T07 | main.tex:506 | released phase-pair-averaged spectra | phase-pair-averaged spectra. Explain their physical and statistical construction in the methods; describe their release in Data Availability. |
| T08 | main.tex:199 | uncertainty associated with the particular random realization | sample variance in the PL--BT comparison. Keep the statement that the shared phases reduce this contribution; do not imply that cosmic variance is eliminated or that a variance estimate has been measured from independent realizations. |

**Retain conventional technical terms:** Extended Press--Schechter formalism, analytic prescriptions, fitting functions, calibration, mass-accretion histories, halo-to-halo scatter, covariance, power-spectrum estimators, transfer functions, mesh assignment, shot noise, window functions, and Nyquist wavenumbers are normal scientific or numerical-cosmology terminology. They should not be removed solely because they also appear in computing. The distinction between an initial linear matter spectrum and a primordial spectrum must remain explicit.

**Editorial criterion:** Name the physical quantity, numerical method, or measured difference. Do not replace a familiar scientific term with an unusual synonym merely to avoid repetition. For example, enhanced primordial power remains enhanced primordial power, not improved power. Preserve model names, equations, units, citations, and conclusions.

## 2026-10-27. Full-Audit Implementation Record

| Items | Revision made |
| --- | --- |
| C01 | The simulation-suite description now identifies the 256-box spectra as auxiliary released data and the 25-box runs as the source of the displayed power-spectrum comparison. The table rows and numerical parameters were retained. |
| C02 | The full-history conclusion now compares only PL and BT kp=1. The three-model half-mass-redshift results remain unchanged. |
| C03 | The abstract now states the redshift and wavenumber dependence of the power enhancement. The Discussion no longer assumes that its fractional amplitude is universally smaller than the halo-statistic changes. |
| C04 | The initial-condition methods now define a phase pair and the arithmetic averaging of equal-epoch power spectra before taking BT/PL. The halo measurements remain explicitly scoped to the original simulations. This wording follows the released phase-pair measurement metadata and does not assume amplitude fixing or independent realizations. |
| C05 | The conclusion now states the D19 selection: 0.25-dex bins lying wholly above 1.89 x 10^9 solar masses and containing at least 20 halos. The 20 per cent result is unchanged. |
| C06 | The BK09 virial-mass difference is stated separately from the shared background-cosmology differences. The external relations remain qualitative PL comparisons. |
| C07 | The approximately 50-particle catalog threshold is distinguished from the higher mass intervals covered by cross-resolution comparisons. No new convergence claim or numerical analysis was introduced. |
| C08 | The earlier-assembly summary is restricted to low final halo masses. All quoted half-mass redshifts, including the high-mass kp=10 value, are unchanged. |
| C09 | The half-mass method and caption now state the linear interpolation at the first increasing-mass crossing between consecutive snapshots, matching the existing calculation. |
| S01 | Corrected the singular power-spectrum interval to use is. |
| S02, S04 | Replaced both template occurrences with model and opened the theory section with its physical definitions. |
| S03 | Replaced the negative early-universe-model opener with the adopted broken-power-law approach. |
| S05, S06 | Removed the repeated initial-redshift caption sentence and consolidated the simulation-suite setup. |
| S07, S08 | Removed the HMF point/ratio tautology and the repeated closing mass-cut warning. The sample definition and caption retain the threshold. |
| S09 | Clarified that M0 is the mass at the center of a selection window and removed for simplicity from the PL/kp=1 sample description. |
| S10 | Removed the repeated non-fitting disclaimer from the MAH caption. The origin of the parameters remains explicit in the text. |
| S11, S20 | Condensed the radial-profile trends and described the plotted quantity as spherically averaged halo density profiles measured from simulation particles. |
| S12 | Removed the empty concentration-result framing sentences while retaining every ratio and scatter statement. |
| S13 | Removed the repeated instruction that the simulations are not direct galaxy or lensing predictions. The omitted physical processes and observational modeling requirement remain stated. |
| S14 | Removed the generic acknowledgment while retaining specific credits, software versions, citations, funding, and names. |
| S15, S16 | Named the common sigma8 target and dimensionless linear power explicitly. |
| S17, S18 | Described sparse-bin residuals without assigning an untested sole cause, and stated directly how the B16 mass function is evaluated. |
| S19 | Specified that the I21 and D19 high-mass concentration predictions turn upward. The sparse-bin qualification remains. |
| O01 | Concentration captions now describe halo-to-halo scatter positively instead of repeatedly contrasting it with model uncertainty. |
| O02 | Previous-work comparisons now state the present periodic-box contribution directly, retaining all cited studies and their methods. |
| O03 | The radial-profile text identifies its M200m sample, and the conclusion separates the resolved inner-profile result from the low-mass concentration result. No universal low-mass cutoff was imposed. |
| T01--T08 | Replaced generic baseline, plugin, population-level, strict-comparison, model-accuracy, and release-oriented phrasing at the audited locations. The appendix is titled Numerical Limits; the initial-phase comparison uses sample variance. Exact software names and established numerical-cosmology terms remain. |

The changes use blue paragraph or caption text rather than recoloring historical revisions. Deleted filler sentences are documented by the original audit excerpts above. Figures, data tables, scripts, bibliography entries, labels, and simulation models were not changed in this pass. The remaining active catalog-release comment is retained.

**Validation:** LaTeX compilation completed successfully with 23 pages. All 44 labels and all 106 citation-key occurrences were preserved, including their occurrence counts. No original numeric token was lost. The final log contains no undefined citations, undefined references, overfull boxes, or PDF-bookmark token errors. Forty revised text regions use the new blue macro. All 23 PDF pages were rendered and checked in a contact sheet, with the abstract and conclusion also inspected at full-page resolution; blue revised text and black unchanged text render correctly. Existing underfull-box and REVTeX float-placement warnings remain. No data analysis or figure regeneration was performed, and no changes have been pushed.

## 2026-10-27. Review of comments still visible in the manuscript

The local branch was fast-forwarded to GitHub main at `ece6392`. The five comments below are active LaTeX comments displayed in the manuscript; commented-out historical requests are not counted as unresolved requests. Earlier status summaries below describe earlier revision rounds.

| Order | Location | Comment | Current status and next action |
| --- | --- | --- | --- |
| 1 | Median Mass-Assembly Histories | Check the half-mass condition and explain how q and a are obtained. | Addressed in this pass: distinguish the Correa formation definition from the measured half-mass redshift; retain the published q relation and background-dependent a. |
| 2 | Median Mass-Assembly Histories | Define sigma. | Addressed: define S(M) and sigma(M) immediately after the f(M0) equation, separately from the q and a discussion. |
| 3 | Mass-assembly-history figure caption | Explain or remove the shading at z > 6. | Addressed: the current image and script contain no high-redshift shading; the obsolete visible comment has been removed. |
| 4 | Nonlinear matter power-spectrum figure | Understand the small-box power-spectrum deviation. | Revised scope at the author's request: show simulation spectra and BT/PL only, with a short finite-box statement. No unique cause of the absolute-spectrum offset is claimed. |
| 5 | Data Availability | Add a user-friendly README and requirements file; release six-snapshot catalogs on Zenodo. | Partly addressed: README and dependency files are present; the published v1.0.0 archive contains no HDF5 catalog. Catalog and complete-input publication remain pending, and the visible comment is retained. |

### Item 1: distinguish the Correa formation redshift from the half-mass redshift

**Comment:** Check M(zf) = M0/2 and state clearly how q and a are derived.

**Revision:** Added an explicit statement that Correa's formation parameter is defined by M(tilde z_f) = M0/q, whereas the measured half-mass redshift uses M(z_1/2) = M0/2. The calculation uses the published mass-dependent q and tilde z_f relations rather than imposing a half-mass condition. The existing explanation of a from the normalized linear growth factor, including a = 0.292 for the adopted background cosmology, is retained. The resolved visible comment was removed.

**Verification:** Checked Section 2.3, equations (14) and (17)--(21), of Correa et al. (2015), [Paper I](https://arxiv.org/html/1409.5228v2). The plotting script reads the published-relation curve tables; the older half-mass-closure tables are not used for the current figure. No curve, measurement, or quoted numerical result was changed.

### Item 2: define sigma next to the variance formula

**Comment:** What is sigma?

**Revision:** Moved the definition immediately after the equation containing S(M0/q) - S(M0). The text identifies S(M) = sigma squared as the variance of the present-day linear density contrast smoothed with a spherical top-hat filter, and sigma(M) as its root-mean-square value. It also identifies the smoothing mass and the model-specific linear matter power spectrum used in the calculation. The published q relations and the explanation of a now form a separate discussion. The resolved visible comment was removed. No calculation or numerical value was changed.

### Item 3: verify removal of the high-redshift shading

**Comment:** Check why z > 6 is shaded and whether the shading is justified.

**Revision:** Inspected the current mass-assembly-history image and its plotting script. None of the three panels contains high-redshift shading, and the caption does not describe any. Removed the obsolete visible comment. The text still uses z <= 6 for quantitative comparisons because more than 90 per cent of each selected sample is identified there. This sample-selection condition is separate from a resolution boundary. No image or data was changed.

### Item 4: focus the power-spectrum comparison on BT/PL

**Comment:** Understand the deviation of the small-box power spectrum.

**Author's direction:** Use the simulation-only figure without HMcode. Describe the differences between BT and PL and mention finite box size briefly.

**Revision:** Replaced the displayed figure with the released 25 h^-1 Mpc phase-pair spectra and BT/PL ratios. Removed the HMcode implementation and residual discussion from the main text and conclusion, along with the detailed comparison of absolute spectra from the two boxes. A single sentence explains that a finite box excludes long-wavelength modes and can shift the absolute power. It does not identify this as the demonstrated sole cause of the earlier offset. The finite-mode equation and its citation were retained in the numerical-range appendix as a diagnostic.

**Data consistency:** The new ratios table gives BT(kp=1)/PL = 1.04784, 1.10605, and 1.15520 at z = 0 near k = 5, 10, and 20 h Mpc^-1. The text now rounds these to 1.05, 1.11, and 1.16 instead of the earlier single-measurement values 1.06, 1.10, and 1.17. At z = 8.52 the ratio near k = 20 h Mpc^-1 is 4.20539, reported as approximately 4.21. These are updates to the displayed measurement product, not changes to the simulation models or the direction of the result. The displayed wavenumber interval is approximately 2.51--32.2 h Mpc^-1, matching the new figure and metadata. The numerical-range table and conclusion were updated accordingly.

**Figure and reproduction:** The supplied simulation-only plot clipped the high-redshift ratio because its vertical limit was 2 while the data reach approximately 5. The plotting script now chooses a limit that includes the full ratio range, uses the manuscript's BT notation, and reads the released CSV files through relative paths. It writes power-spectrum-btpl.png; the all-figure reproduction command now invokes this script. No spectrum or ratio values were altered. Historical HMcode figures and data remain in the release.

**Validation:** Regenerated the figure from a separate working directory; its SHA-256 matches the manuscript image. The plot reports no overlapping labels, and visual inspection confirms that the high-redshift ratios are no longer clipped. The edited Python files pass syntax checks. The manuscript compiles to 23 pages without undefined references, undefined citations, or overfull boxes. The complete all-figure regeneration and catalog-release build were not rerun in this pass.

### Item 5: verify the public release and correct its stated scope

**Comment:** Make GitHub easier to use, add requirements and a README, and publish six-snapshot catalogs on Zenodo.

**Verified:** The root README and requirements file exist. The root requirements file points to the six maintained figure dependencies. The current power-spectrum script runs directly from the released CSV tables. The Zenodo record is published, but its only file is a 37,259,793-byte GitHub v1.0.0 source ZIP corresponding to commit bb7891e. Its central directory contains 122 entries and no HDF5 catalog, clean projection input, radial cache, or project Colossus source. The GitHub tag and local input checks independently confirm those omissions. Metadata was checked through the [Zenodo record API](https://zenodo.org/api/records/22007478), and the archive directory was inspected using an HTTP range request.

**Revision:** Corrected Data Availability and the READMEs to distinguish the current GitHub data from the archived v1.0.0 snapshot. Removed the unsupported statement that the Zenodo archive already contains the compact per-halo catalog. The quick start now gives a working command for the current power-spectrum figure and identifies the extra inputs required for the all-figure command. The catalog and complete-package documentation now state that publication remains pending. Existing extraction and validation results are retained as historical records of the prepared catalog.

**Pending:** Publish the nine prepared HDF5 catalog files, their checksum manifest, the clean projection inputs, radial bootstrap caches, and project Colossus source in a complete release. The release should also include the current phase-pair power-spectrum tables and scripts. After publication, verify the uploaded archive and update the manuscript DOI and availability text. This pass did not upload or modify the Zenodo record. The active comment remains in the manuscript.

### Editorial preferences applied in this review

The local academic-humanizer skill now includes manuscript-specific terminology and editing requirements. In item 1, the repeated explanation that a half-mass condition is not imposed was shortened to a direct distinction between the Correa formation parameter and the measured half-mass redshift. All values, equations, and citation keys were retained. Revision text follows the manuscript's existing black-text configuration.

## Current Status

- Thirty-nine requested revisions have been addressed. The EPS foundations, concentration scatter, HMcode2020 implementation, L16 high-mass limitation, final prose-consistency pass, symbol-definition audit, mass-assembly-history updates, and GitHub/Zenodo release documentation are now recorded.
- One TK follow-up comment from 2026-08-24 remains under review: the small-box power-spectrum deviation.
- The current Correa-response edits remain marked as the active revision; previously confirmed edits are unchanged.
- The Reed07 and B16 comparison rows use relative differences with row-specific symmetric-logarithmic limits.
- On 2026-07-15, the main-text adjacent-snapshot accretion-rate figure and the appendix FOF-$\Gamma$ figure were replaced by the full median FOF mass-assembly-history comparison described below.
- The numerical-methods section now defines $R_{200c}$, $\rho_{\rm crit}(z)$, and $M_{200c}$ explicitly.
- The Power et al. (2003) citation and explanation of the convergence parameter have been added; the original comments remain visible only for final confirmation.
- On 2026-08-19, the unsupported \(V_{\max}\)--\(R_{\max}\) summary was removed because its original figure, calculation script, and source table are no longer part of the manuscript or reproducibility package.
- On 2026-08-19, the initial-spectrum caption was corrected to describe the affected range as resolved wavenumbers rather than mildly nonlinear modes, consistent with the stated linearity at \(z_i=200\).
- On 2026-08-19, the projection-results paragraph was simplified to state directly that the small-scale contrast is strongest for \BTKPone{} at high redshift and becomes less visible toward \(z=0\).
- The language revisions do not change the simulation models.

## 27. Prepare a space-efficient public halo catalog

- **Location:** Public data release
- **Status:** Completed; catalog extracted and validated on 2026-07-23

Prepare an article-specific catalog instead of uploading complete FOF, SOAP, HBT-HERONS, or particle outputs. Preserve the existing reduced `public_data` package first. Then prioritize the FOF mass-function source masses, same-TrackId FOF assembly histories, the SOAP fields used for the (M_{200c}) mass function and concentration relation, and metadata for the halos selected for direct radial profiles. Do not include SOAP membership files or full particle snapshots unless substantially more storage becomes available.

The final release contains nine compressed HDF5 files totaling 74.2 MiB. It
includes individual FOF groups for the six mass-function snapshots; the SOAP
`M200c`, `c200c`, particle-count, central-status, and `TrackId` fields used by
the mass-function and concentration analyses; full same-`TrackId` raw FOF
histories for the PL and \(k_p=1\) BT assembly samples; and metadata for the
1,198 halos selected for direct radial profiles. Full snapshots, SOAP
membership files, and complete HBT-HERONS and SOAP catalogs remain excluded.

The extraction ran as Slurm job `1973235`. Independent validation reproduced
540 published FOF mass-function points, the selections for 3,183,867 `M200c`
rows, 336 mass-bin/snapshot assembly-history medians, and all 1,198 radial
selections. SHA-256 checks passed for every catalog file. The extraction,
Slurm, and validation scripts, the expected checksum manifest, and the schema
documentation are recorded under `public_data/`. The HDF5 files remain in the
separate release staging directory and are not added to the manuscript Git
repository.

## 2026-07-22. Compare with previous BT studies in the Discussion

- **Location:** Discussion
- **Status:** Completed; see item 21

Add a focused comparison between the present simulation results and previous studies of enhanced or blue-tilted small-scale primordial power. The comparison should distinguish agreements and differences in the adopted primordial spectrum, simulation setup, halo definition, redshift range, mass range, and reported halo response.

Search specifically for studies that use the halo mass function to investigate blue-tilted or enhanced-small-scale-power models. Verify that each candidate paper is genuinely relevant before adding it. Summarize how its halo-abundance result compares with the PL--BT trends measured here, and avoid citing papers that discuss related models without measuring or predicting a halo mass function.

A focused comparison has now been added to the Relation to Previous Work subsection. The cited halo mass-function and zoom-in studies were checked against their journal or arXiv records before the revision. Item 21 records the paper-by-paper classification and the resulting manuscript changes.

## 2026-07-22. Shorten the title

- **Location:** Manuscript title
- **Status:** Completed

The title was shortened from `Enhanced Small-Scale Primordial Power and the Nonlinear Formation of Dark Matter Halos` to `Dark Matter Halo Formation with Enhanced Small-Scale Primordial Power`. The revised title states the research subject first and removes the longer phrase "the nonlinear formation of."

## 2026-07-22. Shorten the abstract

- **Location:** Abstract
- **Status:** Completed

The abstract was reduced to a single paragraph. Detailed numerical values were removed, while the simulation design, measured statistics, main physical trends, comparison with published prescriptions, and scope of the dark-matter-only results were retained.

## 2026-07-15. Quantify agreement between published prescriptions and simulations

- **Location:** Halo mass function, median mass-assembly histories, concentration--mass relation, and conclusions
- **Status:** Completed; the original comment remains visible for confirmation

### Requested change

> This paragraph is important, but it sounds odd. Especially, how good the fitting compared to simulations?

### Revision made

The revised text now reports the simulation-to-model agreement directly. For mass bins above the adopted limits with at least 20 halos, the median HMF residual is within 8 per cent of both the Reed et al. (2007) and Bocquet et al. (2016) prescriptions at $z=0$ and $z=3.44$. The median differences increase to 2--22 per cent for Reed et al. and 16--32 per cent for Bocquet et al. at $z=8.52$.

At $z=0$ and $10^9\le M_{200c}/M_\odot<10^{9.5}$, the median $c_{\rm sim}/c_{\rm I21,fit}$ ratios are 0.96, 1.38, and 1.12 for PL, $k_p=1$, and $k_p=10$, respectively. The Correa histories differ from the simulated median histories by at most 46 per cent for PL and 9 per cent for $k_p=1$ over $10^9\le M_0/M_\odot\le10^{11}$ at $z=1,2,4,6$. The conclusion now summarizes these quantitative residuals and states that the published prescriptions are reference models rather than refitted BT formulae.

## 2026-07-15. Replace the accretion-rate section with full mass-assembly histories

- **Location:** Main-text assembly section, Fig. `fig:mass_assembly_history_correa`, conclusions, numerical-range table, and data-availability statement
- **Status:** Completed

The previous main-text $M_{200c}$ adjacent-snapshot accretion-rate figure and the final appendix FOF-$\Gamma$ figure are no longer referenced by the manuscript. They are replaced by `mass-assembly-history-correa.png`.

The new figure selects halos in seven Warren-corrected $z=0$ FOF mass windows and follows each halo through its persistent HBT-HERONS `TrackId`. Each point is the median positive recorded FOF mass among selected halos detected at that snapshot. Missing detections are not filled, and no cumulative-maximum filter is applied. Quantitative interpretation is restricted to $M_0\ge10^9\,M_\odot$ and $z\le6$, where more than 90 per cent of each selected sample is detected.

The BT histories in this figure use only the $k_p=1\,h\,{\rm Mpc}^{-1}$, $m_s=1.5$ simulation. The text and caption state this explicitly. The three-model assembly ranking continues to come from the half-mass-redshift figure.

The analytic comparison uses the Correa et al. (2015) Paper I EPS form and its published mass-dependent $q$ and $\widetilde z_{\rm f}$ relations. The PL and BT predictions use their corresponding linear-spectrum variances and are not fitted to the plotted simulation histories. Reduced histories, curve tables, selection summaries, and a standalone plotting script were added to `public_data/`.

## 1. Describe the projected density fields

- **Location:** Projection subsection and Fig. `fig:dark_matter_comparison`
- **Status:** Completed

### Requested change

> We need to describe the figure. For example, we can see blue tilted has more structures, especially at higher redshift. "The present analysis does not measure a subhalo mass function, radial subhalo distribution, or subhalo survival statistic, so the projections are not used as quantitative evidence for subhalo abundance or concentration." is true but the readers understand that. We can say we will quantify these later.

### Revision made

The revised paragraph explains that the matched initial phases keep the large-scale filamentary network and the most massive collapsed regions spatially aligned across the three models. It then identifies the stronger small-scale contrast and finer structure in the BT runs, especially for the $k_p=1\,h\,{\rm Mpc}^{-1}$ model at $z=8.52$. The paragraph and caption now direct readers to the subsequent quantitative comparisons using the halo mass function, assembly histories, halo profiles, concentration--mass relation, and nonlinear matter power spectrum.

## 2. Acknowledge previous simulation studies

- **Location:** Introduction, after the opening paragraph
- **Status:** Completed

### Requested change

> For simulations, We have Jianhao paper and \cite{Nadler2025enhanced} (but for zoom-in) and \cite{Hirano15BlueTiltedPPS} (for high redshift) also has simulations, although they are not looking into halo statistics in detail.

### Original text

> However, dedicated numerical simulations of enhanced small-scale power spectrum are still limited, so the halo response to different small-scale primordial spectra is not yet well tested.

### Revised text

> Previous studies have simulated enhanced small-scale power in high-redshift cosmological volumes and in zoom-in models of Milky Way--mass environments \citep{Hirano15BlueTiltedPPS,Wu25BT,Nadler2025enhanced}. However, systematic comparisons of halo abundance, assembly histories, internal structure, and nonlinear matter power across matched cosmological volumes remain limited.

### Reason for the revision

The revised wording acknowledges the existing high-redshift and zoom-in simulations while defining the remaining gap more precisely: a systematic comparison of multiple halo and matter statistics in matched cosmological volumes.

## 3. Update the input-power-spectrum legend

- **Location:** Fig. `fig:power_spectrum_comparison`
- **Status:** Completed; the comment has been removed from the manuscript

### Requested change

> change the legend.

### Revision made

The figure legend now uses `BT $k_p=1$` and `BT $k_p=10$` instead of the previous internal labels. The updated names match the model notation used throughout the manuscript.

## 4. Adjust the Sim/Reed07 y-axis range

- **Location:** Sim/Reed07 panels in Fig. `fig:mass_function`
- **Status:** Completed; the figure was regenerated on the cluster

### Requested change

> also in Sim/Reed07 row, the lower limit of yrange can be adjusted.

### Revision made

The fixed Sim/Reed07 range of `0.5--1.5` was replaced with data-informed limits for each redshift row. The two rows use `0.2--5` and `0.2--50`, respectively, so that the low values, high-redshift points, and plotted error bars remain visible. The caption states that the Sim/Reed07 range is set separately for each redshift row.

## 5. Explain the unsmoothed halo mass histories

- **Location:** Half-Mass Redshift subsection, Fig. `fig:half_mass_redshift`, and Appendix `app:trusted_ranges`
- **Status:** Completed

### Requested change

> What is no-envelope measurement?

### Original wording

> no gap filling or cumulative-envelope smoothing is applied

> Under this common no-envelope measurement

### Revised explanation

The manuscript now states that each halo is followed across snapshots through its persistent HBT-HERONS `TrackId`. The recorded FOF masses are used directly: missing snapshots are not filled, and the mass history is not forced to grow monotonically with a cumulative-maximum filter. Temporary FOF mass changes caused by bridge or split events therefore remain in the half-mass assembly histories.

The term `no-envelope measurement` has been removed from the scientific text and caption. It remains only in the image filename, which is not displayed in the manuscript.

## 6. Replace internal analysis terminology with explicit descriptions

- **Location:** Abstract, numerical methods, figure captions, results, conclusions, and numerical-range appendix
- **Status:** Completed

### Revision made

Several internal or ambiguous expressions were replaced with direct descriptions of the calculation:

- `same-TrackId histories` now explains throughout the methods, figure captions, and conclusion that a persistent HBT-HERONS identifier follows the same halo across snapshots.
- `model-matched reference curves` now states that each analytic curve is evaluated with the corresponding PL or BT linear matter power spectrum and is not refitted to the simulations.
- `particle-count profiles` and `particle stacks` now state that radial density profiles are measured directly from simulation particles.
- `estimator-sensitive comparisons` now states that the high-$k$ amplitudes depend on the power-spectrum estimator and treatment of the highest-$k$ modes.
- `caution range`, `qualitative context`, and `numerical reliability bracket` were replaced by the specific particle-number, particle-grid, box-size, or fitting-range limitation.
- Repeated `controlled reference comparison` wording was replaced by a direct statement of what was calculated and which parameters were not refitted.

These edits change only the explanation of the analysis. They do not change any data, numerical values, model definitions, or physical conclusions.

## 7. Compare the measured halo accretion rates with an analytic relation

- **Location:** Mass-accretion-rate discussion and Fig. `fig:mass_accretion_rate_m200c_main_branch`
- **Status:** Completed; the analytic calculation and figure update were performed on the cluster

### Requested change

> I think there is some analytic formula to measure the halo accretion rate: Correa paper I think.

### Revised measurement

The figure now follows the adjacent-snapshot main branch used in the simulation comparison of Correa et al. Descendant central halos are placed in current-$M_{200c}$ bins. For each descendant, the most massive resolved central progenitor in the previous snapshot is selected, and

\[
\frac{dM_{200c}}{dt}
=\frac{M_{200c,\rm desc}-M_{200c,\rm prog}}{t_{\rm desc}-t_{\rm prog}}.
\]

Both halos require $N_{\rm DM}\ge100$. The plotted statistic is the median within each descendant-$M_{200c}$ bin. Negative rates are retained, and each plotted point requires at least 50 matched pairs.

### Analytic comparison

The gray dashed line uses Eq. (23) of Correa et al. (2015), Paper II. It is evaluated at the mean descendant PL mass and descendant redshift. The dashed curve is a mean relation, while the simulation curves show medians, following the comparison in that paper. It is not fitted to the simulations.

The public data package now contains the reduced main-branch $M_{200c}$ accretion table, its summary, the catalog-reduction script, and the plotting script.

The earlier FOF-based diagnostic is retained separately in Appendix `app:fof_gamma_accretion`. It selects halos by their $z=0$ Warren-corrected FOF mass and plots the median adjacent-snapshot $\Gamma=d\ln M_{\rm FOF}/d\ln a$. No Correa curve is shown in that figure because the main-text reference uses dimensional $dM_{200c}/dt$ along the most-massive-progenitor branch. A visible `\Tk{}` comment records that the two figures differ in mass definition, halo sample, bin assignment, and units, and therefore should not be compared point by point.

## 8. Cite and explain the radial-profile convergence criterion

- **Location:** Radial Halo Density Profiles subsection and Fig. `fig:halo_density_analysis`
- **Status:** Addressed; the comments remain in the manuscript for confirmation

### Requested changes

> need to cite the paper

> need to describe what is kappa, or just delete it

### Original wording

> The gray shaded radial range and vertical dotted line mark the Power03 convergence criterion, labelled by \(\kappa=0.6\).

### Revision made

The manuscript now cites Power et al. (2003) and identifies \(\kappa\) as their numerical relaxation parameter. The text states that the convergence radius is defined where \(\kappa=0.6\), and that density profiles at smaller radii may be affected by two-body relaxation associated with finite particle number. The caption now states directly that the gray region and dotted line mark radii below this convergence radius.

The figure and its numerical threshold were not changed. A complete `Power2003` entry was added to the bibliography.

## 9. Remove the generic opening sentence from the Discussion

- **Location:** Opening of the Discussion and Limitations section
- **Status:** Completed

### Requested change

> too generic. sound like robot. Can delete.

### Deleted text

> This section interprets the main trends and summarizes the numerical and observational limitations.

### Revision made

The generic summary sentence was deleted. The section now begins directly with the Physical Interpretation of the Main Trends subsection.

## 10. Remove an empty lead-in to the physical interpretation

- **Location:** Opening of the Physical Interpretation of the Main Trends subsection
- **Status:** Completed

### Requested change

> This sentence sounds odd and empty: "support the following physical interpretation" does not have content. There are many sentences like that. We need to find out and delete them.

### Deleted text

> The results in Sec. IV support the following physical interpretation.

### Revision made

The empty lead-in and its resolved comment were deleted. The subsection now begins directly with the physical effect of enhanced small-scale primordial power on the initial density fluctuations and their collapse time. Similar generic framing sentences elsewhere in the manuscript are being reviewed separately rather than removed automatically.

## 11. Quantify the halo mass scales associated with the BT pivots

- **Location:** Physical Interpretation of the Main Trends subsection
- **Status:** Completed

### Requested change

> Not only low mass halos. Also we need to quantify what is low mass and high mass. Use JianHao Wu kp and Mhalo connection.

### Original wording

> At high redshift, the primary effect is an excess of low-mass halos.

### Revision made

Following Wu et al., the manuscript now associates each pivot wavenumber with a comoving Lagrangian radius \(r_l=\pi/k_p\) and characteristic mass

\[
M_p=\frac{4\pi}{3}r_l^3\rho_{{\rm crit},0}\Omega_{{\rm m},0}.
\]

For the cosmological parameters used here, \(k_p=1\) and \(10\,h\,{\rm Mpc}^{-1}\) correspond to \(M_p=1.68\times10^{13}\) and \(1.68\times10^{10}\,M_\odot\), respectively. The revision states that these are characteristic scales rather than sharp mass boundaries and that the abundance enhancement is strongest below the corresponding \(M_p\) but is not restricted to that range.

## 12. Remove repeated numerical results from the Discussion

- **Location:** Physical Interpretation of the Main Trends subsection
- **Status:** Completed

### Requested change

> We already present these results in previous sections. Don't need to repeat here in discussion; Maybe we should move section V A to the conclusion?

### Deleted material

The Discussion previously repeated the numerical halo mass-function ratios, half-mass redshifts, concentration ratio, and nonlinear matter power-spectrum ratios already reported in the Results and Conclusions.

### Revision made

The repeated numerical summary was deleted rather than moved to the Conclusions, where the same measurements are already listed. The subsection now retains only interpretation:

- the lower pivot of \(\mathrm{BT}_{k_p=1}\) enhances a broader range of resolved modes;
- the higher pivot of \(\mathrm{BT}_{k_p=10}\) confines the enhancement to smaller scales;
- nonlinear growth and mergers reduce the abundance contrast toward lower redshift, while assembly histories and internal structure retain the earlier-collapse signal; and
- the matter power spectrum averages over the full density field, so its fractional response need not match that of statistics restricted to collapsed halos.

## 13. State the scope relative to observational modeling directly

- **Location:** Opening of the Relation to Previous Work subsection
- **Status:** Completed

### Requested change

> We do not model observations directly, but instead study the overall effect of enhancements on dark matter halo profiles and statistics.

### Original wording

> Our comparison is intentionally narrower than direct observational modeling.

### Revision made

The indirect comparison was replaced by a direct statement that the paper does not model observations and instead studies how enhanced small-scale primordial power changes dark matter halo profiles and statistics. The phrase "enhanced small-scale primordial power" replaces the less specific "enhancements."

## 14. Clarify the complementary roles of periodic boxes and zoom-in simulations

- **Location:** Relation to Previous Work subsection
- **Status:** Completed

### Requested change

> I think zoom-in is more suitable for dwarf-galaxy density and strong-lensing studies of low-mass structure?

### Original wording

> Our structural measurements are a dark-matter-only test of isolated halo profiles, which are relevant for dwarf-galaxy density and strong-lensing studies of low-mass structure.

### Revision made

The revised paragraph states that zoom-in simulations are better suited to host-dependent studies of satellites, dwarf galaxies, and strong-lensing substructure. It distinguishes that role from the periodic boxes used here, which measure population-level field-halo statistics and the nonlinear matter power spectrum. The isolated-halo profiles are now described as dark-matter-only population trends that can inform observational models, not as direct predictions for satellite or lensing-subhalo populations.

## 15. State the physical connection to 21-cm observations

- **Location:** Relation to Previous Work subsection
- **Status:** Completed

### Requested change

> This paragraph also sounds vague and odd. I think we should say the enhancement boosts the number of small dark matter halos, hence galaxies and Pop III stars. These can have identifiable signatures in 21-cm observations.

### Original wording

> For 21-cm studies, the relevant link is the timing and abundance of early structure formation.

### Revision made

The paragraph now states the physical sequence directly: enhanced small-scale primordial power increases the abundance of early low-mass dark matter halos, these halos provide more potential formation sites for the first galaxies and Population III stars, and the resulting changes in radiation backgrounds, gas heating, and reionization can affect the 21-cm signal. Because the simulations contain no baryons or radiation, the text describes potential formation sites rather than asserting a one-to-one increase in galaxies or stars, and it retains the requirement for source-population, heating, and reionization models.

## 16. Explain how the tested analytic prescriptions connect to observations

- **Location:** Connection to Observations subsection
- **Status:** Completed

### Requested change

The observational relevance of the tested analytic prescriptions should be stated explicitly. In particular, halo mass-function prescriptions can support models of high-redshift galaxy populations, while the Ishiyama et al. (2021) concentration--mass relation can support strong-lensing analyses. This connection remains useful even though the simulations do not include baryons or galaxies directly.

### Original wording

> The connection to observations is indirect. The results most relevant for observational modeling are the enhanced high-redshift low-mass halo abundance, earlier low-mass assembly, increased low-mass concentrations and inner densities, and enhanced high-k matter clustering.

### Revision made

The revised paragraph assigns a concrete use to each tested prescription. Halo mass-function prescriptions evaluated with the PL and BT linear matter power spectra can enter forward models of high-redshift galaxy populations, while the Ishiyama et al. (2021) concentration--mass relation can inform models of low-mass halo structure used in dwarf-galaxy and strong-lensing studies. It also connects the simulated halo abundance and assembly changes to source-population and reionization models for 21-cm predictions. The paragraph states that the prescriptions were not refitted to the BT simulations and therefore provide inputs to observational modeling rather than direct observational constraints.

## File-Level Change Inventory for the 2026-07-15 Push

### Manuscript and bibliography

- `main.tex`: adds the explicit $M_{200c}$ definition, revises the main accretion-rate description and caption, and adds the final FOF-$\Gamma$ appendix figure and the visible comparison comment.
- `main.bib`: adds the Correa et al. (2015) Paper II reference used for the analytic mean-accretion-rate comparison.

### Figures

- `mass-function.png`: updates the Sim/Reed07 panel limits by redshift row.
- `mass-accretion-rate-m200c-main-branch.png`: replaces the forward population-mean figure with the descendant-selected most-massive-progenitor median used for the main-text comparison.
- `mass-accretion-rate-fof-gamma.png`: preserves the earlier FOF-based dimensionless diagnostic as the final appendix figure, without a Correa reference curve.
- `mass-accretion-rate-trackid.png`: removed because its generic name did not identify the plotted mass definition or statistic.

### Public data and reproducibility scripts

- `public_data/figure_data/mass_accretion/m200c_main_branch_accretion.csv` and `m200c_main_branch_accretion_summary.csv`: descendant-selected most-massive-progenitor reduction and plotted summary.
- `public_data/figure_data/mass_accretion/fof_gamma_bybin.csv` and `fof_gamma_summary.csv`: explicitly named copies of the earlier FOF-$\Gamma$ data.
- `public_data/scripts/compute_m200c_main_branch_accretion.py`: constructs the adjacent-snapshot most-massive-progenitor statistic from SOAP catalogs.
- `public_data/scripts/plot_m200c_main_branch_accretion.py`: plots the median main-branch $dM_{200c}/dt$ figure and the Correa et al. comparison.
- `public_data/scripts/plot_fof_gamma_appendix.py`: independently reproduces the appendix FOF-$\Gamma$ figure without an analytic reference line.
- `public_data/scripts/plot_hmf_public_ratio.py`: implements the revised Sim/Reed07 display ranges.
- `public_data/README.md`, `public_data/MANIFEST.csv`, and `public_data/figure_data/metadata/figure_file_manifest.csv`: distinguish the two accretion statistics and list their data, scripts, and outputs.
- The old generic `mass_accretion_rate_bybin.csv` and `mass_accretion_rate_summary.csv` names were removed in favor of the explicit FOF-$\Gamma$ names above.

### Validation record

- The main-branch reduction contains 661 plotted rows and 24 summary rows. The four displayed mass bins contain 24--35 snapshot points per model, with at least 50 matched halo pairs per point.
- The selected most massive progenitor shares the persistent HBT-HERONS `TrackId` of the descendant for at least 99.98 percent of pairs in the four displayed bins. This confirms that the reconstructed branch follows the persistent main track.
- At every snapshot shared with PL, the median BT $k_p=1$ rate is lower than PL in all four displayed mass bins. The median BT $k_p=1$/PL ratios across the shared outputs range from 0.51 to 0.66.
- The restored appendix image is byte-for-byte identical to the preserved earlier FOF-$\Gamma$ image (SHA-256 `1d9bc362461779f43478ae04cd2214cbca941e04cfab7a1fb8032bfe1cbf11dd`).
- The data reduction and figure regeneration were run through Slurm compute jobs; no heavy calculation was run on the login node.
- LaTeX compilation was intentionally not run for this revision because the figure was requested for visual inspection before compilation.

## 17. Revise the mass-assembly-history comparison figure

- **Location:** Median Mass-Assembly Histories subsection and figure
- **Status:** Figure and caption updated; manuscript compilation intentionally deferred

### Requested changes

The simulation histories should be shown as points rather than connected lines. A lower panel should also show the difference between each simulation history and its analytic reference.

### Revision made

The upper panel now shows the PL and BT simulation medians as unconnected circles and triangles. The Correa relations remain as curves. A new lower panel shows \(M_{\rm sim}/M_{\rm Correa}\), evaluated against the prominent spectrum-dependent Correa curve at each simulation redshift. A horizontal gray band marks a 10 percent difference from unity. The interval at \(z>6\) is shaded because the manuscript restricts its quantitative comparison to \(z\le6\).

## 18. Mark box-specific reliable ranges in the power-spectrum figure

- **Location:** Nonlinear matter power-spectrum figure and numerical-ranges appendix
- **Status:** Completed; figure, caption, main text, and appendix updated

### Requested change

Simulation points outside the reliable range should be identified. The low-wavenumber limit from finite box size must be shown in addition to the high-wavenumber mesh limit, especially for the 25 \(h^{-1}\) Mpc box.

### Revision made

For the low-wavenumber diagnostic, points below \(4k_{\rm f}\), with \(k_{\rm f}=2\pi/L_{\rm box}\), are retained as faded open symbols. At high wavenumber, simulation measurements above \(0.25k_{\rm Ny}\) are omitted from all power-spectrum panels, while the theory curves continue. The displayed intervals are therefore \(1.0\le k/(h\,{\rm Mpc}^{-1})\le32.2\) for the \(25\,h^{-1}{\rm Mpc}\) box and \(0.098\le k/(h\,{\rm Mpc}^{-1})\le3.14\) for the \(256\,h^{-1}{\rm Mpc}\) box. The omitted measurements remain in the released data table. No finite-volume, grid-window, or nonlinear mode-coupling correction is applied.

The main text also states that the two boxes are not spliced into a single spectrum and that each box is interpreted only over its own adopted interval. The low-redshift absolute spectra from the small box differ from the large-box measurements by more than the Gaussian mode-count estimate. BT/PL is formed only from PL and BT runs in the same box, where the shared initial phases partly cancel realization-dependent deviations.

## 19. State the resolution and volume limitations directly

- **Location:** Numerical and Modeling Limitations subsection
- **Status:** Completed

### Requested change

The opening sentence should identify resolution and box size explicitly rather than referring only to the numerical range of each statistic.

### Revision made

The sentence now lists finite mass and force resolution and finite simulation volume alongside the dark-matter-only setup and the single matched realization. The following paragraphs retain the statistic-specific explanation of these limitations.

## 20. Restate the two BT models in the Conclusions

- **Location:** Opening paragraph of the Conclusions
- **Status:** Completed

### Requested change

Readers who begin with the Conclusions should be told explicitly which two BT models are analyzed.

### Revision made

The Conclusions now state that both BT models use \(m_s=1.5\). They also identify \BTKPone{} with \(k_p=1\,h\,{\rm Mpc}^{-1}\) and \BTKPten{} with \(k_p=10\,h\,{\rm Mpc}^{-1}\).

## 21. Compare the results with previous halo mass-function studies

- **Location:** Relation to Previous Work subsection
- **Status:** Completed

### Requested change

The Discussion should compare the simulation results with previous studies of blue-tilted or otherwise enhanced small-scale power, especially work based on the halo mass function.

### Revision made

The revised subsection now separates three types of earlier work. It identifies the analytic Sheth--Tormen calculation of Parashari and Laha, the cosmological N-body halo mass functions of Hirano and Yoshida, and the localized-bump simulations of Tkachev et al. It then states the common result: the halo-abundance response is strongest at low mass and high redshift and becomes weaker toward \(z=0\).

The text also states the extension made here. The matched periodic boxes are used to compare both FOF and \(M_{200c}\) mass functions together with assembly histories, radial profiles, concentrations, and nonlinear matter power. A separate paragraph distinguishes these field-halo measurements from the Milky Way zoom-in subhalo studies of Wu et al. and Nadler et al. Dekker and Kravtsov are no longer described as a halo mass-function study; their work is cited only in the structural and observational context where it belongs.

The cited papers and their stated methods were checked against their journal or arXiv records before the revision. No new bibliography entry was required because all six references were already present in `main.bib`.

## 22. Remove repetition from the Introduction and state the analytic comparisons

- **Location:** Final paragraphs of the Introduction
- **Status:** Completed

### Requested changes

The second list of observational probes repeats the opening paragraph and should be shortened. The statement of the paper's scope should also say that the simulations are compared with existing analytic models.

### Revision made

The repeated list of high-redshift galaxies, Milky Way zoom-ins, dwarf galaxies, lensing, and 21-cm studies has been replaced by two direct sentences. They state that observational interpretation requires additional astrophysical modeling and that this paper first isolates the dark-matter response.

The following scope paragraph now states the simulation design and measured statistics without repeating the observational motivation. It also adds the comparison with published halo mass-function, concentration, and mass-assembly prescriptions. The text specifies that each prescription is evaluated with the linear spectrum of the corresponding model and that its parameters are not refitted to the simulations.

## 23. Reorganize the halo definitions and merger-tree methods

- **Location:** Numerical Methods and the opening sentences of the related Results subsections
- **Status:** Completed

### Requested changes

The Simulation Suite and Terminology subsection should appear before the halo-catalog methods. The halo-method discussion should separately explain the FOF and spherical-overdensity definitions, the halo center and structural measurements, and the merger-tree progenitor assignment. Detailed result-specific cuts should remain in the Results section.

### Revision made

The simulation terminology has been merged into the earlier Simulation Suite subsection, which now precedes the halo-catalog discussion. The duplicate subsection after the halo methods has been removed.

The renamed Halo Catalogs and Merger Trees subsection now follows a fixed order. It first defines the SWIFT FOF groups and their linking length. It then defines \(M_{200c}\) and \(M_{200m}\) and identifies the corresponding SOAP catalog fields. A separate paragraph distinguishes the centers used for the structural measurements: the direct particle profiles use `SO/200_mean/CentreOfMass`, while the SOAP SO concentration uses the HBT-HERONS most-bound-particle input center. It also states the direct particle-shell profile measurement and SOAP's NFW-based radial-moment concentration calculation. The final paragraph explains the HBT-HERONS particle-tracking tree, persistent `TrackId`, descendant link, and the same-`TrackId` main progenitor branch used for the assembly histories.

The FOF mass-function, half-mass redshift, radial-profile, and concentration subsections now refer back to the new methods label. Their sample cuts, binning rules, and numerical results remain in the Results section.

## 24. Explain the redshift and model dependence in the projection figure

- **Location:** Projection figure caption and accompanying Results paragraph
- **Status:** Completed

### Requested change

The text should state that the visual effect is strongest at high redshift and should explain why \BTKPone{} shows the clearest enhancement.

### Revision made

The caption and main text now state that the BT--PL contrast is most visible at \(z=8.52\) and becomes less distinct toward \(z=0\). They also explain that \BTKPone{} has the clearest small-scale structure because its lower pivot enhances a broader range of resolved modes and gives the largest small-scale input power. The shared phases are retained as the reason that the large-scale structures remain aligned across models.

## 25. Introduce the pivot-to-mass conversion with the BT models

- **Location:** Power-Spectrum Models and Linear Matter Power subsection; Physical Interpretation subsection
- **Status:** Completed

### Requested change

The theoretical overview should give readers an approximate halo mass scale associated with each pivot before the numerical results are presented.

### Revision made

The model-definition subsection now introduces the Lagrangian mapping \(r_l=\pi/k_p\) and \(M_p=(4\pi/3)r_l^3\rho_{{\rm crit},0}\Omega_{{\rm m},0}\), following Wu et al. For the adopted cosmology, the text gives \(M_p=1.68\times10^{13}\,M_\odot\) for \(k_p=1\,h\,{\rm Mpc}^{-1}\) and \(M_p=1.68\times10^{10}\,M_\odot\) for \(k_p=10\,h\,{\rm Mpc}^{-1}\). It states immediately that these are approximate characteristic scales rather than sharp boundaries.

The Discussion now refers back to the numbered pivot-mass equation instead of repeating the formula and both numerical values. It retains the physical interpretation that the high-redshift abundance response is strongest below the corresponding characteristic mass, while assembly and internal structure preserve the earlier-collapse signal at later times.

## 26. Define the Power et al. relaxation parameter explicitly

- **Location:** Radial Halo Density Profiles subsection and figure caption
- **Status:** Completed

### Requested change

The text should cite the convergence study and define \(\kappa\) rather than only displaying the threshold \(\kappa=0.6\).

### Revision made

The radial-profile subsection now gives the exact criterion used by the figure script,
\[
\kappa(r)=\frac{N(<r)}{8\ln N(<r)}
\left[\frac{200\rho_{{\rm m},0}}{\overline{\rho}(<r)}\right]^{1/2}.
\]
It defines the enclosed particle count, mean enclosed density, and present-day mean matter density. The convergence radius is the smallest radius satisfying \(\kappa\ge0.6\). The text states that smaller radii can be affected by finite-particle two-body relaxation.

The caption now points to the numbered equation and identifies the gray region as \(r<r_{\rm conv}\). The Power et al. (2003) citation remains attached to the criterion. No figure data or convergence threshold was changed.

## 28. Make the concentration figures compact and consistent

- **Location:** Main-text I21 concentration figure and appendix D19 and L16 concentration figures
- **Status:** Completed; final figures regenerated on Slurm job `1973305`

The four redshift blocks retain the same three-row structure: the
concentration--mass relation, the median simulation-to-reference ratio, and
the halo-to-halo scatter. The canvas and row heights now follow the compact
mass-function layout. Light major grids were added to all panels. The mass
range is shortened at \(z=3.44\) and \(z=8.52\), where no higher-mass simulation
measurements exist, and the concentration limits now include the plotted
16th--84th percentile ranges without retaining unused space below the data.

The neighboring lower-panel y-axis labels and panel spacing were also adjusted
so that the ratio and scatter labels remain separate. The ratio row now shows the median ratio markers without repeating the
16th--84th percentile error bars. The same scatter is already shown by the
error bars in the main panel and quantified in the third row. The change makes
the ratio trend readable without changing any simulation medians, theory
curves, selections, or quoted numerical results. All three figures now use
320-dpi output, and the analysis and public provenance copies of the plotting
script are synchronized.

## 29. Show relative differences in the HMF model comparisons

- **Location:** Bottom rows of the FOF/Reed07 and \(M_{200c}\)/B16 mass-function figures
- **Status:** Completed; figures regenerated on Slurm job `1988333`, manuscript compilation deferred

The FOF bottom row now shows
\(\Delta f/f_{\rm Reed07}=(f_{\rm sim}-f_{\rm Reed07})/f_{\rm Reed07}\)
instead of \(f_{\rm sim}/f_{\rm Reed07}\). The same change was applied to the
\(M_{200c}\) comparison using B16. Zero therefore marks agreement with the
reference model in both figures.

Both bottom rows use a symmetric-logarithmic y-axis with a linear interval for
\(|\Delta f/f|\le0.1\). A horizontal gray band marks this \(\pm10\%\) interval,
and each redshift row uses limits derived from its plotted values and Poisson
error bars. The BT/PL middle rows remain direct ratios.

The main analysis scripts, the portable FOF plotting script, figure captions,
public-data inventory, and figure-file manifest were updated together. The
active HMF figure comment was removed after the revised figures passed visual
inspection.

## 30. Cite and quantify the BK09 and COCO half-mass comparisons

- **Location:** Half-Mass Redshift subsection
- **Status:** Completed

The Millennium-II citation is Boylan-Kolchin et al. (2009), and the COCO
citation is Hellwing et al. (2016). Their DOI and arXiv records were checked
against the published metadata. The source papers also confirm the fitting
coefficients used by the plotting script.

The revised text distinguishes their halo definitions: BK09 calibrated its
relation with virial masses, while COCO used FOF masses. Both relations are
therefore shown as external \(\Lambda\)CDM references rather than fits to the
present simulation.

For the 15 PL bins with
\(1.25\times10^9\le M_{\rm FOF}/M_\odot\le8.22\times10^{11}\), the mean
absolute offsets in \(z_{1/2}\) are \(0.053\) from BK09 and \(0.097\) from
COCO/Hellwing16. The corresponding maximum absolute offsets are \(0.128\) and
\(0.207\). These values are taken from
`same_trackid_no_envelope_summary.csv`.

## 31. Cite the foundations of the EPS framework

- **Location:** Median Mass-Assembly Histories subsection
- **Status:** Completed

The Correa et al. mass-assembly model is now introduced as an application of
the extended Press--Schechter framework. The text cites Bond et al. (1991) for
the excursion-set method and Lacey and Cole (1993) for its application to halo
merger and formation histories. Both bibliography entries were checked against
their journal metadata and DOI records.

## 32. Quantify and compare the concentration scatter

- **Location:** Concentration--Mass Relation subsection
- **Status:** Completed

The revised text compares two resolved mass ranges at \(z=0\). The median
\(\sigma_{68}(\log_{10}c)\) values in
\(10^{9.5}\le M_{200c}/M_\odot<10^{10}\) are \(0.18\), \(0.24\), and \(0.19\)
for PL, \BTKPone{}, and \BTKPten{}. In
\(10^{10.5}\le M_{200c}/M_\odot<10^{11.5}\), they are \(0.15\), \(0.18\), and
\(0.15\). Thus, all three models have larger scatter in the lower-mass range.

Macciò et al. (2007) reported a total scatter
\(\sigma_{\ln c}=0.40\pm0.03\) and an intrinsic scatter of \(0.33\pm0.03\) for
their \(z=0\) halo sample. The manuscript presents this as an approximate
comparison because the studies use different mass definitions, concentration
estimators, and scatter statistics. The article metadata and quoted scatter
values were checked against the published paper.

## 33. Cite HMcode2020 and identify the implementation

- **Location:** Power Spectrum subsection
- **Status:** Completed

The nonlinear-theory paragraph now cites Mead et al. (2021) for HMcode2020 and
links the `pyhmcode` implementation used in the analysis:
`https://github.com/tilmantroester/pyhmcode`. The paper metadata, DOI, arXiv
record, and repository URL were checked before the revision.

## 34. State the high-mass limitation of the L16 comparison

- **Location:** Alternative Concentration Prescriptions appendix
- **Status:** Completed

The appendix now states that the L16 prediction differs more strongly from the
simulations at the high-mass end at \(z=8.52\). The simulated median
concentration rises in the highest-mass bins, while the L16 curve continues to
decline. Because these bins contain few halos, the trend is interpreted
qualitatively. The I21 and D19 predictions are described as showing a similar
trend rather than as precisely capturing the upturn.

## 35. Complete the final prose-consistency pass

- **Location:** Abstract, Introduction, Numerical Methods, Discussion, Conclusions, and Alternative Concentration Prescriptions appendix
- **Status:** Completed

The final pass removed unsupported or obsolete statements and simplified the
remaining prose without changing the numerical results. It removed the stale
\(V_{\max}\)--\(R_{\max}\) paragraph, corrected the initial-spectrum caption,
and shortened the projection description. It also states explicitly that the
two power-spectrum boxes are interpreted separately rather than spliced.

The pass corrected the unscoped `\\small{SWIFT}` declaration, restored a
limitations sentence that had accidentally followed a comment marker, and
replaced several vague or overly strong expressions. The abstract now says
that published prescriptions reproduce broad trends rather than validate
them. The Conclusions identify the box-dependent uncertainty in the absolute
small-box spectra and use direct language for variation among realizations,
finite-volume effects, and future observational tests.

## 36. Define symbols and abbreviations on first use

- **Location:** Theoretical Overview, Numerical Methods, Results, figure captions, numerical-range table, and acknowledgments
- **Status:** Completed

The manuscript now defines the comoving wavenumber \(k\), the scalar spectral
index \(n_s\), the initial redshift \(z_i\), the density parameters, the
normalization \(\sigma_8\), the dimensionless linear power \(\Delta^2\), and
the present-day quantities \(\rho_{{\rm crit},0}\) and
\(\Omega_{{\rm m},0}\). It also expands HMF, FOF, and NFW at first use and defines
\(N_{\rm h}\), the mass-function symbol \(f\), the BK09 and COCO/Hellwing16
labels, the redshift-dependent reference densities used for \(M_{200c}\) and
\(M_{200m}\), the final-mass window center \(M_0\), the main-progenitor mass
\(M(z)\), the Correa formation redshift, and the inverse error function.

The concentration section now defines D19, I21, L16, \(P_{16}\), and
\(P_{84}\). The power-spectrum section uses \(N_{\rm p}\) only for the total
simulation particle count and reserves \(N_{\rm DM}\) for the per-halo dark
matter particle count. It also defines \(N_{\rm mesh}\), \(\Delta k\),
\(N_{\rm mode}\), \(N_{\rm real}\), and \(\sigma_P/P\). JWST, AGN, RGC, and
CUHK are expanded at first use. These edits do not change any numerical value,
selection criterion, or figure.

## 37. Remove the high-redshift shading from the mass-assembly-history figure

- **Location:** Median Mass-Assembly Histories figure and caption
- **Status:** Completed

The vertical gray region at \(z>6\) has been removed from all three panels, and
the corresponding sentence has been deleted from the figure caption. All data
points and analytic curves remain unchanged. The text retains \(z\le6\) as the
range used for quantitative comparisons because more than 90 per cent of every
selected sample is detected over that range; this sample-completeness statement
is not presented as a shaded numerical-resolution boundary.

## 38. Make the GitHub and Zenodo release easier to use

- **Location:** Repository root, public-data documentation, and Data Availability
- **Status:** Completed

The repository now has a root-level `README.md` with environment setup,
one-command regeneration of all 12 figures, a directory guide, compact-catalog
validation instructions, and the Zenodo DOI. A root-level `requirements.txt`
forwards to the maintained figure dependency list in
`public_data/requirements-figures.txt`.

The Data Availability section now states that the Zenodo release contains the
compact per-halo inputs used at six snapshots, plus the tracked assembly
histories and radial-profile selection metadata. The full SWIFT snapshots and
complete HBT-HERONS/SOAP catalogs remain excluded because they are not needed
for reproduction and are hundreds of gigabytes per model.

## 39. Clarify the Correa parameters and use the published relations

- **Location:** Median Mass-Assembly Histories subsection and figure
- **Status:** Completed

The analytic comparison now uses the published Correa et al. mass-dependent
relations for $q$ and $\widetilde z_{\rm f}$. The coefficient $a=0.292$
is calculated from the shared background cosmology. The PL and BT curves use
the same $q(M_0)$, $\widetilde z_{\rm f}(M_0)$, and $a$; their difference
comes only from the corresponding linear-spectrum variance
$S(M_0/q)-S(M_0)$. The text states the equations, numerical $q$ ranges, and
updated simulation-to-model differences. The figure has been renamed
`mass-assembly-history-correa.png`; the older half-mass-closure tables remain
available only as diagnostic products and are no longer read by the plotting
script.

## 40. Restore halo-to-halo error bars without shaded regions in the MAH figure

- **Location:** Median Mass-Assembly Histories figure and caption
- **Status:** Completed

The PL and BT simulation points now show the 16th--84th percentile
halo-to-halo range of Warren-corrected FOF mass in each final-mass window.
The middle-panel error bars show the same mass intervals divided by the
corresponding Correa-EPS value. The figure contains no shaded regions; only
horizontal unity lines remain in the ratio panels. The analytic curves,
simulation medians, and quantitative comparison ranges are unchanged.

## 41. Classify and include the complete article script set

- **Location:** Public-data script package and release builder
- **Status:** Completed

All 29 scripts retained with the article are now indexed by purpose, status,
and execution scope. The index separates current portable figure scripts from
upstream cluster reductions, validation tools, workflow wrappers, shared code,
and archived revision diagnostics. The scripts remain in one directory so the
existing imports and one-command figure workflow do not change.

The release builder now copies the complete script directory rather than a
hand-maintained subset. The public manifest includes the four previously
unlisted scripts plus the new script guide and machine-readable index. The MAH
Slurm wrapper now writes the current `mass-assembly-history-correa.png`
filename. Failed release copies, legacy analysis directories, and raw
simulation data remain outside the public package.

The D19 and I21 concentration PNGs were regenerated from the assembled release
so the article figures now match the portable plotting scripts exactly.
## Redline Display for the Language Revision

The current manuscript shows the language edits relative to commit `ae359b0`
using the LaTeX `changes` package. Replaced or removed wording is black with
strikethrough; added wording is blue; unchanged wording remains black. This
display applies only to the current language revision, not earlier revisions.
It does not introduce further scientific changes. The existing unresolved
catalog-release comment is retained.
