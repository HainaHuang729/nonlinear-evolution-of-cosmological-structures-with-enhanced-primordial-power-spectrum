# Article data explorer

Interactive companion to **Dark Matter Halo Formation with Enhanced Small-Scale Primordial Power**.

[Open the data explorer](https://hainahuang729.github.io/nonlinear-evolution-of-cosmological-structures-with-enhanced-primordial-power-spectrum/)

This branch hosts the static article site on GitHub Pages. Open `index.html` locally for offline use.

The original Retro Aerospace Scientific Modernism visual system uses reusable
design tokens, editorial layouts, accessible controls and reduced-motion support.
See [the design system](DESIGN-SYSTEM.md) for components and reuse instructions.

- Matched density projections at z=8.52, 2.03, and 0 with synchronized zoom and pan.
- Eight real redshifts in the full-particle projection view, with a shared color scale across models at each redshift; the original three-frame paper view remains available.
- Two PL-256-512 full-particle animations (rotation and redshift evolution), with controllable MP4/WebM playback and original GIF downloads. Voxel animations are excluded.
- All six statistical topics remain expanded, with per-topic controls and CSV downloads. Two selected reference figures accompany the mass-function and assembly-history topics; the complete figure collection remains in the archive.
- Independent redshift selections persist while other topics follow projection playback.
- HMcode2020 comparisons, three concentration references, and radial BT/PL density ratios.
- Clickable redshift coverage, thirteen simulation configurations, twelve original figures, and nineteen downloadable CSV tables.

The paper view retains independent panel color normalization. Extended projections share a color scale across models at each redshift, with separate scales between redshifts. Statistical panels identify missing snapshots, units, theoretical references, and uncertainty definitions.
Source hashes and display derivations are recorded in `data/provenance.json`.
Additional projection conservation checks and animation provenance are in `data/media-provenance.json`.
The offline Chinese font uses the license in `assets/FONT-LICENSE.txt`.

GitHub Pages source: **gh-pages**, **/ (root)**. No build step or application server is needed.
