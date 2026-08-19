# Manuscript Revision Record

This document records requested manuscript changes and the corresponding revisions.

## Current Status

- Thirty-five requested revisions have been addressed. The EPS foundations, concentration scatter, HMcode2020 implementation, L16 high-mass limitation, and final prose-consistency pass are now documented.
- All manuscript revisions currently render in black.
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

At $z=0$ and $10^9\le M_{200c}/M_\odot<10^{9.5}$, the median $c_{\rm sim}/c_{\rm I21,fit}$ ratios are 0.96, 1.38, and 1.12 for PL, $k_p=1$, and $k_p=10$, respectively. The modified Correa histories differ from the simulated median histories by at most 25 per cent for PL and 7 per cent for $k_p=1$ over $10^9\le M_0/M_\odot\le10^{11}$ at $z=1,2,4,6$. The conclusion now summarizes these quantitative residuals and states that the published prescriptions are reference models rather than refitted BT formulae.

## 2026-07-15. Replace the accretion-rate section with full mass-assembly histories

- **Location:** Main-text assembly section, Fig. `fig:mass_assembly_history_correa`, conclusions, numerical-range table, and data-availability statement
- **Status:** Completed

The previous main-text $M_{200c}$ adjacent-snapshot accretion-rate figure and the final appendix FOF-$\Gamma$ figure are no longer referenced by the manuscript. They are replaced by `mass-assembly-history-correa-halfmass.png`.

The new figure selects halos in seven Warren-corrected $z=0$ FOF mass windows and follows each halo through its persistent HBT-HERONS `TrackId`. Each point is the median positive recorded FOF mass among selected halos detected at that snapshot. Missing detections are not filled, and no cumulative-maximum filter is applied. Quantitative interpretation is restricted to $M_0\ge10^9\,M_\odot$ and $z\le6$, where more than 90 per cent of each selected sample is detected.

The BT histories in this figure use only the $k_p=1\,h\,{\rm Mpc}^{-1}$, $m_s=1.5$ simulation. The text and caption state this explicitly. The three-model assembly ranking continues to come from the half-mass-redshift figure.

The analytic comparison uses the Correa et al. (2015) Paper I EPS form. Faint curves retain the published mass-dependent $q$ and $\widetilde z_{\rm f}$ relations. Prominent curves recompute the spectrum-dependent quantities and solve $q$ and $\widetilde z_{\rm f}$ with a half-mass closure. The latter are diagnostic modified relations, not fits to the plotted simulation histories. Reduced histories, curve tables, parameters, selection summaries, and a standalone plotting script were added to `public_data/`.

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
