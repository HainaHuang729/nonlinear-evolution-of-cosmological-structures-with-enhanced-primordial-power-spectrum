# Manuscript Revision Record

This document records requested manuscript changes and the corresponding revisions.

## Current Status

- All sixteen requested language, scope, citation, interpretation, and figure revisions have been addressed in the manuscript.
- Revised manuscript text remains blue for review.
- The Sim/Reed07 y-axis range has been revised. The accretion-rate figure now uses current-$M_{200c}$ population means and the Correa et al. analytic comparison.
- The earlier FOF-$\Gamma$ accretion diagnostic is retained as the final appendix figure without an analytic reference line.
- The numerical-methods section now defines $R_{200c}$, $\rho_{\rm crit}(z)$, and $M_{200c}$ explicitly.
- The Power et al. (2003) citation and explanation of the convergence parameter have been added; the original comments remain visible only for final confirmation.
- The language revisions do not change the simulation models. The accretion-rate statistic was reprocessed as recorded below.

## 1. Describe the projected density fields

- **Location:** Projection subsection and Fig. `fig:dark_matter_comparison`
- **Status:** Completed in blue text

### Requested change

> We need to describe the figure. For example, we can see blue tilted has more structures, especially at higher redshift. "The present analysis does not measure a subhalo mass function, radial subhalo distribution, or subhalo survival statistic, so the projections are not used as quantitative evidence for subhalo abundance or concentration." is true but the readers understand that. We can say we will quantify these later.

### Revision made

The revised paragraph explains that the matched initial phases keep the large-scale filamentary network and the most massive collapsed regions spatially aligned across the three models. It then identifies the stronger small-scale contrast and finer structure in the BT runs, especially for the $k_p=1\,h\,{\rm Mpc}^{-1}$ model at $z=8.52$. The paragraph and caption now direct readers to the subsequent quantitative comparisons using the halo mass function, assembly histories, halo profiles, concentration--mass relation, and nonlinear matter power spectrum.

## 2. Acknowledge previous simulation studies

- **Location:** Introduction, after the opening paragraph
- **Status:** Completed in blue text

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
- **Status:** Completed in blue text

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
- **Status:** Completed in blue text

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

- **Location:** Mass-accretion-rate discussion and Fig. `fig:mass_accretion_rate_trackid`
- **Status:** Completed; the analytic calculation and figure update were performed on the cluster

### Requested change

> I think there is some analytic formula to measure the halo accretion rate: Correa paper I think.

### Revised measurement

The figure now measures the population mean mass-accretion rate in current-$M_{200c}$ bins,

\[
\frac{dM_{200c}}{dt}
=\frac{M_{200c,i+1}-M_{200c,i}}{t_{i+1}-t_i}.
\]

At each snapshot, central halos with $N_{\rm DM}\ge100$ are selected using SOAP `SO/200_crit`. Each halo's `DescendantTrackId` is matched to the `TrackId` in the next snapshot. The rates are averaged within the current-$M_{200c}$ bin, and negative rates are retained.

### Analytic comparison

The gray dashed line uses Eq. (23) of Correa et al. (2015), Paper II. It is evaluated at the mean current PL mass and midpoint redshift of each snapshot pair. It is not fitted to the simulations.

The public data package now contains the reduced current-$M_{200c}$ accretion table, its summary, the catalog-reduction script, and the plotting script.

The earlier FOF-based diagnostic is retained separately in Appendix `app:fof_gamma_accretion`. It selects halos by their $z=0$ Warren-corrected FOF mass and plots the median adjacent-snapshot $\Gamma=d\ln M_{\rm FOF}/d\ln a$. No Correa curve is shown in that figure because the main-text reference is a dimensional population mean $dM/dt$. A visible `\Tk{}` comment records that the two figures differ in mass definition, halo sample, bin assignment, averaging statistic, and units, and therefore should not be compared point by point.

## 8. Cite and explain the radial-profile convergence criterion

- **Location:** Radial Halo Density Profiles subsection and Fig. `fig:halo_density_analysis`
- **Status:** Addressed in blue text; the comments remain in the manuscript for confirmation

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
- **Status:** Completed in blue text

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
- **Status:** Completed in blue text

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
- **Status:** Completed in blue text

### Requested change

> We do not model observations directly, but instead study the overall effect of enhancements on dark matter halo profiles and statistics.

### Original wording

> Our comparison is intentionally narrower than direct observational modeling.

### Revision made

The indirect comparison was replaced by a direct statement that the paper does not model observations and instead studies how enhanced small-scale primordial power changes dark matter halo profiles and statistics. The phrase "enhanced small-scale primordial power" replaces the less specific "enhancements."

## 14. Clarify the complementary roles of periodic boxes and zoom-in simulations

- **Location:** Relation to Previous Work subsection
- **Status:** Completed in blue text

### Requested change

> I think zoom-in is more suitable for dwarf-galaxy density and strong-lensing studies of low-mass structure?

### Original wording

> Our structural measurements are a dark-matter-only test of isolated halo profiles, which are relevant for dwarf-galaxy density and strong-lensing studies of low-mass structure.

### Revision made

The revised paragraph states that zoom-in simulations are better suited to host-dependent studies of satellites, dwarf galaxies, and strong-lensing substructure. It distinguishes that role from the periodic boxes used here, which measure population-level field-halo statistics and the nonlinear matter power spectrum. The isolated-halo profiles are now described as dark-matter-only population trends that can inform observational models, not as direct predictions for satellite or lensing-subhalo populations.

## 15. State the physical connection to 21-cm observations

- **Location:** Relation to Previous Work subsection
- **Status:** Completed in blue text

### Requested change

> This paragraph also sounds vague and odd. I think we should say the enhancement boosts the number of small dark matter halos, hence galaxies and Pop III stars. These can have identifiable signatures in 21-cm observations.

### Original wording

> For 21-cm studies, the relevant link is the timing and abundance of early structure formation.

### Revision made

The paragraph now states the physical sequence directly: enhanced small-scale primordial power increases the abundance of early low-mass dark matter halos, these halos provide more potential formation sites for the first galaxies and Population III stars, and the resulting changes in radiation backgrounds, gas heating, and reionization can affect the 21-cm signal. Because the simulations contain no baryons or radiation, the text describes potential formation sites rather than asserting a one-to-one increase in galaxies or stars, and it retains the requirement for source-population, heating, and reionization models.

## 16. Explain how the tested analytic prescriptions connect to observations

- **Location:** Connection to Observations subsection
- **Status:** Completed in blue text

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
- `mass-accretion-rate-m200c-population.png`: replaces the ambiguous main-text accretion figure with the current-$M_{200c}$ population-mean statistic.
- `mass-accretion-rate-fof-gamma.png`: preserves the earlier FOF-based dimensionless diagnostic as the final appendix figure, without a Correa reference curve.
- `mass-accretion-rate-trackid.png`: removed because its generic name did not identify the plotted mass definition or statistic.

### Public data and reproducibility scripts

- `public_data/figure_data/mass_accretion/m200c_population_accretion.csv` and `m200c_population_accretion_summary.csv`: current-$M_{200c}$ halo-level reduction and plotted summary.
- `public_data/figure_data/mass_accretion/fof_gamma_bybin.csv` and `fof_gamma_summary.csv`: explicitly named copies of the earlier FOF-$\Gamma$ data.
- `public_data/scripts/compute_m200c_population_accretion.py`: constructs the adjacent-snapshot current-$M_{200c}$ population statistic from SOAP catalogs.
- `public_data/scripts/bt_plot_mass_accretion_rate_trackid_png.py`: plots the main $dM_{200c}/dt$ figure and the Correa et al. comparison.
- `public_data/scripts/plot_fof_gamma_appendix.py`: independently reproduces the appendix FOF-$\Gamma$ figure without an analytic reference line.
- `public_data/scripts/plot_hmf_public_ratio.py`: implements the revised Sim/Reed07 display ranges.
- `public_data/README.md`, `public_data/MANIFEST.csv`, and `public_data/figure_data/metadata/figure_file_manifest.csv`: distinguish the two accretion statistics and list their data, scripts, and outputs.
- The old generic `mass_accretion_rate_bybin.csv` and `mass_accretion_rate_summary.csv` names were removed in favor of the explicit FOF-$\Gamma$ names above.

### Validation record

- The new current-$M_{200c}$ reduction contains 643 plotted rows and 24 summary rows.
- All 643 rows agree with an independently generated mechanism-test table; the maximum relative numerical difference is approximately $2.1\times10^{-7}$.
- The restored appendix image is byte-for-byte identical to the preserved earlier FOF-$\Gamma$ image (SHA-256 `1d9bc362461779f43478ae04cd2214cbca941e04cfab7a1fb8032bfe1cbf11dd`).
- The data reduction and figure regeneration were run through Slurm compute jobs; no heavy calculation was run on the login node.
- LaTeX compilation was intentionally not run for this revision because the figure was requested for visual inspection before compilation.
