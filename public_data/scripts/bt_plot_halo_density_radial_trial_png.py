#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trial particle-binned median radial density profiles for PL/BT halos.

This diagnostic is intentionally separate from the production halo-density plot.
It measures DM particle mass in spherical shells around SOAP SO/200_mean centres,
then stacks the radial profiles by taking the median in each mass bin.
"""

import os
import sys
from pathlib import Path

import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

SCRIPT_PATH = Path(__file__).resolve()
if str(SCRIPT_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PATH.parent))

from bt_plot_halo_density_profile_png import (  # noqa: E402
    DATA_ROOT,
    PAPERPLOT_ROOT,
    PANEL_COLUMNS,
    H0,
    omega_m,
    THEORY_CONCENTRATION_LABEL,
    THEORY_PS_SPECS,
    calculate_critical_density,
    calculate_theory_nfw_profile,
    calculate_ratio_profile,
    apply_journal_style,
    format_axes,
    save_publication_figure,
    JOURNAL_COLORS,
)


TARGET_MASSES = [1e10, 10.0**10.5, 1e11, 10.0**11.5]

MODEL_SPECS = [
    (
        "PL",
        DATA_ROOT / "PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5",
        DATA_ROOT / "PL/PL_25_1024/PL_25_1024_0056.hdf5",
        JOURNAL_COLORS["black"],
    ),
    (
        "BTKP1",
        DATA_ROOT / "bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5",
        DATA_ROOT / "bluetilted/kp_1_ms_1.5_25_1024/kp_1_ms_1.5_25_1024_0056.hdf5",
        JOURNAL_COLORS["blue"],
    ),
    (
        "BTKP10",
        DATA_ROOT / "bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5",
        DATA_ROOT / "bluetilted/kp_10_ms_1.5_25_1024/kp_10_ms_1.5_25_1024_0056.hdf5",
        JOURNAL_COLORS["green"],
    ),
]

RADIAL_MAX_HALOS_PER_BIN = int(os.environ.get("RADIAL_MAX_HALOS_PER_BIN", "12"))
RADIAL_BINS = np.logspace(-2.0, 0.0, 21)
RADIAL_X = np.sqrt(RADIAL_BINS[:-1] * RADIAL_BINS[1:])
RADIAL_BOOTSTRAPS = int(os.environ.get("RADIAL_BOOTSTRAPS", "160"))
RADIAL_CENTRALS_ONLY = os.environ.get("RADIAL_CENTRALS_ONLY", "0") == "1"
RADIAL_PARTICLE_CHUNK = int(os.environ.get("RADIAL_PARTICLE_CHUNK", "250000"))
RADIAL_CACHE_DIR_ENV = os.environ.get("RADIAL_PROFILE_CACHE_DIR")
RADIAL_PROFILE_CACHE_DIR = Path(RADIAL_CACHE_DIR_ENV).expanduser().resolve() if RADIAL_CACHE_DIR_ENV else None
RADIAL_ONLY_LABELS_ENV = os.environ.get("RADIAL_ONLY_LABELS", "")
RADIAL_ONLY_LABELS = {s.strip() for s in RADIAL_ONLY_LABELS_ENV.split(",") if s.strip()}
RADIAL_ONLY_MASSES_ENV = os.environ.get("RADIAL_ONLY_MASSES", "")
RADIAL_ONLY_MASSES = [
    float(s.strip())
    for s in RADIAL_ONLY_MASSES_ENV.split(",")
    if s.strip()
]
RADIAL_OUTPUT_BASENAME = os.environ.get("RADIAL_OUTPUT_BASENAME", "halo-density-radial-trial.png")
POWER_KAPPA_THRESHOLD = float(os.environ.get("POWER_KAPPA_THRESHOLD", "0.6"))
POWER_CRITERION_LABEL = os.environ.get("POWER_CRITERION_LABEL", "Power03")
POWER_REFERENCE_OVERDENSITY_CRIT = float(
    os.environ.get("POWER_REFERENCE_OVERDENSITY_CRIT", str(200.0 * omega_m))
)
RHO_CRIT_MSUN_KPC3 = calculate_critical_density(H0) / 1.0e9


def load_soap_catalog(path):
    """Load SO/200_mean fields needed for particle-binned profiles."""
    with h5py.File(path, "r") as f:
        m200 = np.asarray(f["/SO/200_mean/TotalMass"], dtype=float) * 1.0e10
        r200_mpc = np.asarray(f["/SO/200_mean/SORadius"], dtype=float)
        centre_mpc = np.asarray(f["/SO/200_mean/CentreOfMass"], dtype=float)
        n200 = np.asarray(f["/SO/200_mean/NumberOfDarkMatterParticles"], dtype=float)
        is_central = np.asarray(f["/InputHalos/IsCentral"], dtype=bool)
    return {
        "M200": m200,
        "R200_mpc": r200_mpc,
        "Centre_mpc": centre_mpc,
        "N200": n200,
        "IsCentral": is_central,
    }


def select_mass_bin_halos(catalog, target_mass, max_halos):
    """Pick a reproducible subset for the trial particle radial stack."""
    m200 = catalog["M200"]
    r200 = catalog["R200_mpc"]
    n200 = catalog["N200"]
    mask = (
        (m200 >= 0.8 * target_mass)
        & (m200 <= 1.2 * target_mass)
        & np.isfinite(r200)
        & (r200 > 0.0)
        & np.isfinite(n200)
        & (n200 >= 20)
    )
    if RADIAL_CENTRALS_ONLY:
        mask &= catalog["IsCentral"]

    idx = np.flatnonzero(mask)
    if idx.size > max_halos:
        rng = np.random.default_rng(int(np.log10(target_mass) * 1000) + 2026)
        idx = np.sort(rng.choice(idx, size=max_halos, replace=False))
    return idx


def overlapping_cells(center, radius, cell_mins, cell_maxs, box_size):
    """Return SWIFT cell indices whose periodic AABB intersects the sphere."""
    min_dist2 = np.full(cell_mins.shape[0], np.inf, dtype=float)
    shifts = (-1.0, 0.0, 1.0)
    for sx in shifts:
        for sy in shifts:
            for sz in shifts:
                shift = np.array([sx * box_size[0], sy * box_size[1], sz * box_size[2]])
                lo = cell_mins + shift
                hi = cell_maxs + shift
                below = np.maximum(lo - center, 0.0)
                above = np.maximum(center - hi, 0.0)
                delta = below + above
                min_dist2 = np.minimum(min_dist2, np.einsum("ij,ij->i", delta, delta))
    return np.flatnonzero(min_dist2 <= radius * radius)


def power_radius_from_counts(power_shell_count, r200_mpc, mass_msun):
    """Power et al.-style convergence radius from enclosed particle counts."""
    n_enc = np.cumsum(power_shell_count).astype(float)
    radius_kpc = RADIAL_BINS * r200_mpc * 1000.0
    volume_kpc3 = (4.0 * np.pi / 3.0) * radius_kpc**3
    mass_enc = n_enc * mass_msun
    rho_bar = mass_enc / volume_kpc3
    valid = (n_enc > 1.0) & (rho_bar > 0.0) & np.isfinite(rho_bar)

    kappa = np.full_like(n_enc, np.nan, dtype=float)
    kappa[valid] = (
        n_enc[valid]
        / (8.0 * np.log(n_enc[valid]))
        * np.sqrt(POWER_REFERENCE_OVERDENSITY_CRIT / (rho_bar[valid] / RHO_CRIT_MSUN_KPC3))
    )

    crossed = np.flatnonzero(valid & (kappa >= POWER_KAPPA_THRESHOLD))
    if crossed.size == 0:
        return RADIAL_BINS[-1] if np.any(valid) else np.nan

    j = int(crossed[0])
    if j == 0:
        return float(RADIAL_BINS[0])

    i = j - 1
    while i >= 0 and not valid[i]:
        i -= 1
    if i < 0 or kappa[i] >= POWER_KAPPA_THRESHOLD or kappa[j] <= kappa[i] or kappa[i] <= 0.0:
        return float(RADIAL_BINS[j])

    log_x0, log_x1 = np.log(RADIAL_BINS[i]), np.log(RADIAL_BINS[j])
    log_k0, log_k1 = np.log(kappa[i]), np.log(kappa[j])
    frac = (np.log(POWER_KAPPA_THRESHOLD) - log_k0) / (log_k1 - log_k0)
    return float(np.exp(log_x0 + frac * (log_x1 - log_x0)))


def halo_particle_profile(snapshot, center, r200_mpc, cell_mins, cell_maxs, offsets, counts):
    """Measure one halo profile from DM particles in intersecting SWIFT cells."""
    coords_ds = snapshot["/PartType1/Coordinates"]
    mass_msun = float(np.median(snapshot["/PartType1/Masses"][:2048])) * 1.0e10
    box_size = np.asarray(snapshot["/Header"].attrs["BoxSize"], dtype=float)
    edges_mpc = RADIAL_BINS * r200_mpc
    power_edges_mpc = np.concatenate(([0.0], edges_mpc))
    shell_vol_kpc3 = (4.0 * np.pi / 3.0) * ((edges_mpc[1:] * 1000.0) ** 3 - (edges_mpc[:-1] * 1000.0) ** 3)
    power_shell_count = np.zeros(RADIAL_BINS.size, dtype=float)

    for cell in overlapping_cells(center, r200_mpc, cell_mins, cell_maxs, box_size):
        offset = int(offsets[cell])
        count = int(counts[cell])
        if count <= 0:
            continue
        end = offset + count
        for start in range(offset, end, RADIAL_PARTICLE_CHUNK):
            stop = min(start + RADIAL_PARTICLE_CHUNK, end)
            coords = np.asarray(coords_ds[start:stop], dtype=float)
            dx = coords - center
            dx -= box_size * np.rint(dx / box_size)
            radius = np.sqrt(np.einsum("ij,ij->i", dx, dx))
            in_power = radius < edges_mpc[-1]
            if not np.any(in_power):
                continue
            hist, _ = np.histogram(radius[in_power], bins=power_edges_mpc)
            power_shell_count += hist.astype(float)

    shell_mass = power_shell_count[1:] * mass_msun
    rho = shell_mass / shell_vol_kpc3
    rho[rho <= 0.0] = np.nan
    power_radius = power_radius_from_counts(power_shell_count, r200_mpc, mass_msun)
    return rho, power_radius


def particle_radial_stack(snapshot_path, catalog, halo_idx):
    """Median stack of particle-binned profiles for selected halos."""
    if halo_idx.size == 0:
        return None, None, None, None, None

    profiles = []
    power_radii = []
    with h5py.File(snapshot_path, "r") as snap:
        cell_mins = np.asarray(snap["/Cells/MinPositions/PartType1"], dtype=float)
        cell_maxs = np.asarray(snap["/Cells/MaxPositions/PartType1"], dtype=float)
        offsets = np.asarray(snap["/Cells/OffsetsInFile/PartType1"], dtype=np.int64)
        counts = np.asarray(snap["/Cells/Counts/PartType1"], dtype=np.int64)
        for i, row in enumerate(halo_idx, start=1):
            if i % 10 == 0 or i == halo_idx.size:
                print(f"    measured {i}/{halo_idx.size} halos")
            profile, power_radius = halo_particle_profile(
                snap,
                catalog["Centre_mpc"][row],
                catalog["R200_mpc"][row],
                cell_mins,
                cell_maxs,
                offsets,
                counts,
            )
            profiles.append(profile)
            power_radii.append(power_radius)

    rho = np.asarray(profiles, dtype=float)
    rho_med = np.nanmedian(rho, axis=0)
    if rho.shape[0] > 1:
        rng = np.random.default_rng(12345)
        boot_idx = rng.integers(0, rho.shape[0], size=(RADIAL_BOOTSTRAPS, rho.shape[0]))
        boot_med = np.nanmedian(rho[boot_idx, :], axis=1)
        rho_lo, rho_hi = np.nanpercentile(boot_med, [16.0, 84.0], axis=0)
    else:
        rho_lo = rho_med.copy()
        rho_hi = rho_med.copy()
    power_radius = float(np.nanmedian(np.asarray(power_radii, dtype=float)))
    return RADIAL_X, rho_med, rho_lo, rho_hi, power_radius


def mass_label_text(target_mass, nsample):
    return rf"$\log_{{10}}M_{{200m}}={np.log10(target_mass):.1f}$"


def sample_label_text(sample_counts):
    counts = [int(n) for n in sample_counts if n]
    if not counts:
        return "particle radial median"
    if min(counts) == max(counts):
        return rf"particle radial median, $N={min(counts)}$"
    return rf"particle radial median, $N={min(counts)}$--{max(counts)}"


def safe_label(label):
    return label.replace("(", "").replace(")", "").replace("/", "_").replace(" ", "_")


def power_threshold_cache_tag():
    if np.isclose(POWER_KAPPA_THRESHOLD, 0.6, rtol=0.0, atol=1.0e-12):
        return ""
    tag = f"{POWER_KAPPA_THRESHOLD:g}".replace("-", "m").replace(".", "p")
    return f"_K{tag}"


def power_reference_cache_tag():
    default_ref = 200.0 * omega_m
    if np.isclose(POWER_REFERENCE_OVERDENSITY_CRIT, default_ref, rtol=0.0, atol=1.0e-12):
        return ""
    tag = f"{POWER_REFERENCE_OVERDENSITY_CRIT:g}".replace("-", "m").replace(".", "p")
    return f"_D{tag}"


def profile_cache_path(label, target_mass):
    if RADIAL_PROFILE_CACHE_DIR is None:
        return None
    sample_tag = "centrals" if RADIAL_CENTRALS_ONLY else "all"
    return (
        RADIAL_PROFILE_CACHE_DIR
        / (
            f"{safe_label(label)}_M{target_mass:.0e}_N{RADIAL_MAX_HALOS_PER_BIN}_"
            f"B{RADIAL_BOOTSTRAPS}{power_threshold_cache_tag()}{power_reference_cache_tag()}_{sample_tag}.npz"
        )
    )


def load_cached_profile(label, target_mass):
    path = profile_cache_path(label, target_mass)
    if path is None or not path.exists():
        return None, None
    data = np.load(path)
    if "power_radius" not in data.files:
        return None, None
    profile = (data["x"], data["rho_med"], data["rho_lo"], data["rho_hi"], float(data["power_radius"]))
    return profile, int(data["nhalo"])


def save_cached_profile(label, target_mass, profile, nhalo):
    path = profile_cache_path(label, target_mass)
    if path is None or profile[0] is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    x, rho_med, rho_lo, rho_hi, power_radius = profile
    np.savez_compressed(
        path,
        x=x,
        rho_med=rho_med,
        rho_lo=rho_lo,
        rho_hi=rho_hi,
        power_radius=np.asarray(power_radius, dtype=float),
        power_kappa_threshold=np.asarray(POWER_KAPPA_THRESHOLD, dtype=float),
        power_reference_overdensity_crit=np.asarray(POWER_REFERENCE_OVERDENSITY_CRIT, dtype=float),
        nhalo=np.asarray(nhalo, dtype=int),
    )
    print(f"    cached {path}")


def compute_or_load_profile(label, snapshot_path, catalog, target_mass):
    if RADIAL_ONLY_MASSES and not any(np.isclose(target_mass, m) for m in RADIAL_ONLY_MASSES):
        return (None, None, None, None, None), 0
    cached, nhalo = load_cached_profile(label, target_mass)
    if cached is not None:
        print(f"{label} M={target_mass:.2e}: loaded cached radial sample {nhalo}")
        return cached, nhalo
    if RADIAL_ONLY_LABELS and label not in RADIAL_ONLY_LABELS:
        print(f"{label} M={target_mass:.2e}: skipped, cache missing")
        return (None, None, None, None, None), 0

    halo_idx = select_mass_bin_halos(catalog, target_mass, RADIAL_MAX_HALOS_PER_BIN)
    print(f"{label} M={target_mass:.2e}: radial sample {halo_idx.size}")
    profile = particle_radial_stack(snapshot_path, catalog, halo_idx)
    save_cached_profile(label, target_mass, profile, halo_idx.size)
    return profile, halo_idx.size


def plot_trial():
    apply_journal_style(base_fontsize=11.2)
    catalogs = {}
    for label, soap_path, _, _ in MODEL_SPECS:
        catalogs[label] = load_soap_catalog(soap_path)

    n_panels = len(TARGET_MASSES)
    n_cols = min(PANEL_COLUMNS, n_panels)
    n_rows = int(np.ceil(n_panels / n_cols))
    fig, axes = plt.subplots(
        n_rows * 2,
        n_cols,
        figsize=(7.2, 3.15 * n_rows),
        gridspec_kw={"height_ratios": [3.0, 1.05] * n_rows},
        squeeze=False,
    )

    profile_cache = {}
    theory_cache = {}
    all_sample_counts = []
    for i, target_mass in enumerate(TARGET_MASSES):
        panel_row = i // n_cols
        col = i % n_cols
        ax = axes[2 * panel_row, col]
        ratio_ax = axes[2 * panel_row + 1, col]
        panel_profiles = {}
        theory_profiles = {}
        sample_counts = []
        panel_power_marks = []

        for label, _, snapshot_path, color in MODEL_SPECS:
            catalog = catalogs[label]
            profile, nhalo = compute_or_load_profile(label, snapshot_path, catalog, target_mass)
            sample_counts.append(nhalo)
            if nhalo:
                all_sample_counts.append(nhalo)
            if profile[0] is None:
                continue
            profile_cache[(label, target_mass)] = profile
            panel_profiles[label] = profile
            if np.isfinite(profile[4]):
                panel_power_marks.append(profile[4])
            x, rho_med, rho_lo, rho_hi = profile[:4]
            ax.errorbar(
                x,
                rho_med,
                yerr=np.vstack((rho_med - rho_lo, rho_hi - rho_med)),
                color=color,
                linestyle="none",
                marker="o",
                markersize=2.6,
                markerfacecolor="white",
                markeredgewidth=0.8,
                elinewidth=0.45,
                capsize=1.1,
                capthick=0.45,
                alpha=0.9,
            )

        for (theory_label_base, ps_args), (_, _, _, color) in zip(THEORY_PS_SPECS, MODEL_SPECS):
            x_theory, rho_theory = calculate_theory_nfw_profile(target_mass, ps_args)
            if x_theory is None:
                continue
            theory_profiles[theory_label_base] = (x_theory, rho_theory)
            theory_cache[(theory_label_base, target_mass)] = (x_theory, rho_theory)
            ax.loglog(x_theory, rho_theory, color=color, linestyle="--", linewidth=1.0, alpha=0.95)

        pl_profile = panel_profiles.get("PL")
        if pl_profile is not None:
            for label, color in [("BTKP1", JOURNAL_COLORS["blue"]), ("BTKP10", JOURNAL_COLORS["green"])]:
                bt_profile = panel_profiles.get(label)
                if bt_profile is None:
                    continue
                x_ratio, ratio, yerr_low, yerr_high = calculate_ratio_profile(bt_profile[:4], pl_profile[:4])
                ratio_ax.errorbar(
                    x_ratio,
                    ratio,
                    yerr=np.vstack((yerr_low, yerr_high)),
                    color=color,
                    linestyle="none",
                    marker="o",
                    markersize=2.3,
                    markerfacecolor="white",
                    markeredgewidth=0.75,
                    elinewidth=0.42,
                    capsize=1.0,
                    capthick=0.42,
                    alpha=0.9,
                )

        theory_pl = theory_profiles.get("PL")
        if theory_pl is not None:
            x_pl, rho_pl = theory_pl
            for label, color in [("BTKP1", JOURNAL_COLORS["blue"]), ("BTKP10", JOURNAL_COLORS["green"])]:
                theory_bt = theory_profiles.get(label)
                if theory_bt is None:
                    continue
                x_bt, rho_bt = theory_bt
                rho_pl_on_bt = np.interp(x_bt, x_pl, rho_pl)
                valid = rho_pl_on_bt > 0.0
                ratio = np.full_like(rho_bt, np.nan, dtype=float)
                ratio[valid] = rho_bt[valid] / rho_pl_on_bt[valid]
                ratio_ax.plot(x_bt, ratio, color=color, linestyle="--", linewidth=0.9, alpha=0.95)

        ax.text(
            0.04,
            0.04,
            mass_label_text(target_mass, min(sample_counts) if sample_counts else 0),
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="left",
            fontsize=7.8,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.8),
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ratio_ax.set_xscale("log")
        ratio_ax.set_yscale("log")
        ratio_ax.set_ylim(0.45, 4.5)
        ratio_ax.yaxis.set_major_locator(FixedLocator([0.5, 1.0, 2.0, 4.0]))
        ratio_ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:g}"))
        ratio_ax.yaxis.set_minor_formatter(NullFormatter())
        ratio_ax.axhline(1.0, color="0.55", linewidth=0.7, alpha=0.85)
        power_x = np.nanmax(panel_power_marks) if panel_power_marks else np.nan
        if np.isfinite(power_x) and power_x > RADIAL_BINS[0]:
            power_x = min(power_x, RADIAL_BINS[-1])
            shade_kwargs = dict(color="0.50", alpha=0.18, linewidth=0.0, zorder=0)
            ax.axvspan(RADIAL_BINS[0], power_x, **shade_kwargs)
            ratio_ax.axvspan(RADIAL_BINS[0], power_x, **shade_kwargs)
            ax.axvline(power_x, color="0.45", linestyle=":", linewidth=0.9, alpha=0.9)
            ratio_ax.axvline(power_x, color="0.45", linestyle=":", linewidth=0.85, alpha=0.85)

        if panel_row == n_rows - 1:
            ratio_ax.set_xlabel(r"$r/R_{200m}$")
        else:
            ratio_ax.tick_params(labelbottom=False)
        ax.tick_params(labelbottom=False)
        if col == 0:
            ax.set_ylabel(r"$\rho_{\rm DM}(r)\,[M_\odot\,{\rm kpc}^{-3}]$")
            ratio_ax.set_ylabel("BT/PL")
        else:
            ax.tick_params(labelleft=False)
            ratio_ax.tick_params(labelleft=False)
        format_axes(ax, grid=True)
        format_axes(ratio_ax, grid=True)
        ax.tick_params(labelleft=(col == 0), labelright=False, labeltop=False)
        ratio_ax.tick_params(labelleft=(col == 0), labelright=False, labeltop=False)

    stack_handles = [
        Line2D([0], [0], color=JOURNAL_COLORS["black"], linestyle="none", marker="o", markerfacecolor="white", markeredgewidth=0.8, markersize=3.0),
        Line2D([0], [0], color=JOURNAL_COLORS["blue"], linestyle="none", marker="o", markerfacecolor="white", markeredgewidth=0.8, markersize=3.0),
        Line2D([0], [0], color=JOURNAL_COLORS["green"], linestyle="none", marker="o", markerfacecolor="white", markeredgewidth=0.8, markersize=3.0),
    ]
    theory_handles = [
        Line2D([0], [0], color=JOURNAL_COLORS["black"], linestyle="--", linewidth=1.0),
        Line2D([0], [0], color=JOURNAL_COLORS["blue"], linestyle="--", linewidth=1.0),
        Line2D([0], [0], color=JOURNAL_COLORS["green"], linestyle="--", linewidth=1.0),
        Patch(facecolor="0.50", alpha=0.28, edgecolor="none"),
    ]
    legend_kwargs = dict(
        loc="upper right",
        bbox_to_anchor=(0.985, 0.88),
        fontsize=6.1,
        frameon=True,
        framealpha=0.72,
        edgecolor="none",
        borderpad=0.16,
        labelspacing=0.08,
        handlelength=1.05,
        handletextpad=0.25,
    )
    axes[0, 0].legend(
        stack_handles,
        ["PL", "BTKP1", "BTKP10"],
        title=sample_label_text(all_sample_counts),
        title_fontsize=6.1,
        **legend_kwargs,
    )
    axes[0, min(1, n_cols - 1)].legend(
        theory_handles,
        [
            "PL",
            "BTKP1",
            "BTKP10",
            rf"{POWER_CRITERION_LABEL} $\kappa={POWER_KAPPA_THRESHOLD:g}$",
        ],
        title=f"{THEORY_CONCENTRATION_LABEL} NFW",
        title_fontsize=6.1,
        **legend_kwargs,
    )

    fig.subplots_adjust(top=0.965, bottom=0.075, left=0.10, right=0.99, hspace=0.08, wspace=0.06)
    out = PAPERPLOT_ROOT / "figures" / RADIAL_OUTPUT_BASENAME
    save_publication_figure(fig, out)
    print(f"Figure saved: {out}")


if __name__ == "__main__":
    plot_trial()
