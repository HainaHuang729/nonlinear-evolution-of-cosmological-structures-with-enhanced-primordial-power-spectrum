# Ref comparison and next data-analysis plan

Date: 2026-05-05

## Reference papers read

- `1409.5228v3.pdf`: Correa et al. 2015a, "The accretion history of dark matter haloes - I. The physical origin of the universal function."
- `1501.04382v2.pdf`: Correa et al. 2015b, "The accretion history of dark matter haloes - II. The connections with the mass power spectrum and the density profile."
- `staa1491.pdf`: Brown et al. 2020, "Connecting the structure of dark matter haloes to the primordial power spectrum."
- `PLAN.md`: existing local summary connecting Brown/Correa to the current blue-tilted PPS project.

Local PDF text extraction tools were not available on this machine (`pdftotext`, `PyPDF2`, `pypdf`, `pdfplumber`, `fitz` missing), so the paper-level summary was cross-checked against the local `PLAN.md`, current `main.tex`, and accessible journal/abstract pages.

## Main comparison

### What Brown et al. 2020 already establishes

Brown et al. varied the primordial power spectrum in collisionless N-body simulations by changing the amplitude, spectral index, and pivot scale while keeping the expansion history fixed. Their key point is that halo structure is not fully universal: halo density profiles, concentration, and pseudo-phase-space-density profiles retain memory of the primordial power spectrum. Increasing the initial fluctuation amplitude raises halo concentrations and can push density profiles away from the standard NFW-like universality.

This overlaps strongly with the current manuscript's qualitative conclusion:

```text
enhanced small-scale PPS -> earlier collapse -> higher concentration / denser inner profiles
```

Therefore the current paper should not be framed as the first demonstration that PPS changes halo structure. The stronger framing is:

```text
Brown et al. demonstrate the general memory effect.
This paper quantifies the same physical response for blue-tilted small-scale PPS benchmark models,
across HMF, z_half, density profiles, concentration, and nonlinear P(k).
```

### What Correa et al. 2015 provides

Correa et al. 2015a gives the theoretical bridge:

```text
linear matter power spectrum -> sigma(M) / S(M) -> mass accretion history M(z)
```

The model has a power-law times exponential form for halo mass growth, with parameters controlled by cosmology and the linear matter power spectrum.

Correa et al. 2015b connects halo mass accretion history to internal structure:

```text
M(z) / formation time -> concentration and density profile
```

This is exactly the missing mechanism test for the current manuscript. The current results show HMF, z_half, profile, and concentration separately, but they do not yet directly prove that the concentration enhancement is mediated by earlier assembly.

## Current manuscript status

The current `main.tex` already has a coherent descriptive chain:

- HMF: BT_soft strongly boosts low-mass abundance at high redshift, e.g. BT_soft/PL is about 4.8-6.6 at z=8.52 over roughly 1e9-1e10 Msun.
- Half-mass redshift: BT_soft shifts z_half earlier, e.g. near M_z0 ~ 1.3e9 Msun, PL is 2.40 and BT_soft is 4.43.
- Density profile: BT halos have higher inner densities, especially at r < 0.1 R200.
- Concentration: at z=0, low-mass c200c is enhanced, with BT_soft/PL around 3.2 in the 1e9-1e9.5 Msun bin.
- Nonlinear power spectrum: BT_soft/PL rises at high k, reaching about 1.17 at k=20 h/Mpc in the fiducial box.

The main gap is not lack of more descriptive diagnostics. The main gap is causal linkage:

```text
Does enhanced PPS increase concentration mainly because halos assemble earlier?
Does the BT result collapse when expressed in sigma(M), peak height nu, or MAH parameters?
Does the profile shape itself change, or only concentration/compactness?
```

## Recommended next analyses

### Priority 1: c - z_half relation at fixed mass

Goal: directly test the Brown + Correa physical interpretation.

Make these plots:

1. `c200c` vs `z_half` in fixed z=0 mass bins.
2. Median `c200c(z_half)` for PL, BT_soft, BT_deep.
3. BT/PL concentration ratio before and after matching or binning by `z_half`.

Expected interpretation:

- If BT halos lie on the same `c - z_half` relation as PL, then BT mostly changes concentration by shifting assembly earlier.
- If BT remains higher concentration at fixed `z_half`, then BT changes profile structure beyond assembly timing, closer to Brown's non-universality result.

This should be the next figure if time allows only one new mechanism analysis.

### Priority 2: full main-progenitor MAH

Goal: replace the single-number `z_half` summary with the full growth history.

Make:

```text
median M_main(z) / M0 vs z
```

for fixed z=0 mass bins, comparing PL, BT_soft, BT_deep.

Use the existing half-mass CSV products under:

```text
analysis/paperplot/data/halfmass_masscorr/
analysis/STAR_STEK/PL/new_test/
```

This provides the cleanest connection to Correa's MAH framework.

### Priority 3: specific accretion rate

There is already an analysis scaffold in:

```text
analysis/STAR_STEK/accretion_rate/
```

Useful existing outputs:

```text
outputs/halo_accretion_rates.csv
outputs/rate_summary_by_snapshot.csv
outputs/rate_summary_by_mass_bin.csv
```

But the current collapsed-over-snapshot summary can hide the redshift dependence. The more useful paper figure is:

```text
median d ln M / d ln a vs z
```

in fixed final-mass bins, plus BT/PL ratio panels. This tells where in cosmic time BT halos grow earlier or slower after early assembly.

### Priority 4: fit Correa MAH parameters

Fit median MAH in each mass bin with:

```text
M(z) = M0 (1 + z)^alpha exp(beta z)
```

Then compare:

```text
alpha(M), beta(M)
c vs alpha
c vs beta
z_half vs beta
```

This would let the paper explicitly say it connects the Correa MAH-concentration framework to blue-tilted PPS simulations.

### Priority 5: sigma(M) / peak-height nu re-expression

There is already a starting point:

```text
analysis/peakheight/nu.py
```

Recommended outputs:

1. `z_half` vs `nu`.
2. `c200c` vs `nu`.
3. HMF or abundance ratio as a function of `nu`.

Key test:

- If PL and BT collapse onto a common relation in `nu`, the response is mostly controlled by the linear variance.
- If they do not collapse, the BT model produces extra non-universality beyond a simple peak-height remapping.

This is especially important because Brown and Correa both emphasize the role of the linear power spectrum amplitude/variance.

### Priority 6: profile-shape / NFW residual test

Current profile and concentration plots show compactness, but Brown's distinctive result is about possible breakdown of profile universality.

Add:

```text
NFW residuals in stacked profiles
Einasto alpha or inner slope d ln rho / d ln r
chi2_NFW by mass bin and model
```

This answers:

```text
Does BT only raise concentration, or does it alter the profile shape?
```

If time is short, use stacked-profile residuals rather than refitting every halo.

## Suggested execution order

1. Build matched halo table containing at least `model`, `halo_id`, `M_FOF_z0`, `M200c_z0`, `c200c_z0`, `z_half`, and available quality cuts.
2. Plot `c200c - z_half` at fixed mass.
3. Plot median MAH `M_main(z)/M0`.
4. Convert existing accretion-rate outputs into `d ln M / d ln a vs z`.
5. Compute sigma(M) / nu consistently from the linear input spectra, then redraw `c` and `z_half` versus `nu`.
6. Add profile-shape residuals only after the assembly-link figures are stable.

## Manuscript positioning

Recommended framing:

```text
Our results are consistent with Brown et al. (2020), who showed that halo structure retains memory of the primordial power spectrum. The novelty here is not the existence of this memory effect in general, but its quantitative imprint for blue-tilted small-scale PPS benchmarks across abundance, assembly history, internal structure, and nonlinear clustering. Correa et al. (2015a,b) provide the mechanism-level interpretation: the modified linear spectrum changes sigma(M) and the mass accretion history, which then shifts formation time and concentration.
```

## Minimal set to finish first

If time is tight, do only:

1. `c200c` vs `z_half` at fixed mass.
2. median `M_main(z)/M0`.
3. `d ln M / d ln a` from the existing accretion-rate pipeline.

These three analyses turn the current paper from "BT changes several halo statistics" into "BT changes MAH, and MAH explains the structural response."
