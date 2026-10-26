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
