"""Standalone Bocquet16 M200c halo mass function plot.

This script reads SOAP SO/200_crit halo masses and compares them with the
Bocquet et al. (2016) mass function using the corresponding PL/BT power
spectra. It writes only to the HALOMASS plot directory.
"""

import csv
import os
import shutil
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ANALYSIS_ROOT = SCRIPT_DIR.parent
ARTICLE_ROOT = next((p for p in SCRIPT_DIR.parents if (p / "main.tex").exists()), SCRIPT_DIR.parents[2])


def find_project_root(script_dir):
    for parent in script_dir.parents:
        if (parent / "data").exists() and (parent / "software" / "colossus").exists():
            return parent
    return script_dir.parents[2]


PROJECT_ROOT = find_project_root(SCRIPT_DIR)
WORKSPACE_ROOT = PROJECT_ROOT
COLOSSUS_ROOT = PROJECT_ROOT / "software" / "colossus"


def colossus_has_project_models():
    try:
        from colossus.cosmology import power_spectrum as colossus_power_spectrum
    except Exception:
        return False
    required = {"eisenstein98_pl", "eisenstein98_bt", "eisenstein98_bt_soft"}
    return required.issubset(colossus_power_spectrum.models)


if not colossus_has_project_models() and COLOSSUS_ROOT.exists() and str(COLOSSUS_ROOT) not in sys.path:
    sys.path.insert(0, str(COLOSSUS_ROOT))

import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.legend_handler import HandlerTuple
from matplotlib.ticker import FixedLocator, FuncFormatter, LogFormatterMathtext, LogLocator, NullFormatter
from colossus import settings
from colossus.cosmology import cosmology
from colossus.lss import mass_function


STYLE_CANDIDATES = list(SCRIPT_DIR.parents) + [
    PROJECT_ROOT / "papers" / "article_nonlinear_evolution_pps" / "public_data" / "scripts"
]
STYLE_ROOT = next(
    (p for p in STYLE_CANDIDATES if (p / "cosmology_plot_style.py").exists()),
    WORKSPACE_ROOT,
)
if str(STYLE_ROOT) not in sys.path:
    sys.path.insert(0, str(STYLE_ROOT))

from cosmology_plot_style import (  # noqa: E402
    JOURNAL_COLORS,
    apply_journal_style,
    format_axes,
    format_redshift,
    panel_label,
    save_publication_figure,
)


settings.BASE_DIR = os.environ.get(
    "COLOSSUS_CACHE_DIR", str(SCRIPT_DIR / "colossus_cache_bocquet16_m200c")
)

DATA_ROOT = PROJECT_ROOT / "data"
PUBLIC_POINTS_PATH = ARTICLE_ROOT / "public_data" / "figure_data" / "m200c_hmf" / "m200c_bocquet16_hmf_points.csv"
OUTPUT_PATH = ARTICLE_ROOT / "mass-function-m200c-bocquet16.png"
PAPERPLOT_OUTPUT_PATH = OUTPUT_PATH
CACHE_DIR = SCRIPT_DIR / "output" / "m200c_bocquet16_lowhigh_cache"

H = 0.6736
MASS_UNIT_MSUN = 1.0e10
MAIN_PARTICLE_MASS_MSUN = 1.89e6
NPART_MIN = 100
M200C_COMPLETE_MIN_MSUN = 2.0e8
SNAPSHOTS = ["0056", "0040", "0032", "0030", "0027", "0024"]
PANEL_COLUMNS = 3
MASS_BINS_MSUN = 10 ** np.arange(8.0, 13.85, 0.15)
THEORY_MASS_MSUN = 10 ** np.linspace(8.0, 13.8, 400)
HMF_X_MAJOR_TICKS = 10.0 ** np.arange(8, 12)
HMF_RATIO_TICK_POOL = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0])
BT_PL_LABEL_TICKS = np.array([0.1, 1.0, 10.0, 1000.0])
SIM_B16_LABEL_TICKS = np.array([0.5, 1.0, 2.0])
PUBLIC_MODEL_MAP = {"PL": "PL", "BT_soft": "BT_soft", "BT_deep": "BT_deep", "BTKP1": "BT_soft", "BTKP10": "BT_deep"}

MODELS = {
    "PL": {
        "label": "PL",
        "template": DATA_ROOT
        / "PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_pl",
        "color": JOURNAL_COLORS["black"],
        "marker": "o",
        "linestyle": "-",
    },
    "BT_soft": {
        "label": r"BT $k_p=1$",
        "template": DATA_ROOT
        / "bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_bt",
        "color": JOURNAL_COLORS["blue"],
        "marker": "^",
        "linestyle": "--",
    },
    "BT_deep": {
        "label": r"BT $k_p=10$",
        "template": DATA_ROOT
        / "bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_bt_soft",
        "color": JOURNAL_COLORS["green"],
        "marker": "s",
        "linestyle": "-.",
    },
}


def setup_cosmology():
    cosmology.setCosmology(
        "bocquet16_m200c_hmf",
        {
            "flat": True,
            "H0": 100.0 * H,
            "Om0": 0.3153,
            "Ob0": 0.0493,
            "sigma8": 0.8111,
            "ns": 0.9649,
            "relspecies": False,
        },
    )


def set_hmf_x_ticks(ax):
    ax.xaxis.set_major_locator(FixedLocator(HMF_X_MAJOR_TICKS))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.xaxis.set_minor_formatter(NullFormatter())


def set_hmf_log_ticks(ax, *, y_decades):
    set_hmf_x_ticks(ax)
    y_ticks = 10.0 ** np.arange(y_decades[0], y_decades[1] + 1)
    if y_ticks.size > 5:
        keep = np.linspace(0, y_ticks.size - 1, 5).round().astype(int)
        y_ticks = y_ticks[np.unique(keep)]
    ax.yaxis.set_major_locator(FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.yaxis.set_minor_formatter(NullFormatter())


def ratio_tick_label(value, _pos):
    if value <= 0 or not np.isfinite(value):
        return ""
    exponent = np.log10(value)
    rounded = int(np.rint(exponent))
    if np.isclose(exponent, rounded, atol=1.0e-10):
        return rf"$10^{{{rounded}}}$"
    return f"{value:g}"


def set_hmf_ratio_ticks(ax, *, ratio_ticks=None):
    set_hmf_x_ticks(ax)
    ymin, ymax = ax.get_ylim()
    if ratio_ticks is None:
        ratio_ticks = HMF_RATIO_TICK_POOL
    y_ticks = ratio_ticks[(ratio_ticks >= ymin) & (ratio_ticks <= ymax)]
    if len(y_ticks) >= 2:
        ax.yaxis.set_major_locator(FixedLocator(y_ticks))
        ax.yaxis.set_major_formatter(FuncFormatter(ratio_tick_label))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5), numticks=20))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="y", which="major", labelsize=8.0, pad=1.0)
    for tick_label in ax.get_yticklabels():
        tick_label.set_verticalalignment("center")


def apply_completeness_cut(centers, hmf, err):
    complete = centers >= M200C_COMPLETE_MIN_MSUN
    return centers[complete], hmf[complete], err[complete]


def mark_m200c_resolution(ax, annotate=False):
    """Mark the low-mass region below the plotted M200c completeness cut."""
    ax.axvspan(1.0e8, M200C_COMPLETE_MIN_MSUN, color="0.82", alpha=0.22, lw=0, zorder=0)
    ax.axvline(M200C_COMPLETE_MIN_MSUN, color="0.35", linestyle="--", linewidth=0.85, alpha=0.9, zorder=1)
    if annotate:
        ax.text(
            0.045,
            0.80,
            r"$N_{\rm DM}\lesssim100$",
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=7.0,
            color="0.35",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 0.8},
        )


def load_m200c_hmf_catalog(path, chunk_size=500_000, progress_label=None):
    with h5py.File(path, "r") as f:
        group = f["SO"]["200_crit"]
        mass_ds = group["TotalMass"]
        npart_ds = group["NumberOfDarkMatterParticles"]
        redshift = float(np.asarray(f["Header"].attrs["Redshift"]).flat[0])
        box_size_mpc = float(np.asarray(f["Header"].attrs["BoxSize"]).flat[0])

        counts = np.zeros(len(MASS_BINS_MSUN) - 1, dtype=np.float64)
        n_kept = 0
        n_total = len(mass_ds)
        for start in range(0, n_total, chunk_size):
            if progress_label and start and start % 1_000_000 == 0:
                print(f"{progress_label}: processed {start}/{n_total} M200c rows", flush=True)
            stop = min(start + chunk_size, n_total)
            mass_msun = np.asarray(mass_ds[start:stop], dtype=np.float64) * MASS_UNIT_MSUN
            npart = np.asarray(npart_ds[start:stop], dtype=np.int64)
            valid = np.isfinite(mass_msun) & (mass_msun > 0.0) & (npart >= NPART_MIN)
            n_kept += int(np.count_nonzero(valid))
            if np.any(valid):
                counts += np.histogram(mass_msun[valid], bins=MASS_BINS_MSUN)[0]

    redshift = 0.0 if abs(redshift) < 1.0e-8 else redshift
    dlnm = np.diff(np.log(MASS_BINS_MSUN))
    volume = box_size_mpc**3
    dndlnm = counts / (volume * dlnm)
    err = np.sqrt(counts) / (volume * dlnm)
    centers = np.sqrt(MASS_BINS_MSUN[:-1] * MASS_BINS_MSUN[1:])
    valid_bins = counts > 0
    centers, dndlnm, err = apply_completeness_cut(
        centers[valid_bins], dndlnm[valid_bins], err[valid_bins]
    )
    return centers, dndlnm, err, redshift, box_size_mpc, n_kept, n_total


def binned_hmf_dndlnm(mass_msun, box_size_mpc):
    counts, edges = np.histogram(mass_msun, bins=MASS_BINS_MSUN)
    dlnm = np.diff(np.log(edges))
    volume = box_size_mpc**3
    dndlnm = counts / (volume * dlnm)
    err = np.sqrt(counts) / (volume * dlnm)
    centers = np.sqrt(edges[:-1] * edges[1:])
    valid = counts > 0
    return centers[valid], dndlnm[valid], err[valid]


def bocquet16_theory(redshift, ps_model):
    mass_msun_h = THEORY_MASS_MSUN * H
    hmf_h3 = mass_function.massFunction(
        mass_msun_h,
        redshift,
        mdef="200c",
        model="bocquet16",
        q_out="dndlnM",
        ps_args={"model": ps_model},
        hydro=False,
    )
    return THEORY_MASS_MSUN, hmf_h3 * H**3


def interpolate_ratio(sim_mass, sim_hmf, sim_err, theory_mass, theory_hmf):
    finite = np.isfinite(theory_hmf) & (theory_hmf > 0.0)
    theory_at_sim = 10 ** np.interp(
        np.log10(sim_mass),
        np.log10(theory_mass[finite]),
        np.log10(theory_hmf[finite]),
        left=np.nan,
        right=np.nan,
    )
    valid = np.isfinite(theory_at_sim) & (theory_at_sim > 0.0)
    return sim_mass[valid], sim_hmf[valid] / theory_at_sim[valid], sim_err[valid] / theory_at_sim[valid]


def bt_to_pl_ratio(bt_data, pl_data):
    pl_lookup = {
        round(float(np.log10(mass)), 10): (hmf, err)
        for mass, hmf, err in zip(pl_data["mass"], pl_data["hmf"], pl_data["err"])
        if np.isfinite(mass) and np.isfinite(hmf) and np.isfinite(err) and hmf > 0.0
    }
    masses = []
    ratios = []
    errors = []
    for mass, hmf, err in zip(bt_data["mass"], bt_data["hmf"], bt_data["err"]):
        key = round(float(np.log10(mass)), 10)
        if key not in pl_lookup or not (np.isfinite(hmf) and np.isfinite(err) and hmf > 0.0):
            continue
        pl_hmf, pl_err = pl_lookup[key]
        ratio = hmf / pl_hmf
        ratio_err = ratio * np.sqrt((err / hmf) ** 2 + (pl_err / pl_hmf) ** 2)
        masses.append(mass)
        ratios.append(ratio)
        errors.append(ratio_err)
    return np.asarray(masses), np.asarray(ratios), np.asarray(errors)


def collect_results():
    sim_results = {name: {} for name in MODELS}
    theory_results = {name: {} for name in MODELS}

    for snap in SNAPSHOTS:
        for name, model in MODELS.items():
            path = Path(str(model["template"]).format(snap=snap))
            if not path.exists():
                print(f"Missing file: {path}")
                continue

            cache_file = CACHE_DIR / f"{name}_snap{snap}_m200c_bocquet16_input.npz"
            if cache_file.exists():
                cached = np.load(cache_file)
                centers = cached["centers"]
                hmf = cached["hmf"]
                err = cached["err"]
                centers, hmf, err = apply_completeness_cut(centers, hmf, err)
                redshift = float(cached["redshift"])
                n_kept = int(cached["n_kept"])
                n_total = int(cached["n_total"])
                print(f"{snap} {model['label']}: loaded cached M200c HMF", flush=True)
            else:
                centers, hmf, err, redshift, box_size, n_kept, n_total = load_m200c_hmf_catalog(
                    path, progress_label=f"{snap} {model['label']}"
                )
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(
                    cache_file,
                    centers=centers,
                    hmf=hmf,
                    err=err,
                    redshift=redshift,
                    n_kept=n_kept,
                    n_total=n_total,
                )
            theory_mass, theory_hmf = bocquet16_theory(redshift, model["ps_model"])
            ratio_mass, ratio, ratio_err = interpolate_ratio(centers, hmf, err, theory_mass, theory_hmf)

            sim_results[name][snap] = {
                "mass": centers,
                "hmf": hmf,
                "err": err,
                "ratio_mass": ratio_mass,
                "ratio": ratio,
                "ratio_err": ratio_err,
                "redshift": redshift,
                "n_kept": n_kept,
                "n_total": n_total,
            }
            theory_results[name][snap] = {
                "mass": theory_mass,
                "hmf": theory_hmf,
                "redshift": redshift,
            }
            print(f"{snap} {model['label']}: kept {n_kept}/{n_total} M200c halos")

    return sim_results, theory_results


def collect_results_from_public():
    grouped = {name: {snap: [] for snap in SNAPSHOTS} for name in MODELS}
    with PUBLIC_POINTS_PATH.open(newline="") as handle:
        for row in csv.DictReader(handle):
            name = PUBLIC_MODEL_MAP.get(row.get("model", ""))
            snap = str(int(float(row.get("snapshot", "nan")))).zfill(4)
            if name not in MODELS or snap not in SNAPSHOTS:
                continue
            grouped[name][snap].append(row)

    sim_results = {name: {} for name in MODELS}
    theory_results = {name: {} for name in MODELS}
    for snap in SNAPSHOTS:
        for name, model in MODELS.items():
            rows = grouped[name].get(snap, [])
            if not rows:
                continue
            rows = sorted(rows, key=lambda item: float(item["M_200c_Msun"]))
            centers = np.asarray([float(row["M_200c_Msun"]) for row in rows], dtype=float)
            hmf = np.asarray([float(row["dn_dlog10M"]) for row in rows], dtype=float)
            err = np.asarray([float(row["poisson_err"]) for row in rows], dtype=float)
            complete = centers >= M200C_COMPLETE_MIN_MSUN
            centers = centers[complete]
            hmf = hmf[complete]
            err = err[complete]
            if centers.size == 0:
                continue
            redshift = float(rows[0]["redshift"])
            n_kept = int(float(rows[0].get("n_kept", 0) or 0))
            n_total = int(float(rows[0].get("n_total", 0) or 0))
            theory_mass, theory_hmf = bocquet16_theory(redshift, model["ps_model"])
            ratio_mass, ratio, ratio_err = interpolate_ratio(centers, hmf, err, theory_mass, theory_hmf)
            sim_results[name][snap] = {
                "mass": centers,
                "hmf": hmf,
                "err": err,
                "ratio_mass": ratio_mass,
                "ratio": ratio,
                "ratio_err": ratio_err,
                "redshift": redshift,
                "n_kept": n_kept,
                "n_total": n_total,
            }
            theory_results[name][snap] = {
                "mass": theory_mass,
                "hmf": theory_hmf,
                "redshift": redshift,
            }
    return sim_results, theory_results


def padded_ratio_ylim(values, fallback=(0.5, 2.0)):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values) & (values > 0.0)]
    if values.size == 0:
        return fallback
    ymin = max(0.3, values.min() * 0.82)
    ymax = min(1.0e3, max(2.0, values.max() * 1.18))
    if ymax / ymin > 30.0:
        ymin = 10.0 ** np.floor(np.log10(ymin))
        ymax = 10.0 ** np.ceil(np.log10(ymax))
    return ymin, ymax


def ratio_ylim(values, fallback=(0.5, 10.0)):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values) & (values > 0.0)]
    if values.size == 0:
        return fallback
    ymin = max(0.08, values.min() * 0.82)
    ymax = max(2.0, values.max() * 1.18)
    if ymax / ymin > 30.0:
        ymin = 10.0 ** np.floor(np.log10(ymin))
        ymax = 1.35 * 10.0 ** np.ceil(np.log10(ymax))
    return ymin, ymax


def plot_results(sim_results, theory_results):
    apply_journal_style(base_fontsize=12.8)

    n_panels = len(SNAPSHOTS)
    n_cols = min(PANEL_COLUMNS, n_panels)
    n_rows = int(np.ceil(n_panels / n_cols))
    bt_pl_ratio_results = {name: {} for name in ("BT_soft", "BT_deep")}
    bt_pl_ratio_values = []
    sim_b16_values_by_row = {row: [] for row in range(n_rows)}

    for idx, snap in enumerate(SNAPSHOTS):
        row = idx // n_cols
        pl_data = sim_results.get("PL", {}).get(snap)
        if pl_data is None:
            continue
        for name in ("BT_soft", "BT_deep"):
            bt_data = sim_results.get(name, {}).get(snap)
            if bt_data is None:
                continue
            ratio_mass, ratio, ratio_err = bt_to_pl_ratio(bt_data, pl_data)
            bt_pl_ratio_results[name][snap] = {
                "mass": ratio_mass,
                "ratio": ratio,
                "ratio_err": ratio_err,
            }
            bt_pl_ratio_values.extend(ratio[np.isfinite(ratio) & (ratio > 0.0)])
        for name in MODELS:
            data = sim_results.get(name, {}).get(snap)
            if data is not None:
                sim_b16_values_by_row[row].extend(data["ratio"][np.isfinite(data["ratio"]) & (data["ratio"] > 0.0)])

    bt_pl_ratio_ylim = ratio_ylim(bt_pl_ratio_values)
    sim_b16_ratio_ylims = {}
    for row in range(n_rows):
        sim_b16_ratio_ylims[row] = padded_ratio_ylim(sim_b16_values_by_row.get(row, []), fallback=(0.5, 2.0))

    fig = plt.figure(figsize=(3.20 * n_cols, 4.35 * n_rows))
    outer = gridspec.GridSpec(
        n_rows,
        n_cols,
        figure=fig,
        left=0.095,
        right=0.995,
        bottom=0.085,
        top=0.985,
        wspace=0.10,
        hspace=0.12,
    )

    for idx, snap in enumerate(SNAPSHOTS):
        inner = gridspec.GridSpecFromSubplotSpec(
            3, 1, subplot_spec=outer[idx], height_ratios=[4.0, 1.15, 1.25], hspace=0.08
        )
        ax_upper = fig.add_subplot(inner[0])
        ax_bt = fig.add_subplot(inner[1], sharex=ax_upper)
        ax_model = fig.add_subplot(inner[2], sharex=ax_upper)
        row = idx // n_cols
        col = idx % n_cols

        redshift = None
        for name, model in MODELS.items():
            if snap in theory_results[name]:
                theory = theory_results[name][snap]
                redshift = theory["redshift"]
                ax_upper.plot(
                    theory["mass"],
                    theory["hmf"],
                    color=model["color"],
                    linestyle=model["linestyle"],
                    linewidth=1.25,
                    alpha=0.95,
                )
            if snap in sim_results[name]:
                sim = sim_results[name][snap]
                ax_upper.errorbar(
                    sim["mass"],
                    sim["hmf"],
                    yerr=sim["err"],
                    fmt=model["marker"],
                    color=model["color"],
                    markersize=3.5,
                    capsize=1.5,
                    alpha=0.9,
                    markerfacecolor="white",
                    markeredgewidth=0.7,
                    elinewidth=0.65,
                )
                ax_model.errorbar(
                    sim["ratio_mass"],
                    sim["ratio"],
                    yerr=sim["ratio_err"],
                    fmt=model["marker"],
                    color=model["color"],
                    markersize=3.2,
                    capsize=1.3,
                    alpha=0.9,
                    markerfacecolor="white",
                    markeredgewidth=0.7,
                    elinewidth=0.6,
                )

        for name in ("BT_soft", "BT_deep"):
            if snap in bt_pl_ratio_results[name]:
                ratio_data = bt_pl_ratio_results[name][snap]
                model = MODELS[name]
                ax_bt.errorbar(
                    ratio_data["mass"],
                    ratio_data["ratio"],
                    yerr=ratio_data["ratio_err"],
                    fmt=model["marker"],
                    color=model["color"],
                    markersize=3.3,
                    capsize=1.4,
                    alpha=0.9,
                    markerfacecolor="white",
                    markeredgewidth=0.7,
                    elinewidth=0.6,
                )

        format_axes(ax_upper, grid=True)
        format_axes(ax_bt, grid=True)
        format_axes(ax_model, grid=True)
        y_min = 1.0e-8 if redshift is not None and redshift >= 8.0 else 1.0e-7
        ax_upper.set(xscale="log", yscale="log", xlim=(1.0e8, 2.0e11), ylim=(y_min, 1.0e2))
        ax_bt.set(xscale="log", yscale="log", xlim=(1.0e8, 2.0e11), ylim=bt_pl_ratio_ylim)
        ax_model.set(xscale="log", yscale="log", xlim=(1.0e8, 2.0e11), ylim=sim_b16_ratio_ylims[row])
        set_hmf_log_ticks(ax_upper, y_decades=(int(np.log10(y_min)), 2))
        set_hmf_ratio_ticks(ax_bt, ratio_ticks=BT_PL_LABEL_TICKS)
        set_hmf_ratio_ticks(ax_model, ratio_ticks=SIM_B16_LABEL_TICKS)
        mark_m200c_resolution(ax_upper, annotate=False)
        mark_m200c_resolution(ax_bt, annotate=(idx == 0))
        mark_m200c_resolution(ax_model, annotate=False)
        for ratio_ax in (ax_bt, ax_model):
            ratio_ax.axhline(1.0, color="black", linewidth=0.7, alpha=0.65)
            ratio_ax.axhline(2.0, color="0.5", linewidth=0.55, linestyle=":", alpha=0.7)
            ratio_ax.axhline(5.0, color="0.5", linewidth=0.55, linestyle=":", alpha=0.7)

        if redshift is not None:
            panel_label(
                ax_upper,
                rf"$z={format_redshift(redshift, 2)}$",
                loc=(0.95, 0.92),
                ha="right",
                fontsize=12.4,
            )

        if row == n_rows - 1:
            ax_model.set_xlabel(r"$M_{200c}\,[M_\odot]$")
        else:
            ax_model.tick_params(labelbottom=False)
        ax_upper.tick_params(labelbottom=False)
        ax_bt.tick_params(labelbottom=False)

        if col == 0:
            ax_upper.set_ylabel(r"$dn/d\ln M_{200c}\,[{\rm Mpc}^{-3}]$")
            ax_bt.set_ylabel(r"$f_{\rm BT}/f_{\rm PL}$")
            ax_model.set_ylabel(r"$\mathrm{Sim}/\mathrm{B16}$")
        else:
            ax_upper.tick_params(labelleft=False)
            ax_bt.tick_params(labelleft=False)
            ax_model.tick_params(labelleft=False)

    handles = []
    labels = []
    for model in MODELS.values():
        line = plt.Line2D(
            [0], [0], color=model["color"], linestyle=model["linestyle"], linewidth=1.25
        )
        marker = plt.Line2D(
            [0],
            [0],
            color=model["color"],
            marker=model["marker"],
            markersize=3.7,
            markerfacecolor="white",
            markeredgewidth=0.7,
            linestyle="",
        )
        handles.append((line, marker))
        labels.append(model["label"])

    fig.axes[0].legend(
        handles,
        labels,
        title=r"B16 $M_{200c}$; BT: $m_s=1.5$",
        handler_map={tuple: HandlerTuple(ndivide=None)},
        loc="lower left",
        fontsize=10.3,
        title_fontsize=10.0,
        frameon=True,
        framealpha=0.75,
        edgecolor="none",
        borderpad=0.25,
        labelspacing=0.25,
        handletextpad=0.35,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAPERPLOT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_path = Path(os.environ.get("M200C_HMF_OUTPUT_PATH", OUTPUT_PATH))
    paperplot_output_path = Path(
        os.environ.get("M200C_HMF_PAPERPLOT_OUTPUT_PATH", PAPERPLOT_OUTPUT_PATH)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    paperplot_output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving: {output_path}", flush=True)
    fig.savefig(output_path, dpi=320, bbox_inches="tight", pad_inches=0.08)
    if output_path.resolve() != paperplot_output_path.resolve():
        print(f"Copying: {paperplot_output_path}", flush=True)
        shutil.copy2(output_path, paperplot_output_path)
    plt.close(fig)
    print(f"Saved: {output_path}")
    print(f"Saved: {paperplot_output_path}")


def main():
    setup_cosmology()
    if PUBLIC_POINTS_PATH.exists() and os.environ.get("M200C_HMF_USE_CATALOG", "0") != "1":
        sim_results, theory_results = collect_results_from_public()
    else:
        sim_results, theory_results = collect_results()
    plot_results(sim_results, theory_results)


if __name__ == "__main__":
    main()
