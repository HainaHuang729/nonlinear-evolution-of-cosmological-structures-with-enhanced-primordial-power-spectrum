# Article data explorer

Interactive companion to **Dark Matter Halo Formation with Enhanced Small-Scale Primordial Power**.

[Open the data explorer](https://hainahuang729.github.io/nonlinear-evolution-of-cosmological-structures-with-enhanced-primordial-power-spectrum/)

This branch hosts the static article site on GitHub Pages. Open `index.html` locally for offline use.

The original Retro Aerospace Scientific Modernism visual system uses reusable
design tokens, editorial layouts, accessible controls and reduced-motion support.
Muted red, yellow and blue ribbons mark the hero register and section boundaries.
See [the design system](DESIGN-SYSTEM.md) for components and reuse instructions.

- A header button switches between Chinese and English and remembers the preference. Switching retains redshift, zoom, video position, filters and archive state; original scientific files remain unchanged. Both languages also work offline.
- Matched density projections at z=8.52, 2.03, and 0 with synchronized zoom and pan.
- Eight real redshifts projected with the paper’s adaptive smoothing settings (57 neighbours, kernel_gamma=1.8, speedup_fac=2, dimension=3) onto 1024² grids. All panels use independent logarithmic color normalization, as in the paper; the original three-frame paper view remains available.
- Two PL-256-512 full-particle animations (rotation and redshift evolution), with controllable MP4/WebM playback and original GIF downloads. Voxel animations are excluded.
- All six statistical topics remain expanded, with per-topic controls and CSV downloads. Inline paper reference images are removed; the complete figure collection remains in the archive.
- The figure and data archive starts collapsed. Expand it to search, filter or download; collapsing it preserves the current filter state.
- Independent redshift selections persist while other topics follow projection playback.
- HMcode2020 comparisons, three concentration references, and radial BT/PL density ratios.
- Clickable redshift coverage, thirteen simulation configurations, twelve original figures, and nineteen downloadable CSV tables.

Both projection views use the paper’s independent panel color normalization. Colors show morphology and cannot be directly compared as absolute density between panels. Statistical panels identify missing snapshots, units, theoretical references, and uncertainty definitions.
Source hashes and display derivations are recorded in `data/provenance.json`.
Full-particle projection settings, comparison with all nine overlapping paper panels, and animation provenance are in `data/media-provenance.json`.
The offline Chinese font uses the license in `assets/FONT-LICENSE.txt`.

GitHub Pages source: **gh-pages**, **/ (root)**. No build step or application server is needed.
