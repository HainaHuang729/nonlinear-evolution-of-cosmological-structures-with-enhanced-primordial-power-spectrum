# Measurement display density, 2026-10-29

The first pass updates `mass-function.png`,
`mass-assembly-history-correa.png`, and
`halfmass-redshift-trackid-no-envelope.png`.

The shared `sparse_errorbar` helper retains every original centre as a small
point and spaces the larger model symbols every two samples. The MAH lower
panel uses larger symbols every three samples with small points everywhere.
All uncertainty segments remain present at their original coordinates and
extents, without caps, at alpha 0.60 and at most 0.5-point stroke width.
Continuous lines, model colours, axis limits, mass/redshift bins, and interval
interpretations are retained. FOF raster export is increased from 120 to 600 dpi.

A read-only plotting trace compared the HEAD and revised script calls:

| Script | Errorbar calls | Coordinate and uncertainty arrays |
|---|---:|---|
| `plot_hmf_public_ratio.py` | 48 | Identical, including nonfinite entries |
| `plot_mass_assembly_history_correa.py` | 24 | Identical, including nonfinite entries |
| `plot_same_trackid_no_envelope_allmodels.py` | 3 | Identical, including nonfinite entries |

Every call retains its complete input arrays. The full released CSV files are
unchanged. Incidental table exports during regeneration were checked for
numerical agreement and their original byte representations retained.

The concentration and M200c HMF figures are left unchanged in this pass: their
original theoretical-model environment is unavailable in this checkout.
No replacement theoretical curves were generated from a different model or
library implementation. The PS figure and common journal-style defaults are
unchanged; the new helper is used only by the three listed figure scripts.

The three before/after previews were visually inspected. Script syntax and
`git diff --check` pass. The manuscript is rebuilt after replacing the PNGs.
