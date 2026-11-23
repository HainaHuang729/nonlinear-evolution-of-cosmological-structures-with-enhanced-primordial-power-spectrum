#!/usr/bin/env python3
"""Cluster-ready halo-matter bias estimator with paired-mode and block jackknife uncertainties.

Extends the leave-one-mode-out cross-power estimator in measure_bias.py with:
1. Paired-mode jackknife for phase-matched BT/PL bias ratios (capturing cosmic-variance
   cancellation between shared Fourier modes).
2. Grouped k-shell jackknife to test sensitivity to residual scale dependence across
   each wavenumber window.
3. Spatial 8-octant delete-one-octant jackknife on the real-space overdensity grids to
   capture mode coupling and super-sample covariance within the simulation volume.

Includes a ``--self-test`` mode that verifies all estimators on synthetic phase-matched
3D Gaussian fields locally without requiring cluster HDF5 files.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.fft import rfftn

try:
    import h5py
except ImportError:  # Allow local --self-test without HDF5 if needed
    h5py = None


DEFAULT_PROJECT = Path("/oss06/data/project/tkcastrosim/HNHuang/project_big_sim")
MODELS = {
    (25, "PL"): ("PL/PL_25_1024", "PL_25_1024"),
    (25, "BT"): ("bluetilted/kp_1_ms_1.5_25_1024", "kp_1_ms_1.5_25_1024"),
    (25, "BT10"): ("bluetilted/kp_10_ms_1.5_25_1024", "kp_10_ms_1.5_25_1024"),
    (256, "PL"): ("PL/PL_256_1024", "PL_1024"),
    (256, "BT"): ("bluetilted/kp_1_ms_1.5_256_1024", "kp_1_ms_1.5_256_1024"),
    (256, "BT10"): ("bluetilted/kp_10_ms_1.5_256_1024", "kp_10_ms_1.5_256_1024"),
}
GRID = 256
MPC_IN_CM = 3.0856775814913673e24
MSUN_IN_G = 1.98841e33
UNIT_ATTR = "Conversion factor to CGS (not including cosmological corrections)"
MASS_EDGES = 10.0 ** np.arange(8.1, 14.41, 0.30)


def scalar(group, key: str) -> float:
    return float(np.asarray(group.attrs[key]).flat[0])


def deposit_ngp(xyz: np.ndarray, box: float, grid: int = GRID) -> np.ndarray:
    """Deposit coordinates onto a periodic cubic NGP mesh."""
    index = np.floor(np.asarray(xyz, dtype=np.float64) * (grid / box)).astype(np.int32) % grid
    flat = (index[:, 0] * grid + index[:, 1]) * grid + index[:, 2]
    return np.bincount(flat, minlength=grid**3).astype(np.float64).reshape((grid, grid, grid))


def overdensity_from_counts(counts: np.ndarray) -> np.ndarray:
    """Convert raw mesh counts to zero-mean overdensity field delta = rho/rho_bar - 1."""
    mean_count = float(counts.mean(dtype=np.float64))
    if mean_count <= 0.0:
        raise ValueError("Grid has non-positive total count")
    return counts.astype(np.float64) / mean_count - 1.0


def fft_overdensity(delta: np.ndarray, workers: int = 4) -> np.ndarray:
    """Compute 3D rFFT of an overdensity grid."""
    return rfftn(delta, workers=workers)


def select_modes(
    box: float,
    *,
    grid: int = GRID,
    k_lo: float = 0.03,
    k_hi: float = 0.60,
) -> tuple[tuple[np.ndarray, np.ndarray, np.ndarray], np.ndarray, np.ndarray]:
    """Select unique upper-half-space Fourier modes and NGP window correction."""
    n_nyq = grid // 2
    nmax = min(n_nyq, int(np.ceil(k_hi * box / (2.0 * np.pi))))
    xy = np.arange(-nmax, nmax + 1)
    kz_max = min(n_nyq, nmax)
    x, y, z = np.meshgrid(xy, xy, np.arange(kz_max + 1), indexing="ij")
    # Exclude negative-frequency Hermitian duplicates on the kz=0 plane and Nyquist edge ambiguity.
    unique = (z > 0) | ((z == 0) & ((y > 0) | ((y == 0) & (x > 0))))
    k = np.sqrt(x * x + y * y + z * z) * (2.0 * np.pi / box)
    keep = unique & (k >= k_lo) & (k <= k_hi)
    x, y, z = x[keep], y[keep], z[keep]
    ngp = np.sinc(x / grid) * np.sinc(y / grid) * np.sinc(z / grid)
    return (x % grid, y % grid, z), k[keep], ngp


def jackknife_std(replicates: np.ndarray) -> float:
    """Standard delete-one jackknife standard deviation from N replicate estimates."""
    vals = np.asarray(replicates, dtype=np.float64)
    n = vals.size
    if n < 2:
        return float("nan")
    return float(np.sqrt((n - 1.0) / n * np.sum((vals - vals.mean()) ** 2)))


def jackknife_cov(rep_a: np.ndarray, rep_b: np.ndarray) -> float:
    """Jackknife covariance between two estimators evaluated on matched delete-one replicates."""
    a = np.asarray(rep_a, dtype=np.float64)
    b = np.asarray(rep_b, dtype=np.float64)
    if a.size != b.size or a.size < 2:
        return float("nan")
    n = a.size
    return float((n - 1.0) / n * np.sum((a - a.mean()) * (b - b.mean())))


def _group_assignments(k_vals: np.ndarray, n_groups: int) -> tuple[np.ndarray, int]:
    """Partition selected modes into contiguous sorted-k shells for grouped jackknife."""
    n_modes = k_vals.size
    g_eff = max(2, min(int(n_groups), n_modes))
    order = np.argsort(k_vals, kind="mergesort")
    groups = np.empty(n_modes, dtype=np.int32)
    for gid, chunk in enumerate(np.array_split(order, g_eff)):
        groups[chunk] = gid
    return groups, g_eff


def _window_replicates(
    mm: np.ndarray,
    hm: np.ndarray,
    k_vals: np.ndarray,
    n_shells: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return full bias, leave-one-mode-out replicates, and grouped k-shell replicates."""
    tot_mm = float(mm.sum())
    tot_hm = float(hm.sum())
    if tot_mm <= 0.0:
        raise ValueError("Zero total matter power in wavenumber window")
    bias = tot_hm / tot_mm
    mode_reps = (tot_hm - hm) / (tot_mm - mm)

    groups, g_eff = _group_assignments(k_vals, n_shells)
    shell_mm = np.bincount(groups, weights=mm, minlength=g_eff)
    shell_hm = np.bincount(groups, weights=hm, minlength=g_eff)
    shell_reps = (tot_hm - shell_hm) / (tot_mm - shell_mm)
    return bias, mode_reps, shell_reps


def octant_mode_spectra(
    delta_m: np.ndarray,
    delta_h: np.ndarray,
    index: tuple[np.ndarray, np.ndarray, np.ndarray],
    ngp: np.ndarray,
    *,
    deconvolve_ngp: bool = True,
    workers: int = 4,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute delete-one-octant cross/auto spectra on the 8 spatial sub-volumes."""
    grid = delta_m.shape[0]
    half = grid // 2
    mm_oct = np.empty((8, ngp.size), dtype=np.float64)
    hm_oct = np.empty((8, ngp.size), dtype=np.float64)
    denom = ngp if deconvolve_ngp else np.ones_like(ngp)

    # Periodic zero-masking of each octant scales mode variance by the kept fraction 7/8,
    # which cancels in the ratio hm/mm per octant replicate.
    oct_idx = 0
    for ix in (slice(0, half), slice(half, grid)):
        for iy in (slice(0, half), slice(half, grid)):
            for iz in (slice(0, half), slice(half, grid)):
                mask = np.ones((grid, grid, grid), dtype=np.float64)
                mask[ix, iy, iz] = 0.0
                m_k = fft_overdensity(delta_m * mask, workers=workers)[index].astype(np.complex128) / denom
                h_k = fft_overdensity(delta_h * mask, workers=workers)[index].astype(np.complex128) / denom
                mm_oct[oct_idx] = (m_k.real * m_k.real + m_k.imag * m_k.imag)
                hm_oct[oct_idx] = (h_k * m_k.conj()).real
                oct_idx += 1
    return mm_oct, hm_oct


def compute_single_window_stats(
    matter_k: np.ndarray,
    halo_k: np.ndarray,
    k_vals: np.ndarray,
    select: np.ndarray,
    volume: float,
    npart: int,
    *,
    grid: int = GRID,
    n_shells: int = 8,
    mm_oct: np.ndarray | None = None,
    hm_oct: np.ndarray | None = None,
) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    """Compute single-run bias and mode / shell / octant jackknife errors."""
    km = k_vals[select]
    m_sel = matter_k[select]
    h_sel = halo_k[select]
    mm = np.abs(m_sel) ** 2
    hm = (h_sel * m_sel.conj()).real
    bias, mode_reps, shell_reps = _window_replicates(mm, hm, km, n_shells)

    if mm_oct is not None and hm_oct is not None:
        oct_mm = mm_oct[:, select].sum(axis=1)
        oct_hm = hm_oct[:, select].sum(axis=1)
        oct_reps = oct_hm / oct_mm
        oct_err = jackknife_std(oct_reps)
    else:
        oct_reps = np.array([], dtype=np.float64)
        oct_err = float("nan")

    power = float(mm.mean()) * volume / (grid**6)
    stats = {
        "bias": bias,
        "bias_err_mode_jk": jackknife_std(mode_reps),
        "bias_err_shell_jk": jackknife_std(shell_reps),
        "bias_err_octant_jk": oct_err,
        "N_modes": int(km.size),
        "N_shells": int(shell_reps.size),
        "k_min": float(km.min()),
        "k_max": float(km.max()),
        "k_eff": float(np.average(km, weights=mm)),
        "matter_poisson_fraction": (volume / max(npart, 1)) / power if power > 0 else float("nan"),
    }
    reps = {"mode": mode_reps, "shell": shell_reps, "octant": oct_reps}
    return stats, reps


def compute_paired_ratio_stats(
    pl_stats: dict[str, float],
    pl_reps: dict[str, np.ndarray],
    bt_stats: dict[str, float],
    bt_reps: dict[str, np.ndarray],
) -> dict[str, float]:
    """Compute b_BT / b_PL with paired-mode, paired-shell, paired-octant, and uncorrelated errors."""
    b_pl = pl_stats["bias"]
    b_bt = bt_stats["bias"]
    ratio = b_bt / b_pl

    mode_ratio_reps = bt_reps["mode"] / pl_reps["mode"]
    shell_ratio_reps = bt_reps["shell"] / pl_reps["shell"]

    sig_pl = pl_stats["bias_err_mode_jk"]
    sig_bt = bt_stats["bias_err_mode_jk"]
    uncorr_err = ratio * float(np.sqrt((sig_bt / b_bt) ** 2 + (sig_pl / b_pl) ** 2))
    paired_mode_err = jackknife_std(mode_ratio_reps)
    paired_shell_err = jackknife_std(shell_ratio_reps)

    cov_mode = jackknife_cov(bt_reps["mode"], pl_reps["mode"])
    corr_mode = cov_mode / (sig_bt * sig_pl) if sig_bt > 0 and sig_pl > 0 else float("nan")

    if bt_reps["octant"].size == 8 and pl_reps["octant"].size == 8:
        paired_octant_err = jackknife_std(bt_reps["octant"] / pl_reps["octant"])
    else:
        paired_octant_err = float("nan")

    return {
        "ratio_bt_over_pl": ratio,
        "ratio_err_paired_mode": paired_mode_err,
        "ratio_err_paired_shell": paired_shell_err,
        "ratio_err_paired_octant": paired_octant_err,
        "ratio_err_uncorr": uncorr_err,
        "mode_replicate_corr": corr_mode,
        "error_reduction_factor": paired_mode_err / uncorr_err if uncorr_err > 0 else float("nan"),
    }


def load_halos(
    folder: Path,
    snap: int,
    redshift: float,
    h: float,
    length: float,
    mass_definition: str,
    soap_dir: Path | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if h5py is None:
        raise RuntimeError("h5py is required to read SWIFT/SOAP HDF5 catalogs")
    if mass_definition == "fof":
        path = folder / f"fof_output_{snap:04d}.hdf5"
        mass_key, centre_key, size_key = "Groups/Masses", "Groups/Centres", "Groups/Sizes"
    else:
        soap_dir = soap_dir or folder / "SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus"
        path = soap_dir / f"halo_properties_{snap:04d}.hdf5"
        mass_key = "SO/200_mean/TotalMass"
        centre_key = "InputHalos/HaloCentre"
        size_key = "SO/200_mean/NumberOfDarkMatterParticles"

    with h5py.File(path, "r") as f:
        if not np.isclose(scalar(f["Header"], "Redshift"), redshift):
            raise ValueError(f"Catalog and snapshot redshift differ: {path}")
        keep = slice(None) if mass_definition == "fof" else f["InputHalos/IsCentral"][:] == 1
        mass = f[mass_key][:].reshape(-1)[keep].astype(np.float64)
        mass *= scalar(f[mass_key], UNIT_ATTR) * h / MSUN_IN_G
        centres = f[centre_key][:][keep]
        centres *= scalar(f[centre_key], UNIT_ATTR) / MPC_IN_CM / length
        sizes = f[size_key][:].reshape(-1)[keep]
    return mass, centres, sizes


def load_snapshot_matter(
    folder: Path,
    stem: str,
    snap: int,
    box_label: int,
    grid: int = GRID,
) -> dict[str, object]:
    if h5py is None:
        raise RuntimeError("h5py is required to read SWIFT snapshot HDF5 files")
    with h5py.File(folder / f"{stem}_{snap:04d}.hdf5", "r") as f:
        h = scalar(f["Cosmology"], "h")
        box = scalar(f["Header"], "BoxSize")
        redshift = scalar(f["Header"], "Redshift")
        coords = f["PartType1/Coordinates"]
        length = scalar(coords, UNIT_ATTR) / MPC_IN_CM
        box_h = box * length * h
        if not np.isclose(box_h, box_label, rtol=1e-5):
            raise ValueError(f"Unexpected box size {box_h} vs {box_label}")
        particle_masses = f["PartType1/Masses"]
        mp = float(particle_masses[0]) * scalar(particle_masses, UNIT_ATTR) * h / MSUN_IN_G
        npart = len(coords)
        counts = np.zeros((grid, grid, grid), dtype=np.float64)
        for start in range(0, npart, 8_000_000):
            counts += deposit_ngp(coords[start : start + 8_000_000], box, grid=grid)
        if counts.sum(dtype=np.float64) != npart:
            raise ValueError("Matter deposition did not conserve particle count")
    return {
        "h": h,
        "box": box,
        "box_h": box_h,
        "length": length,
        "redshift": redshift,
        "mp": mp,
        "npart": npart,
        "delta_m": overdensity_from_counts(counts),
    }


def run_paired_snapshot(
    project_root: Path,
    box_label: int,
    bt_model: str,
    snap: int,
    mass_definition: str,
    output_dir: Path,
    *,
    pl_soap_dir: Path | None = None,
    bt_soap_dir: Path | None = None,
    n_shells: int = 8,
    with_octants: bool = True,
) -> Path:
    """Measure matched single-model and paired-mode BT/PL bias statistics at one snapshot."""
    pl_rel, pl_stem = MODELS[box_label, "PL"]
    bt_rel, bt_stem = MODELS[box_label, bt_model]
    pl_folder = project_root / "data" / pl_rel
    bt_folder = project_root / "data" / bt_rel

    snap_pl = load_snapshot_matter(pl_folder, pl_stem, snap, box_label)
    snap_bt = load_snapshot_matter(bt_folder, bt_stem, snap, box_label)
    if not np.isclose(snap_pl["redshift"], snap_bt["redshift"], rtol=1e-5, atol=1e-5):
        raise ValueError("PL and BT snapshot redshifts differ")

    index, k, ngp = select_modes(float(snap_pl["box_h"]))
    matter_pl_k = fft_overdensity(snap_pl["delta_m"])[index].astype(np.complex128) / ngp
    matter_bt_k = fft_overdensity(snap_bt["delta_m"])[index].astype(np.complex128) / ngp

    mass_pl, cen_pl, size_pl = load_halos(
        pl_folder, snap, float(snap_pl["redshift"]), float(snap_pl["h"]), float(snap_pl["length"]),
        mass_definition, pl_soap_dir,
    )
    mass_bt, cen_bt, size_bt = load_halos(
        bt_folder, snap, float(snap_bt["redshift"]), float(snap_bt["h"]), float(snap_bt["length"]),
        mass_definition, bt_soap_dir,
    )

    windows = [("matched", 0.25, 0.60)]
    if box_label == 256:
        windows.insert(0, ("large_scale", 0.03, 0.15))

    single_rows: list[dict[str, object]] = []
    paired_rows: list[dict[str, object]] = []
    volume = float(snap_pl["box_h"]) ** 3
    mp_floor = 100.0 * max(float(snap_pl["mp"]), float(snap_bt["mp"]))

    for m0, m1 in zip(MASS_EDGES[:-1], MASS_EDGES[1:]):
        if m0 < mp_floor:
            continue
        keep_pl = (mass_pl >= m0) & (mass_pl < m1) & (size_pl >= 100)
        keep_bt = (mass_bt >= m0) & (mass_bt < m1) & (size_bt >= 100)
        n_pl, n_bt = int(keep_pl.sum()), int(keep_bt.sum())

        pl_halo_delta = overdensity_from_counts(deposit_ngp(cen_pl[keep_pl], float(snap_pl["box"]))) if n_pl >= 200 else None
        bt_halo_delta = overdensity_from_counts(deposit_ngp(cen_bt[keep_bt], float(snap_bt["box"]))) if n_bt >= 200 else None

        pl_halo_k = fft_overdensity(pl_halo_delta)[index].astype(np.complex128) / ngp if pl_halo_delta is not None else None
        bt_halo_k = fft_overdensity(bt_halo_delta)[index].astype(np.complex128) / ngp if bt_halo_delta is not None else None

        if with_octants and pl_halo_delta is not None:
            pl_mm_oct, pl_hm_oct = octant_mode_spectra(snap_pl["delta_m"], pl_halo_delta, index, ngp)
        else:
            pl_mm_oct = pl_hm_oct = None
        if with_octants and bt_halo_delta is not None:
            bt_mm_oct, bt_hm_oct = octant_mode_spectra(snap_bt["delta_m"], bt_halo_delta, index, ngp)
        else:
            bt_mm_oct = bt_hm_oct = None

        for window, lo, hi in windows:
            sel = (k >= lo) & (k <= hi)
            pl_res = bt_res = None
            if pl_halo_k is not None:
                s_pl, r_pl = compute_single_window_stats(
                    matter_pl_k, pl_halo_k, k, sel, volume, int(snap_pl["npart"]),
                    n_shells=n_shells, mm_oct=pl_mm_oct, hm_oct=pl_hm_oct,
                )
                pl_res = (s_pl, r_pl)
                single_rows.append(
                    dict(
                        model="PL", box_hMpc=box_label, snap=snap, redshift=snap_pl["redshift"],
                        mass_lo=m0, mass_hi=m1, mass_median=float(np.median(mass_pl[keep_pl])),
                        N_halos=n_pl, window=window, **s_pl,
                    )
                )
            if bt_halo_k is not None:
                s_bt, r_bt = compute_single_window_stats(
                    matter_bt_k, bt_halo_k, k, sel, volume, int(snap_bt["npart"]),
                    n_shells=n_shells, mm_oct=bt_mm_oct, hm_oct=bt_hm_oct,
                )
                bt_res = (s_bt, r_bt)
                single_rows.append(
                    dict(
                        model=bt_model, box_hMpc=box_label, snap=snap, redshift=snap_bt["redshift"],
                        mass_lo=m0, mass_hi=m1, mass_median=float(np.median(mass_bt[keep_bt])),
                        N_halos=n_bt, window=window, **s_bt,
                    )
                )
            if pl_res is not None and bt_res is not None:
                paired = compute_paired_ratio_stats(pl_res[0], pl_res[1], bt_res[0], bt_res[1])
                paired_rows.append(
                    dict(
                        bt_model=bt_model, box_hMpc=box_label, snap=snap, redshift=snap_pl["redshift"],
                        mass_lo=m0, mass_hi=m1, N_halos_PL=n_pl, N_halos_BT=n_bt, window=window,
                        b_PL=pl_res[0]["bias"], b_BT=bt_res[0]["bias"], **paired,
                    )
                )

    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = "bias" if mass_definition == "fof" else "bias_m200m"
    single_path = output_dir / f"{prefix}_{box_label}_PL_{bt_model}_{snap:04d}_jackknife.csv"
    paired_path = output_dir / f"{prefix}_{box_label}_{bt_model}_over_PL_{snap:04d}_paired.csv"
    for path, rows in ((single_path, single_rows), (paired_path, paired_rows)):
        if not rows:
            continue
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    return paired_path


def run_self_test() -> None:
    """Verify paired-mode, k-shell, and 8-octant jackknife on synthetic phase-matched 3D fields."""
    rng = np.random.default_rng(20261123)
    grid = 32
    box = 256.0
    kx = np.fft.fftfreq(grid, d=box / grid) * (2.0 * np.pi)
    ky = kx
    kz = np.fft.rfftfreq(grid, d=box / grid) * (2.0 * np.pi)
    kk = np.sqrt(kx[:, None, None] ** 2 + ky[None, :, None] ** 2 + kz[None, None, :] ** 2)

    # Generate shared Gaussian linear phases plus small-scale model difference and halo shot noise.
    white = rng.normal(size=(grid, grid, grid))
    delta_base_k = np.fft.rfftn(white) / (1.0 + (kk / 0.12) ** 2)
    delta_base_k[0, 0, 0] = 0.0
    delta_m_pl = np.fft.irfftn(delta_base_k, s=(grid, grid, grid), axes=(0, 1, 2))
    delta_m_bt = np.fft.irfftn(delta_base_k * (1.0 + 0.05 * (kk / 0.15)), s=(grid, grid, grid), axes=(0, 1, 2))

    # Give halos strong cosmic-mode bias + moderate Poisson noise so shared modes drive b_PL & b_BT together.
    b_pl_true, b_bt_true = 1.20, 0.96
    noise_pl = rng.normal(scale=0.18, size=(grid, grid, grid))
    noise_bt = rng.normal(scale=0.18, size=(grid, grid, grid))
    delta_h_pl = b_pl_true * delta_m_pl + noise_pl - noise_pl.mean()
    delta_h_bt = b_bt_true * delta_m_bt + noise_bt - noise_bt.mean()

    index, k, ngp = select_modes(box, grid=grid, k_lo=0.03, k_hi=0.15)
    sel = (k >= 0.03) & (k <= 0.15)
    m_pl_k = fft_overdensity(delta_m_pl + 1.0 - 1.0, workers=1)[index].astype(np.complex128)
    h_pl_k = fft_overdensity(delta_h_pl, workers=1)[index].astype(np.complex128)
    m_bt_k = fft_overdensity(delta_m_bt, workers=1)[index].astype(np.complex128)
    h_bt_k = fft_overdensity(delta_h_bt, workers=1)[index].astype(np.complex128)

    pl_mm_oct, pl_hm_oct = octant_mode_spectra(delta_m_pl, delta_h_pl, index, ngp, deconvolve_ngp=False, workers=1)
    bt_mm_oct, bt_hm_oct = octant_mode_spectra(delta_m_bt, delta_h_bt, index, ngp, deconvolve_ngp=False, workers=1)

    s_pl, r_pl = compute_single_window_stats(
        m_pl_k, h_pl_k, k, sel, box**3, grid**3, grid=grid, n_shells=6, mm_oct=pl_mm_oct, hm_oct=pl_hm_oct
    )
    s_bt, r_bt = compute_single_window_stats(
        m_bt_k, h_bt_k, k, sel, box**3, grid**3, grid=grid, n_shells=6, mm_oct=bt_mm_oct, hm_oct=bt_hm_oct
    )
    paired = compute_paired_ratio_stats(s_pl, r_pl, s_bt, r_bt)

    assert np.isfinite(s_pl["bias_err_mode_jk"]) and s_pl["bias_err_mode_jk"] > 0
    assert np.isfinite(s_pl["bias_err_shell_jk"]) and s_pl["bias_err_shell_jk"] > 0
    assert np.isfinite(s_pl["bias_err_octant_jk"]) and s_pl["bias_err_octant_jk"] > 0
    assert np.isfinite(paired["ratio_err_paired_mode"]) and paired["ratio_err_paired_mode"] > 0
    assert paired["error_reduction_factor"] < 1.0, (
        f"Expected paired variance cancellation (<1), got {paired['error_reduction_factor']:.3f}"
    )

    print(
        f"SELF_TEST_OK: N_modes={s_pl['N_modes']} b_PL={s_pl['bias']:.4f}+-{s_pl['bias_err_mode_jk']:.4f} "
        f"(shell={s_pl['bias_err_shell_jk']:.4f}, oct={s_pl['bias_err_octant_jk']:.4f}) | "
        f"R={paired['ratio_bt_over_pl']:.4f} paired_mode={paired['ratio_err_paired_mode']:.4f} vs "
        f"uncorr={paired['ratio_err_uncorr']:.4f} (corr={paired['mode_replicate_corr']:.3f}, "
        f"reduction={paired['error_reduction_factor']:.3f})"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run synthetic paired-field self-test and exit.")
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--box", type=int, choices=(25, 256), default=256)
    parser.add_argument("--bt-model", choices=("BT", "BT10"), default="BT")
    parser.add_argument("--snap", type=int, default=56)
    parser.add_argument("--mass-def", choices=("fof", "m200m"), default="m200m")
    parser.add_argument("--output-dir", type=Path, default=Path("./bias_paired_out"))
    parser.add_argument("--pl-soap-dir", type=Path, default=None)
    parser.add_argument("--bt-soap-dir", type=Path, default=None)
    parser.add_argument("--n-shells", type=int, default=8)
    parser.add_argument("--no-octants", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    out_path = run_paired_snapshot(
        args.project_root,
        args.box,
        args.bt_model,
        args.snap,
        args.mass_def,
        args.output_dir,
        pl_soap_dir=args.pl_soap_dir,
        bt_soap_dir=args.bt_soap_dir,
        n_shells=args.n_shells,
        with_octants=not args.no_octants,
    )
    print(f"Saved paired jackknife results: {out_path}")


if __name__ == "__main__":
    main()
