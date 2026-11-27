# Article data explorer

Interactive companion to **Nonlinear Structure Formation with Enhanced Small-Scale Primordial Power Spectrum** (`v1.2.0`).

- [Open the data explorer](https://hainahuang729.github.io/nonlinear-evolution-of-cosmological-structures-with-enhanced-primordial-power-spectrum/)
- [Download compiled manuscript PDF](assets/main.pdf)
- [Zenodo v1.2.0 archive](https://doi.org/10.5281/zenodo.24455135) · [Full snapshot archive](https://doi.org/10.5281/zenodo.24182716)

This branch hosts the static article site on GitHub Pages. Open `index.html` locally for offline use.

The original Retro Aerospace Scientific Modernism visual system uses reusable
design tokens, editorial layouts, accessible controls and reduced-motion support.
Muted red, yellow and blue ribbons mark the hero register and section boundaries.
See [the design system](DESIGN-SYSTEM.md) for components and reuse instructions.

- Bilingual Chinese/English toggle that remembers preference and preserves UI state offline.
- Matched density projections at z=8.52, 2.03, and 0 with synchronized zoom and pan, plus eight real redshifts projected with the paper’s adaptive smoothing settings onto 1024² grids.
- Two PL-256-512 full-particle animations (rotation and redshift evolution), with controllable MP4/WebM playback and original GIF downloads.
- Separate [BT Blender gallery](assets/blender/index.html) and interactive 3D WebGL particle viewer (`assets/swift-viewer/index.html`).
- Seven interactive statistical topics aligned with the `v1.2.0` manuscript (`Input power`, `Mass function`, `Halo–matter bias`, `Assembly history`, `Internal structure`, `Matter power`, `Numerical reliability`), with independent or projection-synced redshift controls and CSV downloads.
- Complete 14 manuscript figures (including PDF/PNG halo-matter bias figures, most-bound-particle radial density profiles, relaxation-split concentration relations, and phase-pair 25 h⁻¹ Mpc power spectra over $10k_{\rm f} \le k \le 0.25k_{\rm Ny}$), compiled `assets/main.pdf`, and downloadable CSV tables in the archive.

GitHub Pages source: **gh-pages**, **/ (root)**. No build step or application server is needed.
