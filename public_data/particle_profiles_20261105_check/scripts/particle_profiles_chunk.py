"""Chunked particle binning for halo density profiles (memory-light)."""
import argparse, json
from pathlib import Path

import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path("/oss06/data/project/tkcastrosim/HNHuang/project_big_sim/data")
SNAP = "0056"
SOAP = "SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"
RUNS = {
    "PL": ("PL/PL_25_1024", "PL_25_1024"),
    "kp1": ("bluetilted/kp_1_ms_1.5_25_1024", "kp_1_ms_1.5_25_1024"),
    "kp10": ("bluetilted/kp_10_ms_1.5_25_1024", "kp_10_ms_1.5_25_1024"),
}
TARGET_MASSES = [1e9, 1e10, 1e11, 1e12]
MASS_TOL = 0.2

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True, choices=list(RUNS))
ap.add_argument("--nhalo", type=int, default=10)
ap.add_argument("--chunk", type=int, default=4_000_000)
ap.add_argument("--outdir", required=True)
a = ap.parse_args()
OUT = Path(a.outdir); OUT.mkdir(parents=True, exist_ok=True)

rel, stem = RUNS[a.run]
run_dir = DATA / rel
with h5py.File(run_dir / SOAP, "r") as s:
    m200 = np.asarray(s["SO/200_mean/TotalMass"][:], float) * 1e10
    r200 = np.asarray(s["SO/200_mean/SORadius"][:], float)
    com_so = np.asarray(s["SO/200_mean/CentreOfMass"][:], float)
    com_bs = np.asarray(s["BoundSubhalo/CentreOfMass"][:], float)
    central = np.asarray(s["InputHalos/IsCentral"][:], int)
    box = float(np.asarray(s["Header"].attrs.get("BoxSize", 25.0)).ravel()[0])
print("box", box, "halos", m200.size, flush=True)

sel_halos = []          # (target_mass, idx)
for target in TARGET_MASSES:
    sel = np.where(central == 1)[0]
    keep = sel[np.abs(np.log10(m200[sel]) - np.log10(target)) < MASS_TOL]
    if keep.size == 0:
        continue
    keep = keep[np.argsort(np.abs(np.log10(m200[keep]) - np.log10(target)))][: a.nhalo]
    for idx in keep:
        sel_halos.append((target, int(idx)))
nh = len(sel_halos)
idx_arr = np.array([i for _, i in sel_halos])
print("selected halos:", nh, flush=True)

nbins = 20
edges = np.logspace(-2, 0, nbins + 1)
rgrid = edges[None, :] * r200[idx_arr][:, None]        # (nh, nbins+1)

hist_so = np.zeros((nh, nbins)); hist_bs = np.zeros((nh, nbins))
cnt_so = np.zeros((nh, nbins)); cnt_bs = np.zeros((nh, nbins))
com_so_s = com_so[idx_arr]; com_bs_s = com_bs[idx_arr]

with h5py.File(run_dir / f"{stem}_{SNAP}.hdf5", "r") as f:
    coords = f["PartType1/Coordinates"]
    masses = f["PartType1/Masses"]
    unit_len = float(np.asarray(f["Units"].attrs.get("Unit length in cgs (U_L)", 1.0)).ravel()[0]) / 3.0857e24
    unit_mass = float(np.asarray(f["Units"].attrs.get("Unit mass in cgs (U_M)", 1.0)).ravel()[0]) / 1.98892e33
    n_tot = coords.shape[0]
    print("particles", n_tot, "unit_len", unit_len, "unit_mass", unit_mass, flush=True)
    for start in range(0, n_tot, a.chunk):
        stop = min(start + a.chunk, n_tot)
        xyz = np.asarray(coords[start:stop], float) * unit_len
        m = np.asarray(masses[start:stop], float) * unit_mass
        for j in range(nh):
            for centres, hist in ((com_so_s, hist_so), (com_bs_s, hist_bs)):
                d = xyz - centres[j]
                d -= box * np.round(d / box)
                rad = np.sqrt(np.einsum("ij,ij->i", d, d))
                h, _ = np.histogram(rad, bins=rgrid[j], weights=m)
                hist[j] += h
                c, _ = np.histogram(rad, bins=rgrid[j])
                (cnt_so if hist is hist_so else cnt_bs)[j] += c
        if start % (a.chunk * 50) == 0:
            print(f"  chunk {start}/{n_tot}", flush=True)

vol = 4.0 / 3.0 * np.pi * (edges[1:]**3 - edges[:-1]**3)
results = []
for j, (target, idx) in enumerate(sel_halos):
    for key, hist in (("so", hist_so[j]), ("bs", hist_bs[j])):
        results.append({"run": a.run, "mass": target, "halo_index": idx, "centre": key,
                        "r_over_r200": (0.5 * (edges[1:] + edges[:-1])).tolist(),
                        "rho": (hist / (vol * r200[idx]**3)).tolist(),
                        "count": (cnt_so[j] if key == "so" else cnt_bs[j]).tolist()})
(OUT / f"profiles_{a.run}.json").write_text(json.dumps(results, indent=1))

fig, axes = plt.subplots(2, 2, figsize=(9, 7))
for ax, target in zip(axes.ravel(), TARGET_MASSES):
    for key, colour, label in (("so", "tab:blue", "centre: R200m COM"), ("bs", "tab:orange", "centre: bound-subhalo COM")):
        rows = [r for r in results if r["mass"] == target and r["centre"] == key]
        if not rows:
            continue
        arr = np.array([r["rho"] for r in rows])
        x = np.array(rows[0]["r_over_r200"])
        ax.plot(x, np.median(arr, 0), color=colour, lw=1.6, label=label)
        ax.fill_between(x, np.percentile(arr, 16, 0), np.percentile(arr, 84, 0), color=colour, alpha=0.18, lw=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$r/R_{200m}$"); ax.set_ylabel(r"$\rho$ [$M_\odot\,\mathrm{Mpc}^{-3}$]")
    ax.set_title(f"{a.run}: M200m ~ {target:.0e}", fontsize=9); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(OUT / f"density_profile_{a.run}.png", dpi=160)
print("wrote", OUT / f"density_profile_{a.run}.png", flush=True)
