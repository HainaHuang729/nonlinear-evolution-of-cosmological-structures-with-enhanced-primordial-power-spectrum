"""Standalone Bocquet16 M200c halo mass function plot.

This script reads SOAP SO/200_crit halo masses and compares them with the
Bocquet et al. (2016) mass function using the corresponding PL/BT power
spectra. It writes only to the HALOMASS plot directory.
"""

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ANALYSIS_ROOT = SCRIPT_DIR.parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
WORKSPACE_ROOT = PROJECT_ROOT
COLOSSUS_ROOT = PROJECT_ROOT / "software" / "colossus"
if COLOSSUS_ROOT.exists() and str(COLOSSUS_ROOT) not in sys.path:
    sys.path.insert(0, str(COLOSSUS_ROOT))

import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.legend_handler import HandlerTuple
from scipy.interpolate import interp1d

from colossus import settings
from colossus.cosmology import cosmology
from colossus.lss import mass_function


STYLE_ROOT = next(
    (p for p in SCRIPT_DIR.parents if (p / "cosmology_plot_style.py").exists()),
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


settings.BASE_DIR = str(SCRIPT_DIR / "colossus_cache_bocquet16_m200c")

DATA_ROOT = PROJECT_ROOT / "data"
OUTPUT_PATH = SCRIPT_DIR / "plot" / "mass_function_bocquet16_m200c_highz_3models.png"
PAPERPLOT_OUTPUT_PATH = ARTICLE_ANALYSIS_ROOT / "paperplot" / "figures" / "mass-function-m200c-bocquet16.png"
CACHE_DIR = SCRIPT_DIR / "output" / "m200c_bocquet16_lowhigh_cache"

H = 0.6736
MASS_UNIT_MSUN = 1.0e10
NPART_MIN = 100
M200C_COMPLETE_MIN_MSUN = 2.0e8
SNAPSHOTS = ["0056", "0040", "0032", "0030", "0027", "0024"]
PANEL_COLUMNS = 3
MASS_BINS_MSUN = 10 ** np.arange(8.0, 13.85, 0.15)
THEORY_MASS_MSUN = 10 ** np.linspace(8.0, 13.8, 400)

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


def apply_completeness_cut(centers, hmf, err):
    complete = centers >= M200C_COMPLETE_MIN_MSUN
    return centers[complete], hmf[complete], err[complete]


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
    interp = interp1d(
        np.log10(theory_mass[finite]),
        np.log10(theory_hmf[finite]),
        bounds_error=False,
        fill_value=np.nan,
    )
    theory_at_sim = 10 ** interp(np.log10(sim_mass))
    valid = np.isfinite(theory_at_sim) & (theory_at_sim > 0.0)
    return sim_mass[valid], sim_hmf[valid] / theory_at_sim[valid] - 1.0, sim_err[valid] / theory_at_sim[valid]


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


def plot_results(sim_results, theory_results):
    apply_journal_style(base_fontsize=12.8)

    n_panels = len(SNAPSHOTS)
    n_cols = min(PANEL_COLUMNS, n_panels)
    n_rows = int(np.ceil(n_panels / n_cols))

    fig = plt.figure(figsize=(3.20 * n_cols, 3.45 * n_rows))
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
            2, 1, subplot_spec=outer[idx], height_ratios=[4, 1], hspace=0.08
        )
        ax_upper = fig.add_subplot(inner[0])
        ax_lower = fig.add_subplot(inner[1], sharex=ax_upper)
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
                ax_lower.errorbar(
                    sim["ratio_mass"],
                    sim["ratio"],
                    yerr=sim["ratio_err"],
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
        format_axes(ax_lower, grid=True)
        y_min = 1.0e-8 if redshift is not None and redshift >= 8.0 else 1.0e-7
        ax_upper.set(xscale="log", yscale="log", xlim=(1.0e8, 2.0e11), ylim=(y_min, 1.0e2))
        ax_lower.set(xscale="log", xlim=(1.0e8, 2.0e11), ylim=(-1.05, 1.05))
        ax_lower.axhline(0.0, color="black", linewidth=0.7, alpha=0.65)
        ax_lower.axhline(0.1, color="0.5", linewidth=0.55, linestyle=":", alpha=0.7)
        ax_lower.axhline(-0.1, color="0.5", linewidth=0.55, linestyle=":", alpha=0.7)

        if redshift is not None:
            panel_label(
                ax_upper,
                rf"$z={format_redshift(redshift, 2)}$",
                loc=(0.95, 0.92),
                ha="right",
                fontsize=12.4,
            )

        if row == 1:
            ax_lower.set_xlabel(r"$M_{200c}\,[M_\odot]$")
        else:
            ax_lower.tick_params(labelbottom=False)
        ax_upper.tick_params(labelbottom=False)

        if col == 0:
            ax_upper.set_ylabel(r"$dn/d\ln M_{200c}\,[{\rm Mpc}^{-3}]$")
            ax_lower.set_ylabel(r"$\mathrm{sim}/\mathrm{B16}-1$")
        else:
            ax_upper.tick_params(labelleft=False)
            ax_lower.tick_params(labelleft=False)

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
    print(f"Saving: {OUTPUT_PATH}", flush=True)
    fig.savefig(OUTPUT_PATH, dpi=320, bbox_inches="tight", pad_inches=0.08)
    print(f"Saving: {PAPERPLOT_OUTPUT_PATH}", flush=True)
    fig.savefig(PAPERPLOT_OUTPUT_PATH, dpi=320, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"Saved: {OUTPUT_PATH}")
    print(f"Saved: {PAPERPLOT_OUTPUT_PATH}")


def main():
    setup_cosmology()
    sim_results, theory_results = collect_results()
    plot_results(sim_results, theory_results)


if __name__ == "__main__":
    main()
