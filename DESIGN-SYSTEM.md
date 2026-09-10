# Retro Aerospace Scientific Modernism

An original, content-reusable visual system. This installation retains the
existing article explorer, data adapters, scientific definitions and media.
No framework, runtime package, remote font or build server is required.
Open `index.html` directly, or serve the directory as a static site.

## Layers

| File | Responsibility |
| --- | --- |
| `tokens.css` | Semantic colors, typography, spacing, grid, line and motion tokens |
| `styles.css` | Foundation, header, hero, editorial media, scientific panels, archive, dark close, responsive and print styles |
| `system.js` | Navigation disclosure, section location, progressive reveal and reusable circular index |
| `index.html` | Content and semantic section structure |
| `app.js` | Existing article interactions and data-to-presentation adapter |
| `data.js`, `media.js`, `data/` | Article content, numerical data and media provenance |

Load `tokens.css` before `styles.css`, and `system.js` before a consuming app.
To reuse the system, replace content and data adapters, retain the primitive
classes, and override semantic tokens. The visual components do not fetch data.
The circular index accepts `{items, index, onSelect, label, selectLabel}`; each
item supplies a `label`. Values and selection state belong to the consuming app.

## Composition

- `.page-width`: 1600 px maximum, 32–48 px desktop gutters, 20 px mobile gutters.
- `.editorial-grid`: twelve desktop columns, eight tablet columns, one mobile column.
- `.technical-label`, `.eyebrow`: mono, 9–11 px, uppercase Latin labels with wide tracking.
- `.section-heading`: large left-aligned title plus a separate contextual column.
- `.button`, `.text-button`: rectangular control or lightweight text action.
- `.status-indicator`: accent mark paired with visible meaningful text.
- `.animation-card`: editorial media and caption columns, alternating placement;
  the legacy class name does not imply a bordered card container.
- `.chart-card`: open chart area with a top rule, title and caption.
- `.library-item`: numbered archive row, document type, title, filename and action.
- `.library-disclosure`: a native, initially closed `details` element. Its summary
  displays the archive count and an open/close label. Keyboard and pointer users
  can reveal the search, filters and file list; closing retains the current filter.
- `.about`: quiet dark close with broader spacing and reduced visual density.

The header, hero, section heading, media figure, chart panel, table, index row
and footer have distinct rhythms. Rounded container cards and shadows are not
used. The only circular controls are the frame index, where angular position
means discrete item order, not physical time or a cosmological trajectory.

## Type and color

Sans-serif display type contrasts with small mono metadata. Chinese content
uses the bundled ArticleSans subset, with system fallbacks. Display type uses
negative tracking; metadata uses positive tracking. Body copy is 15–16 px;
scientific captions and dense supporting notes are 11–14 px.

Warm off-white and charcoal carry the page. Safety orange marks selection,
focus, playback and current-frame state. `--orange-ink` supplies a darker
accessible text accent on light surfaces. Model data use charcoal, muted teal
and muted red. The fourth resolution series uses muted ochre. SVG series and
HTML legends read the same color tokens. Model names and tooltips remain
available so the figures do not depend exclusively on color.

Original scientific image pixels and their color scales remain unchanged.
Only interactive chart presentation consumes the new palette. No data are
resampled for this visual update.

## Interaction and accessibility

The header language button switches between Chinese and English. `locales.js`
holds the English catalog separately from presentation; `i18n.js` translates
text and accessible labels in place, including newly rendered chart captions.
Switching retains the existing controls, plot values, focus, video position and
archive disclosure state. Original scientific files are not translated.
The browser remembers the selected language when local storage is available;
`?lang=en` and `?lang=zh` override it for a visit. Chinese is the default.
Keep both scripts in offline distributions. The control is hidden without JavaScript.

Navigation is a normal link list. On mobile a real disclosure button exposes
all links; Escape closes it and returns focus. Without JavaScript the link list
remains visible. Scroll position sets `aria-current="location"` on the
corresponding link.

The circular index is synchronized with the existing projection state, supports
click, arrow keys, Home and End, and exposes selection through `aria-pressed`.
On mobile the existing linear timeline is the primary frame control.

Headings reveal once, by at most 16 px. No data panel, figure, control or long
section is hidden for scroll animation. IntersectionObserver is optional.
`prefers-reduced-motion` disables motion; a live change reveals pending headings.
No continuous motion, fake progress or autoplay is introduced. Print styles
reveal everything and remove interactive controls.

## Verification

All project verification runs through the existing Slurm wrapper. The visual
review saves desktop/mobile screenshots and checks navigation, index-state
synchronization, responsive widths from 320 to 1920 px, reduced motion and the
static no-script/no-image layout. The full explorer regression retains source
integrity, chart/data controls, projection pan/zoom, GIF/video and download checks.
Publication copies the exact validated runtime manifest to `gh-pages` only.
