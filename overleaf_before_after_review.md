# Before/after review

Scope:

- Part A lists edits already present in the current local draft compared with the Git version.
- Part B lists proposed next edits based on the 84-comment audit. These are not applied to `main.tex` yet.

## Part A. Already applied in the current local draft

### A1. Add blue-revision helper and table-cell helper

Before:

```tex
\usepackage{xcolor}
\usepackage{hyperref}
```

After:

```tex
\usepackage{xcolor}
\newcommand{\revisionblue}[1]{\textcolor{blue}{#1}}
\newcommand{\tabcell}[2]{\parbox[t]{#1}{\raggedright #2}}
\usepackage{hyperref}
```

Purpose: makes new response text blue and fixes table wrapping.

### A2. Abstract: quantify nonlinear matter-power response

Before:

```tex
While the blue-tilted model significantly boosts the non-linear matter power spectrum for $k> k_p$, the enhancement diminishes significantly at low redshift. {\color{red} quantify}
```

After:

```tex
\revisionblue{For the field-level statistic, the nonlinear matter-power response is more modest but measurable: in the fiducial \(25\,h^{-1}{\rm Mpc}\) box at \(z=0\), BT\_soft reaches \(P_{\rm BT}/P_{\rm PL}=1.17\) at \(k=20\,h\,{\rm Mpc}^{-1}\) and \(1.34\) at \(k=40\,h\,{\rm Mpc}^{-1}\), whereas BT\_deep remains close to unity at both wavenumbers.}
```

Comment status: the quantification request is addressed, but "field-level" should still be changed because the professor later said power spectrum is a summary statistic.

### A3. Introduction: replace older tension wording with higher-redshift/JWST motivation

Before:

```tex
The standard cosmological model, combining a nearly power-law primordial power spectrum with the $\Lambda$ Cold Dark Matter ($\Lambda$CDM) paradigm, provides an accurate description of the Universe on large scales ($>1 {\rm Mpc})$. Measurements of the cosmic microwave background, galaxy clustering, and the Lyman-$\alpha$ forest are consistent with the standard cosmological model \citep{Planck20CMB,Blanton17SDSSsurvey,Chabanier19LyalphaPS}. On the other hand, the constraints on small scales are weaker. For example, there are potential small-scale tensions in cosmology model such as the missing-satellites, core-cusp, and too-big-to-fail problems \citep{Bullock17smallscalechallenges,Sales22challenges}, although they are subject to the uncertainties in baryonic physics \citep{Benson2002reionization,Chan2015corecusp}. At the same time, early JWST measurements have revealed unexpectedly abundant and potentially massive galaxy candidates at $z\gtrsim 8$--$10$ \citep{Labbe23MassiveGalaxies,Donnan23UVLF}. These observations have motivated renewed interest in enhanced small-scale primordial matter power \cite{Parashari23JWSTPPS,Hira24bluetilt},but high redshift baryonic physics is also potential solutions, e.g., evolving star-formation efficiency, weak feedback, dust, UV emission efficiency, and selection effects \citep{Lovell23JWSTExtreme}.
```

After:

```tex
\revisionblue{The standard cosmological model, combining a nearly power-law primordial power spectrum with the \(\Lambda\) Cold Dark Matter (\(\Lambda\)CDM) paradigm, provides an accurate description of the Universe on large scales (\(>1\,{\rm Mpc}\)). Measurements of the cosmic microwave background, galaxy clustering, and the Lyman-\(\alpha\) forest are consistent with this picture \citep{Planck20CMB,Blanton17SDSSsurvey,Chabanier19LyalphaPS}. On smaller scales, however, constraints are weaker. Potential small-scale tensions such as the missing-satellites, core-cusp, and too-big-to-fail problems have motivated departures from the simplest cold-dark-matter picture \citep{Bullock17smallscalechallenges,Sales22challenges}, although baryonic physics can substantially affect these comparisons \citep{Benson2002reionization,Chan2015corecusp}. Early JWST measurements have also revealed unexpectedly abundant and potentially massive galaxy candidates at \(z\gtrsim 8\)--\(10\) \citep{Labbe23MassiveGalaxies,Donnan23UVLF}. These observations have motivated renewed interest in enhanced small-scale primordial matter power \citep{Parashari23JWSTPPS,Hira24bluetilt}; however, high-redshift baryonic physics and observational effects remain plausible explanations, including evolving star-formation efficiency, weak feedback, dust, UV emission efficiency, and selection effects \citep{Lovell23JWSTExtreme}.}
```

Comment status: addresses comments about obsolete tensions and more relevant references.

### A4. Introduction: add physical motivations for enhanced small-scale power

Before:

```tex
{\color{red} add motivations for enhanced power spectrum: e.g. ``the enhanced small-scale power spectrum can stem from a wide range of alternative cosmological theories, including warm inflation \citep{Arya20WarmInflation}, axion models with hyperbolic field-space geometry \cite{Sai26BlueTilt}, and multi-field hybrid inflation models that can naturally generate a broken power-law, blue-tilted spectrum \citep{Linde94Hybridinflation, Wang24BTinflationtheory, Wang25HybridInflation}. The discreteness of primordial black holes can also induce an isocurvature term that enhances especially the small-scale spectrum \cite{Inman2019PBHBT}.'' need rephase. }
```

After:

```tex
\revisionblue{Enhanced small-scale power can arise in several classes of beyond-minimal early-Universe scenarios. Examples include warm-inflation models that amplify curvature perturbations \citep{Arya20WarmInflation}, axion models with nontrivial field-space geometry that can generate blue spectra \citep{Sai26BlueTilt}, and multi-field or hybrid-inflation constructions capable of producing broken-power-law enhancements \citep{Linde94Hybridinflation,Wang24BTinflationtheory,Wang25HybridInflation}. A distinct route is provided by a discrete population of primordial black holes (PBHs), whose Poisson fluctuations source an isocurvature contribution to the small-scale matter power spectrum \citep{Inman2019PBHBT}. In this work we do not attempt to distinguish among these mechanisms; instead, we use the blue-tilted spectrum as a phenomenological input model for testing the gravitational response to enhanced small-scale power.}
```

Comment status: addresses motivation/reference request. Also added `Inman2019PBHBT` in `main.bib`.

### A5. Introduction: define "blue-tilted"

Before:

```tex
We use a blue-tilted (BT) power spectrum following the previous literatures \citep[e.g.][]{Hirano15BlueTiltedPPS,Parashari23JWSTPPS,Hira24bluetilt,Tkac24BumpyPPS,deKruijf25DarkAges,Dekker25DwarfPPS,Wu25BT}. {\color{red} need to describe what blue tilted is.} Note that the BT models are phenomenological models instead of directly deriving from, e.g., any inflationary model.
```

After:

```tex
\revisionblue{Following previous literature \citep[e.g.][]{Hirano15BlueTiltedPPS,Parashari23JWSTPPS,Hira24bluetilt,Tkac24BumpyPPS,deKruijf25DarkAges,Dekker25DwarfPPS,Wu25BT}, we use ``blue-tilted'' (BT) to denote a broken-power-law input spectrum whose large-scale part follows the standard nearly scale-invariant slope, while above a pivot wavenumber \(k_p\) the effective high-\(k\) slope is increased to \(m_s>n_s\). In this sense the tilt is ``blue'' because power is shifted toward shorter wavelengths, or larger \(k\), increasing the small-scale primordial matter power relative to PL. The BT models are phenomenological benchmarks rather than direct fits to any one inflationary model.}
```

Comment status: addresses the definition request.

### A6. Introduction: remove duplicated pivot paragraph and fix typo

Before:

```tex
The large-scale power spectrum follows the standard power-law form $P(k)\propto k^{n_s}$ with $n_s\simeq0.965$,

but the primordial matter power spectrum is enhanced above a pivot wavenumber $k_p$. The pivot therefore separates the well-measured large scales from the more weakly constrained small scales, preserving the successful large-scale predictions of $\Lambda$CDM while directly changing the abundance and collapse history of small halos.
Several recent studies ... can be degenerate with the priomordial power spectrum.
```

After:

```tex
Several recent studies ... can be degenerate with the primordial power spectrum.
```

Comment status: removes a repeated/clumsy definition paragraph and fixes `priomordial` to `primordial`.

### A7. Introduction: add roadmap

Before:

```tex
{\color{red} State what we do in different sections}
```

After:

```tex
\revisionblue{The rest of this paper is organized as follows. Section~\ref{sec:theory} defines the PL and BT input spectra and explains how the pivot scale changes the initial matter field. Section~\ref{sec:numerical} describes the simulation suite, halo catalog construction, analysis definitions, and numerical interpretation ranges. Section~\ref{sec:results} presents the halo abundance, assembly, concentration, and nonlinear-power responses. Section~\ref{sec:discussion} discusses the main numerical and modeling limitations and connects the benchmark diagnostics to observations. Section~\ref{sec:conclusion} summarizes the quantitative trends and the analytic ingredients that should be carried forward.}
```

Comment status: addresses the section-roadmap request.

### A8. Model table: fix typo "Blue-tiled"

Before:

```tex
Blue-tiled Soft (BT\_soft) & 1 & 1.5 \\
Blue-tiled Deep (BT\_deep) & 10 & 1.5 \\
```

After:

```tex
\revisionblue{Blue-tilted Soft (BT\_soft)} & 1 & 1.5 \\
\revisionblue{Blue-tilted Deep (BT\_deep)} & 10 & 1.5 \\
```

Comment status: typo fixed. Separate comment about combining this table with the simulation table is still open.

### A9. Trusted-ranges table: rewrite table implementation to compile cleanly

Before:

```tex
\begin{ruledtabular}
\begin{tabular}{p{0.22\textwidth}p{0.22\textwidth}p{0.22\textwidth}p{0.26\textwidth}}
Diagnostic & Quantity & Quantitative range & Interpretation note \\
\colrule
...
\end{tabular}
\end{ruledtabular}
```

After:

```tex
\begingroup
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}llll@{}}
\toprule
\tabcell{0.18\textwidth}{Diagnostic} & \tabcell{0.17\textwidth}{Quantity} & \tabcell{0.20\textwidth}{Quantitative range} & \tabcell{0.36\textwidth}{Interpretation note} \\
\midrule
...
\bottomrule
\end{tabular}
\endgroup
```

Comment status: this was mainly a LaTeX compile/layout fix, not a professor-content request.

### A10. Observation paragraph: grammar fix

Before:

```tex
The main value of the present work is therefore to identify where an primordial-power signal is likely to be largest before those additional complications are introduced.
```

After:

```tex
The main value of the present work is therefore to identify where \revisionblue{a primordial-power signal} is likely to be largest before those additional complications are introduced.
```

Comment status: small grammar fix. Broader comments about prioritizing halo effects and strengthening the final sentence are still open.

### A11. Response-summary table: rewrite table implementation to compile cleanly

Before:

```tex
\begin{ruledtabular}
\begin{tabular}{p{0.34\columnwidth}p{0.50\columnwidth}}
Diagnostic & Representative response \\
\colrule
...
\end{tabular}
\end{ruledtabular}
```

After:

```tex
\begin{tabular}{@{}ll@{}}
\toprule
\tabcell{0.28\columnwidth}{Diagnostic} & \tabcell{0.58\columnwidth}{Representative response} \\
\midrule
...
\bottomrule
\end{tabular}
```

Comment status: compile/layout fixed. Professor's comment that this should become conclusion bullet points is still open.

### A12. Bibliography: add PBH motivation reference

Before:

```bibtex
% No Inman2019PBHBT entry.
```

After:

```bibtex
@ARTICLE{Inman2019PBHBT,
       author = {{Inman}, Derek and {Ali-Ha{\"i}moud}, Yacine},
        title = "{Early structure formation in primordial black hole cosmologies}",
      journal = {\prd},
         year = 2019,
        month = oct,
       volume = {100},
       number = {8},
          eid = {083528},
        pages = {083528},
          doi = {10.1103/PhysRevD.100.083528},
archivePrefix = {arXiv},
       eprint = {1907.08129},
 primaryClass = {astro-ph.CO}
}
```

Comment status: supports the added PBH motivation paragraph.

## Part B. Proposed next before/after edits, not yet applied

### B1. Replace "field-level" for power spectrum

Before:

```tex
For the field-level statistic, the nonlinear matter-power response is more modest but measurable...
```

After:

```tex
For the matter-power summary statistic, the nonlinear response is more modest but measurable...
```

Reason: comments 53-54 say the power spectrum is not field-level; it is a summary statistic.

### B2. Fix "particle-field statistic" wording

Before:

```tex
The nonlinear matter power spectrum is a particle-field statistic and does not require a halo mass definition.
```

After:

```tex
The nonlinear matter power spectrum is measured from the particle density field and does not require a halo mass definition.
```

Reason: avoids calling the power spectrum itself field-level.

### B3. Clarify HMF ratio panels

Before:

```tex
The lower ratio panels show the direct model response, \(f_{\rm BT}(M)/f_{\rm PL}(M)\)...
```

After:

```tex
The lower ratio panels show the BT abundance relative to PL, \(f_{\rm BT}(M)/f_{\rm PL}(M)\)...
```

Reason: comment 27 says "direct model response" is unclear.

### B4. Make the IC paragraph active and clearer

Before:

```tex
For the BT models, the implementation modifies the transfer function above \(k_p\)...
```

After:

```tex
For the BT models, we modify the transfer function above \(k_p\)...
```

Reason: comment 14 asks for first-person active wording.

### B5. Make sigma8 normalization explicit

Before:

```tex
The BT spectra use the same background cosmology and large-scale normalization as PL; their matter power differs only above the pivot scale \(k_p\).
```

After:

```tex
The PL and BT initial conditions use the same \(\sigma_8=0.8111\) normalization and the same background cosmology; the BT runs differ from PL only through the transfer-function modification above \(k_p\).
```

Reason: comments 10-11 ask whether PL and BT use the same sigma8.

### B6. Terminology rule for "primordial" vs "input"

Before:

```tex
The purpose of this paper is to isolate the gravitational, nonlinear response to enhanced small-scale power in the primordial matter spectrum ... comparing a standard power-law input matter spectrum with two transfer-function-modified BT benchmark models.
```

After:

```tex
The purpose of this paper is to isolate the gravitational, nonlinear response to an enhanced small-scale primordial power spectrum. In the simulations, this enhancement is implemented as a transfer-function modification of the input linear matter power spectrum at \(z_i=200\).
```

Reason: comments 1, 2, 15, 16, and 45 ask for clearer, more consistent terminology.

### B7. Rewrite physical interpretation opening

Before:

```tex
Increasing the small-scale input matter power at \(z_i=200\) raises the initial amplitude of low-mass density fluctuations, so these perturbations cross the collapse threshold earlier than in the PL model. This earlier collapse first appears as a high-redshift abundance excess and then leaves a lower-redshift structural imprint.
```

After:

```tex
The enhanced primordial power spectrum increases the amplitude of small-scale density fluctuations in the initial conditions. These early density fluctuations trigger earlier collapse at high redshift, producing an excess of low-mass halos first and leaving a later imprint on halo assembly histories and concentrations.
```

Reason: comments 47-50 explicitly request this clearer physical wording.

### B8. Replace "uniform rescaling" sentence

Before:

```tex
The signal is not simply a uniform rescaling of all nonlinear statistics.
```

After:

```tex
The response is not the same for every diagnostic: it depends on pivot scale, redshift, halo mass, and whether the statistic measures abundance, assembly, concentration, or \(P(k)\).
```

Reason: comment 51 says "rescaling of all nonlinear statistics" is unclear.

### B9. Rename NFW diagnostic

Before:

```tex
\subsubsection{NFW-Equivalent Compactness Diagnostic}
```

After:

```tex
\subsubsection{Concentration-Derived NFW Density Profiles}
```

Reason: comments 36-40 say the current phrase is misleading and strange.

### B10. Clarify NFW caption

Before:

```tex
NFW-equivalent compactness curves reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and concentrations...
```

After:

```tex
Concentration-derived NFW density profiles reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and catalog concentrations...
```

Reason: makes clear these are not direct particle-count radial profiles.

### B11. Remove the response-summary table and fold numbers into conclusion bullets

Before:

```tex
Table~\ref{tab:main_response_summary} collects representative response amplitudes for the same trends. The main conclusions, with the corresponding result sections and figures, are as follows:
```

After:

```tex
The main conclusions, with representative response amplitudes and the corresponding result sections and figures, are as follows:
```

Reason: comments 60-62 say the table is hard to understand and should become bullet points.

### B12. Equation reference style

Before:

```tex
Eq.~(\ref{eq:bt_input_power})
```

After:

```tex
Eq.~\ref{eq:bt_input_power}
```

Reason: comment 66 says brackets are not needed for equations.

### B13. Data availability with GitHub/Zenodo placeholders

Before:

```tex
The reduced data products supporting the figures and quantitative comparisons in this article are openly available in the \texttt{public\_data/} directory accompanying this manuscript.
```

After:

```tex
The reduced data products supporting the figures and quantitative comparisons in this article are available in the project GitHub repository at \url{<GITHUB_URL>} and will be archived on Zenodo at \url{<ZENODO_URL>} if a DOI is assigned.
```

Reason: comments 81-82 ask for GitHub and possible Zenodo information.

### B14. Stronger final sentence

Before:

```tex
They are relevant to JWST-era high-redshift galaxy studies, dwarf-galaxy structure, strong-lensing probes of low-mass structure, 21 cm forecasts, and small-scale clustering measurements, but each application requires additional modeling of baryons, reionization, galaxy selection, and survey response.
```

After:

```tex
By identifying the halo masses, redshifts, and wavenumbers where the dark-matter response is largest, these simulations provide a concrete target set for future hydrodynamic simulations, semi-analytic modeling, and multi-probe tests of enhanced small-scale primordial power.
```

Reason: comment 80 says the final sentence is too weak.

### B15. Items that need data, not just text

Mass accretion rate:

```text
Comment 30 asks for a mass-accretion-rate study. This cannot be fixed honestly by prose alone; it needs a new diagnostic from merger histories.
```

Resolution study:

```text
Comment 84 asks for a resolution study. Current text only gives trusted numerical ranges. A real response needs a resolution/volume comparison if the needed runs exist.
```
