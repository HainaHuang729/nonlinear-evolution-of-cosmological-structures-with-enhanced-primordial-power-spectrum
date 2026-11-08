# Same-halo radial profile rerun

The included selection is the published Zenodo v1.1.0
`halo_catalog/radial_profile_selection.hdf5` (DOI 10.5281/zenodo.23788725).
Use it for both centres. It contains 1,198 selections over PL, kp1 and kp10
at the four manuscript masses. Each model is paired across centring choices
within its own halo sample.

Run one invocation per model in the existing cluster Python environment with
NumPy, h5py, Matplotlib and the project's Colossus available. Supply the z=0
SOAP catalog, SWIFT snapshot and the matching HBT SubSnap file(s) for that
model. Use all shards of that snapshot if split. Check the HBT coordinate unit
against the snapshot before supplying the conversion. A factor of 1 is only
appropriate when both are already in Mpc.

```sh
python public_data/scripts/recompute_paired_radial_profiles.py \
    --model BTKP10 --soap "$SOAP_FILE" --snapshot "$SNAPSHOT_FILE" \
    --hbt "$HBT_DIR"/SubSnap_056*.hdf5 --mb-to-mpc "$HBT_TO_MPC" \
    --output "$PAIRED_OUTPUT"
```

Repeat with the PL and BTKP1 files. Adjust the HBT filename pattern to the
actual layout. The script stops on missing or duplicate selected HBT IDs,
or if the supplied SOAP catalog does not match the archived selections.

Return the 12 reduced NPZ files and job logs. Each NPZ includes the exact
IDs, both centers, their periodic separation, individual densities, per-halo
Power03 radii, and integer shell counts. Count column zero is the sphere
inside the first displayed shell edge, 0.01 R200m. Columns 1–20 correspond
to the displayed shells. Compare recomputed COM medians to the released
tables before interpreting the paired MB differences. In particular, inspect
PL and kp10 near the high-mass convergence boundary and compare the empirical
offset distributions before deciding whether the earlier MB cache is usable.

## Manuscript inputs from Slurm job 2358490

The `cache/` directory contains the 12 most-bound-particle stacks for the
manuscript figure, with the original halo selections and 160 bootstrap
resamples (seed 12345). All selected TrackIds matched across the complete
HBT shard sets. The previous kp10 trial read only shard zero and fell back
to the center of mass for 350 of 398 selected halos. Recreating that fallback
with the paired measurements exactly reproduces the trial medians. The new
center-of-mass medians reproduce the released CSVs to relative precision
better than 5e-10. `kp10_pl_comparison.csv` compares the two uniform centering
choices and the earlier mixed-center calculation on the same radial grid.

The manuscript figure can be regenerated with `reproduce_all_figures.py`
or with the radial plotter alone. Run from the repository root with the
released custom Colossus on PYTHONPATH:

```sh
MPLBACKEND=Agg RADIAL_MANUSCRIPT_MB_LAYOUT=1 RADIAL_CENTRALS_ONLY=0 \
  RADIAL_PROFILE_CACHE_DIR="$PWD/public_data/particle_profiles_paired/cache" \
  RADIAL_OUTPUT_PATH=/tmp/halo-density-radial-mb-corrected.png \
  python public_data/scripts/bt_plot_halo_density_radial_trial_png.py
```
