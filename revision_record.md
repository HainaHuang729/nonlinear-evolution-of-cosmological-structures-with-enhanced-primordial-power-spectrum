# Revision Record

Date: 2026-04-26

Project: `/Users/amadeus/overleaf/nonlinear-evolution-of-cosmological-structures-with-enhanced-primordial-power-spectrum`

Main source file: `main.tex`

Compiled output: `main.pdf`

## 1. Abstract

Location: `main.tex:156`

Changes:

- Rewrote the abstract into a standard paper structure: motivation, method, models, diagnostics, main results, and observational relevance.
- Clarified that the study uses high-resolution dark-matter-only cosmological `N`-body simulations.
- Specified the comparison between a standard power-law primordial spectrum and two blue-tilted benchmark models.
- Listed the measured diagnostics: halo mass function, half-mass assembly redshift, stacked halo density profiles, concentration-mass relation, and nonlinear matter power spectrum.
- Replaced the awkward phrase about "for example, like strong and weak gravitational lensing observations" with a clearer list of relevant probes: JWST high-redshift galaxy counts, local dwarf-galaxy structure, strong-lensing substructure constraints, and future small-scale clustering measurements.
- Removed draft-style color markup from the abstract.

Purpose:

- Make the abstract more concise, more formal, and better aligned with the revised Introduction and Discussion.

## 2. Introduction

Location: `main.tex:162`

Changes:

- Reorganized the Introduction around the standard logic used in related cosmological simulation papers:
  1. large-scale success of Lambda CDM and the weakly constrained small-scale PPS;
  2. motivation from JWST high-redshift galaxy candidates and small-scale structure problems;
  3. definition of the blue-tilted PPS as a controlled small-scale modification;
  4. summary of related observational and theoretical work;
  5. statement of the gap filled by this paper.
- Clarified that previous work often asks observation-specific questions, while this paper isolates the dark-matter-only nonlinear response to enhanced small-scale primordial power.
- Added a clearer statement of the paper's contribution: providing the simulation-level link between modified initial conditions and dark-matter statistics used by JWST, 21 cm, dwarf-galaxy, and strong-lensing analyses.

Key added or emphasized citations:

- `Labbe23MassiveGalaxies`
- `Donnan23UVLF`
- `Parashari23JWSTPPS`
- `Hira24bluetilt`
- `Wu25BT`
- `Dekker25DwarfPPS`
- `Gilman22SubgalacticPPS`
- `Munoz20SmallScale21cm`
- `deKruijf25DarkAges`
- `Zhu26SKAPPS`

Purpose:

- Make the research gap explicit.
- Explain more clearly whether similar work already exists and how this paper is complementary rather than repetitive.

## 3. Theoretical Overview

Location: `main.tex:182`

Changes:

- Framed the blue-tilted model as one representative application of a broader modified-PPS program.
- Added wording that the analysis pipeline can later be applied to other PPS shapes if the initial conditions are generated consistently.

Purpose:

- Avoid making the paper sound limited to only one phenomenological model.
- Make the theoretical setup more general and reusable.

Note:

- Some text in this section is still marked with `\yellow{...}` as draft-highlight text. This can be removed or converted to normal text in a final cleanup pass.

## 4. Numerical Methods Headings

Locations:

- `main.tex:195`
- `main.tex:197`
- `main.tex:199`
- `main.tex:249`

Changes:

- Changed `initial conditions (IC)` to `Initial Conditions`.
- Changed `Simulation code` to `Simulation Code`.
- Changed `Cosmological parameters` to `Cosmological Parameters`.
- Changed `Halo finder and halo property post-processor` to `Halo Finder and Halo Property Post-processor`.

Purpose:

- Make section headings consistent with formal paper style.

## 5. Discussion and Limitations

Location: `main.tex:446`

Changes:

- Rewrote `Physical Interpretation of the Main Trends` to connect the separate results into one physical picture:
  - enhanced small-scale primordial power increases the initial amplitude of low-mass perturbations;
  - low-mass structures collapse earlier;
  - halo abundance, assembly history, density profiles, concentrations, and nonlinear power spectrum respond consistently.
- Added a new subsection: `Relation to Previous Work`.
- In the new subsection, separated related studies into several categories:
  - JWST high-redshift galaxy motivation;
  - zoom-in simulations and Milky Way substructure;
  - dwarf-galaxy and strong-lensing constraints;
  - 21 cm probes of cosmic dawn and reionization.
- Clarified that this paper does not replace observation-specific analyses, but supplies the dark-matter simulation benchmark that those analyses can build on.
- Removed red draft grouping from the rewritten Discussion text.
- Cleaned the `Connection to Observations` subsection and integrated the strong-lensing and dwarf-galaxy citations into normal text.

Purpose:

- Directly answer the question: what has already been studied, what this paper adds, and where it is complementary.
- Make the Discussion less like a repeated results summary and more like a scientific positioning section.

## 6. Conclusions

Location: `main.tex:475`

Changes:

- Changed the section title from `CONCLUSIONS` to `Conclusions`.
- Replaced the previous multiple-subsection structure with a more standard journal-style conclusion.
- Consolidated the results into four main findings:
  1. blue-tilted models produce an excess of low-mass halos;
  2. halos assemble earlier at fixed final mass;
  3. halo inner densities and concentrations are enhanced;
  4. nonlinear matter power retains and amplifies high-wavenumber excess.
- Added a final paragraph on future work:
  - hydrodynamic simulations or semi-analytic galaxy modeling;
  - reionization modeling for 21 cm predictions;
  - larger simulation suites for convergence and sample variance;
  - joint analysis of multiple small-scale probes.

Purpose:

- Make the conclusion more concise and less repetitive.
- Emphasize the scientific contribution rather than restating each plotted statistic separately.

## 7. Bibliography

Location: `main.bib:460`

Added entries:

- `Labbe23MassiveGalaxies`
- `Donnan23UVLF`
- `Munoz20SmallScale21cm`
- `Zhu26SKAPPS`

Purpose:

- Support the revised Introduction and Discussion with references on JWST high-redshift galaxies and 21 cm constraints on small-scale primordial power.

## 8. Generated LaTeX Files

Changed automatically after compilation:

- `main.aux`
- `main.bbl`
- `main.blg`
- `main.fdb_latexmk`
- `main.fls`
- `main.log`
- `main.out`
- `main.pdf`

Reason:

- These files changed because `latexmk -pdf main.tex` was run after editing the manuscript.
- The substantive human edits are in `main.tex`, `main.bib`, and this `revision_record.md` file.

## 9. Compile Check

Command run:

```bash
latexmk -pdf main.tex
```

Result:

- Compilation succeeded.
- `main.pdf` was regenerated.
- No undefined citations were found.
- No undefined references were found.
- No LaTeX fatal errors were found.
- Remaining warnings are non-blocking layout or package warnings, mainly underfull hbox and caption/revtex warnings.
