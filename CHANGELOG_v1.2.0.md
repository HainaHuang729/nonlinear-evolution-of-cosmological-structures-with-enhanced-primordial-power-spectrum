# Changelog: v1.1.0 -> v1.2.0 (2026-11-23)

## Manuscript & Bibliography
- Revised `main.tex` and `main.bib` addressing peer-review and consistency checks:
  - Disabled review-highlight color macro and removed draft comments/internal cluster paths.
  - Corrected pivot mass values ($M_p \simeq 1.69\times10^{13}$ and $1.69\times10^{10}\,M_\odot$), $256\,h^{-1}{\rm Mpc}$ Nyquist wavenumber ($k_{\rm Ny}\simeq12.6\,h\,{\rm Mpc}^{-1}$), 3LPT initialization details, and NGP power-spectrum window smoothing magnitude ($\sim3\%$--$5\%$).
  - Added full high-$z$ ($z=10.52$--$19.41$) HMF comparisons, Bocquet et al. (2016) cluster/low-$z$ extrapolation caveats, and quantitative caveats for Correa-EPS (fixed WMAP5 closure, PL progenitor truncation `83.6%` at $z=6.15$), Power (2003) $\kappa\ge0.6$ critical-vs-mean density scaling ($\Omega_{m,0}^{-1/2}\simeq1.78$), and SOAP radial-moment concentration estimates vs NFW profile fitting.
  - Split resolved low-mass concentration enhancement ($10^{9.5}$--$10^{10}\,M_\odot$, where $r_s>\epsilon_{\rm Pl}$: `2.71` and `1.19`) from the threshold-straddling $10^9$--$10^{9.5}\,M_\odot$ interval (`3.20` and `1.35`).
  - Incorporated the 23 passing $256\,h^{-1}{\rm Mpc}$ ${\rm BT}_{k_p=10}$ SOAP bias bins (`BT10/PL = 0.988--1.009`), updated Appendix D shared-bin metrics (`170` bins; median residuals `6.19%` for SOAP/T10 and `7.83%` for FOF/ST99), explained the $z=0$ negative bias offset via HBT-HERONS satellite/backsplash classification and mode-weighted quasi-nonlinear $b(k)$, and switched Appendix D Fig. 14 to two-column `figure*`.
  - Changed `@software{Hahn2020MUSIC2monofonIC}` to `@misc` in `main.bib` (eliminating all BibTeX warnings).

## Data & Scripts
- **`halo_bias_measurements.csv`**: Merged the 23 `large_scale` ${\rm BT}_{k_p=10}$ $256\,h^{-1}{\rm Mpc}$ SOAP central bias bins (`476 -> 499` rows, no duplicates).
- **`m200c_bocquet16_hmf_points.csv` & `plot_bocquet16_m200c_hmf.py`**: Renamed mislabeled header `dn_dlog10M` to `dn_dlnM` to match values; raised top-row lower axis limit to `1e-5`, thinned symlog residual ticks, and moved annotation clear of dashed curve.
- **Colossus `k_p=10` spline overshoot fix**: Increased `cosmo.k_Pk_Nbins` to `[10, 30, 60, 600, 10]` (with `persistence=""`) across `plot_bocquet16_m200c_hmf.py`, `concentration_qc_kp10.py`, `bt_plot_halo_density_profile_png.py`, and `halomass_fof_reed07.py`, eliminating the `~5.6%` cubic-spline ringing near $k_p=10\,h\,{\rm Mpc}^{-1}$.
- **Concentration relaxation figures & dataset**: Added 7 reduced CSVs in `public_data/figure_data/concentration_relaxation/` and standalone script `public_data/scripts/plot_concentration_relaxation.py` (producing `concentration-qc-{d19,i21-relaxed-fit,l16}-relaxation.png` with two-row x-tick labels, clean D19 legend, and unclipped log ratios).
- **Radial-profile most-bound cache**: Added the 12 compact `.npz` caches in `public_data/figure_data/halo_density_radial/cache_mb/` supporting `halo-density-radial-mb-corrected.png`.
- **Other figure & portability fixes**:
  - `plot_input_power_spectrum.py`: Scaled input $P(k)$ by $(2\pi)^3$ to $h^{-3}\,{\rm Mpc}^3$ and increased high-$k$ gray contrast.
  - `plot_hmf_public_ratio.py`: Fixed `dn/dlog10 M_FOF` & `\Delta f/f_{Reed07}` labels and decluttered symlog residual ticks.
  - `plot_halo_bias.py`: Added `$256\,h^{-1}{\rm Mpc}$` / `$25\,h^{-1}{\rm Mpc}$` sample labels and removed Python 3.10-only `strict=True` in `zip(...)` calls for Python 3.9 compatibility.
  - `plot_mass_assembly_history_correa.py`: Added `$z=6$` vertical limit line, clarified `BT k_p=1` legend entries, and thinned ratio error bars.
  - `reproduce_all_figures.py`: Updated to regenerate and validate all 14 active manuscript figures (both PNG and PDF).
  - **`measure_bias_paired_jackknife.py` (new)**: Cluster-ready bias script implementing paired-mode jackknife on `b_BT/b_PL`, contiguous $k$-shell jackknife, and 8-octant real-space jackknife with synthetic `--self-test`.
