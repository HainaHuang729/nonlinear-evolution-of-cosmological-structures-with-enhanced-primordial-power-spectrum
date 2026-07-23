# Compact Article Halo Catalog

## Scope

The compact catalog contains the per-halo inputs needed for the main halo
statistics in the article. It is distributed separately from the manuscript
source because the nine compressed HDF5 files total 74.2 MiB. The existing
`figure_data/` directory remains the smaller package for reproducing plotted
points directly.

The release does not contain full simulation snapshots, particle membership
files, or complete HBT-HERONS and SOAP catalogs. Those files are hundreds of
gigabytes per model and are not needed to reproduce the article measurements.

## Files

| File | Models | Contents |
| --- | --- | --- |
| `fof_hmf_source_*.hdf5` | PL, BT kp=1, BT kp=10 | Individual FOF groups used to calculate the halo mass function at snapshots 24, 27, 30, 32, 40, and 56. |
| `m200c_concentration_source_*.hdf5` | PL, BT kp=1, BT kp=10 | Individual SOAP halo masses, concentrations, and particle counts at the same six snapshots. |
| `mah_track_source_*.hdf5` | PL, BT kp=1 | Raw same-TrackId FOF mass histories for the seven final-mass samples in the mass-assembly figure. |
| `radial_profile_selection.hdf5` | PL, BT kp=1, BT kp=10 | Metadata for the halos selected for the direct particle radial profiles. |
| `catalog_manifest.csv` | All | File sizes and SHA-256 checksums. |

The file name suffixes `PL`, `BT_kp1`, and `BT_kp10` identify the three
simulation models. Every HDF5 file has `schema_version=1.0` and records the
model, units, selection, and source-file provenance in its attributes.

## Selections And Fields

### FOF halo mass function

The FOF files include halos with Warren-corrected masses from
`1e8` to `1e13 Msun`. Each snapshot group contains `source_row`, `group_id`,
`mass_fof_raw_msun`, `mass_fof_warren_msun`, and `particle_count`. Snapshot
attributes give the redshift, box size, dark-matter particle mass, and source
file.

### M200c mass function and concentration

The SOAP files include halos with positive `M200c` and at least 100 dark-matter
particles within `R200c`. Each snapshot group contains `source_row`,
`track_id`, `is_central`, `mass_m200c_msun`, `concentration_c200c`, and
`particle_count_m200c`. Invalid concentration values are retained so that the
article's concentration quality cuts can be applied explicitly.

### Mass-assembly histories

At redshift zero, halos are selected within 0.1 dex of seven Warren-corrected
FOF target masses from `3e8` to `3e11 Msun`. The files follow the selected
HBT-HERONS `track_id` values through snapshots 21--56. They contain the raw FOF
mass and particle-count histories, the snapshot redshifts, and the final-mass
selection metadata. `NaN` mass and zero particle count mark a missing
detection. Missing outputs are not filled, and the histories are not forced to
increase monotonically.

### Radial-profile sample

The radial-selection file records the redshift-zero halos used for the direct
particle profiles. Four `M200m` windows are centered on `1e10`, `10^10.5`,
`1e11`, and `10^11.5 Msun`, with a width of 20 percent. Each model and mass bin
contains at most 100 deterministically selected halos with at least 20
particles inside `R200m`. The fields include `track_id`, `is_central`,
`mass_m200m_msun`, `radius_r200m_mpc`, `particle_count_m200m`, and the
`SO/200_mean/CentreOfMass` position used to center the particle profiles.

## Reproduction And Validation

The extraction should be run through Slurm:

```bash
sbatch public_data/scripts/submit_extract_article_halo_catalog.sbatch
```

After obtaining the release directory, validate it against the reduced article
data with:

```bash
python public_data/scripts/validate_article_halo_catalog.py \
  /path/to/compact_catalog --article-root .
```

The 2026-07-23 release passed all checks: SHA-256 checksums for nine files, 540
published FOF mass-function points, 3,183,867 selected M200c rows, 336
mass-bin/snapshot assembly-history medians, and 1,198 radial-profile halo
selections. The release manifest is copied to
`figure_data/metadata/article_halo_catalog_manifest.csv` so the expected files
can be checked before download or analysis.
