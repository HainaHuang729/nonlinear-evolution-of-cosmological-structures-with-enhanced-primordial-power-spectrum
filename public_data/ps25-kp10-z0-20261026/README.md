# PS25 with the new kp10 z=0 phase pair (2026-10-26)

Measurement: phase_supplement_kp10_0056_job2288271 (Slurm 2288271), native 1024^3 NGP,
one V/N shot subtraction, no window deconvolution, exact-epoch arithmetic phase mean.
Snapshots: kp_10_ms_1.5_25_1024_0056.hdf5 vs kp10_inv_lowz_0001.hdf5 (a=1.0, z=0).

Plot: ps25_paper_format_job2289693 (Slurm 2289693), five phase supplements
(kp1_0040, kp10_0048, pl_0048, kp1_0056, kp10_0056), compact + original layout.

Files: figure, spectra.csv, ratios.csv, plot summary, measurement phase_pair.npz and summary.
No simulation snapshots are included.

## BT/PL variant (no HMcode, no Sim/HM row)

power-spectrum-25-btpl_20261026.png is drawn by plot_ps25_btpl.py: same colours/markers as the original
style module, BT/PL ratio row kept on the right-hand axis of each panel, HMcode curves and the
Sim/HM residual row removed. Text-overlap check reports 0 overlapping labels.

## Current manuscript figure

The manuscript uses `power-spectrum-btpl.png` at the repository root. Regenerate it from the released tables with:

```bash
python public_data/ps25-kp10-z0-20261026/plot_ps25_btpl.py
```

Use `--output PATH` for another destination. The selected 2026-10-29 layout uses a compact 2-by-2 arrangement, thin connecting lines with sparse open markers, the original black/blue/teal model colours (PL #000000, BT kp=1 #0072B2, BT kp=10 #009E73), and independent linear BT/PL axes for each redshift. Every displayed CSV sample is retained in the lines; no smoothing is applied. The power spectra use logarithmic axes with limits set separately for each redshift. The historical PNG files in this directory retain earlier layouts. The spectra are phase-pair averages, and the displayed interval is 10 times the box fundamental wavenumber to one quarter of the mesh Nyquist wavenumber. The measurement tables are unchanged. The accompanying manuscript edits revise two explanatory passages without changing numerical results.
