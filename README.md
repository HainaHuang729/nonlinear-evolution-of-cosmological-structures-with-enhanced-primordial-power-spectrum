# Article data explorer

Interactive companion to **Dark Matter Halo Formation with Enhanced Small-Scale Primordial Power**.

[Open the data explorer](https://hainahuang729.github.io/nonlinear-evolution-of-cosmological-structures-with-enhanced-primordial-power-spectrum/)

This branch hosts the static article site on GitHub Pages. Open `index.html` locally for offline use.

The original Retro Aerospace Scientific Modernism visual system uses reusable
design tokens, editorial layouts, accessible controls and reduced-motion support.
See [the design system](DESIGN-SYSTEM.md) for components and reuse instructions.

- Matched density projections at z=8.52, 2.03, and 0 with synchronized zoom and pan.
- Eight real redshifts in the full-particle projection view, with a shared color scale across models at each redshift; the original three-frame paper view remains available.
- Four existing PL-256-512 3D animations with controllable MP4/WebM playback and original GIF downloads.
- All six statistical topics and eleven article reference figures are expanded together, with per-topic controls and CSV downloads.
- Independent redshift selections persist while other topics follow projection playback.
- HMcode2020 comparisons, three concentration references, and radial BT/PL density ratios.
- Clickable redshift coverage, thirteen simulation configurations, twelve original figures, and nineteen downloadable CSV tables.

The paper view retains independent panel color normalization. Extended projections share a color scale across models at each redshift, with separate scales between redshifts. Statistical panels identify missing snapshots, units, theoretical references, and uncertainty definitions.
Source hashes and display derivations are recorded in `data/provenance.json`.
Additional projection conservation checks and animation provenance are in `data/media-provenance.json`.
The offline Chinese font uses the license in `assets/FONT-LICENSE.txt`.

GitHub Pages source: **gh-pages**, **/ (root)**. No build step or application server is needed.
