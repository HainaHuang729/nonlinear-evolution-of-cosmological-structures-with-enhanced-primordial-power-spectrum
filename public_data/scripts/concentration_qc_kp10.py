import os
import sys
from pathlib import Path

import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

LOCAL_COLOSSUS_ROOT = next(
    (
        p / "software" / "colossus"
        for p in Path(__file__).resolve().parents
        if (p / "software" / "colossus" / "colossus").exists()
    ),
    None,
)
if LOCAL_COLOSSUS_ROOT is not None and str(LOCAL_COLOSSUS_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCAL_COLOSSUS_ROOT))

from colossus import settings
from colossus.cosmology import cosmology
from colossus.halo import concentration

WORKSPACE_ROOT = next(
    (p for p in Path(__file__).resolve().parents if (p / "data" / "PL").exists()),
    Path.cwd(),
)
PAPERPLOT_ROOT = next(
    (
        p
        for p in (
            WORKSPACE_ROOT / "analysis" / "_used_by_article_nonlinear_evolution_pps" / "paperplot",
            WORKSPACE_ROOT / "analysis" / "paperplot",
        )
        if p.exists()
    ),
    WORKSPACE_ROOT / "analysis" / "paperplot",
)
STYLE_ROOT = next(
    (p for p in Path(__file__).resolve().parents if (p / "cosmology_plot_style.py").exists()),
    WORKSPACE_ROOT,
)
if str(STYLE_ROOT) not in sys.path:
    sys.path.insert(0, str(STYLE_ROOT))

settings.BASE_DIR = str(PAPERPLOT_ROOT / "cache")

from cosmology_plot_style import (  # noqa: E402
    JOURNAL_COLORS,
    apply_journal_style,
    format_axes,
    format_redshift,
    panel_label,
    save_publication_figure,
)


REDSHIFT_BY_SNAPSHOT = {
    "0032": 8.519850605,
    "0040": 3.441080566,
    "0048": 1.071796860,
    "0056": 0.000000000,
}

BASE_PATH = WORKSPACE_ROOT / "data"
SNAPSHOTS = ["0056", "0048", "0040", "0032"]
MASS_UNIT = 1e10
NPART_MIN = 100
MAIN_PARTICLE_MASS_MSUN = 1.89e6
NPART_STRICT = 1000
MASS_NPART_STRICT_MSUN = NPART_STRICT * MAIN_PARTICLE_MASS_MSUN
CONC_MAX = 500.0
SIMULATION_N_BINS = 22
THEORY_MODELS = {
    "diemer19": {"label": "D19", "linestyle": ":", "linewidth": 2.15, "alpha": 0.95},
    "ishiyama21": {"label": "I21", "linestyle": "-.", "linewidth": 1.95, "alpha": 0.85},
}

MODELS = {
    "PL": {
        "label": "PL",
        "template": BASE_PATH
        / "PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_pl",
        "color": JOURNAL_COLORS["black"],
        "marker": "o",
    },
    "BT_kp1": {
        "label": "BT(soft)",
        "template": BASE_PATH
        / "bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_bt",
        "color": JOURNAL_COLORS["blue"],
        "marker": "^",
    },
    "BT_kp10": {
        "label": "BT(deep)",
        "template": BASE_PATH
        / "bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_bt_soft",
        "color": JOURNAL_COLORS["green"],
        "marker": "s",
    },
}

cosmology.setCosmology(
    "concentration_qc",
    {
        "flat": True,
        "H0": 100 * 0.6736,
        "Om0": 0.3153,
        "Ob0": 0.0493,
        "sigma8": 0.8111,
        "ns": 0.9649,
        "relspecies": False,
    },
)


def load_data(file_path):
    """Load 200c mass and concentration with basic quality cuts."""
    with h5py.File(file_path, "r") as f:
        group = f["SO"]["200_crit"]
        conc = group["Concentration"][:]
        mass = group["TotalMass"][:] * MASS_UNIT
        npart = group["NumberOfDarkMatterParticles"][:]

    valid = (
        np.isfinite(mass)
        & np.isfinite(conc)
        & (mass > 0)
        & (conc > 0)
        & (conc < CONC_MAX)
        & (npart >= NPART_MIN)
    )
    return np.log10(mass[valid]), conc[valid], int(valid.sum()), int(len(valid))


def bin_stats(log_mass, conc, n_bins=SIMULATION_N_BINS):
    """Return median log10(c) and 16/84 percentiles in log-mass bins."""
    log_conc = np.log10(conc)
    bin_edges = np.linspace(8.0, 13.5, n_bins + 1)
    bin_medians, _, _ = stats.binned_statistic(
        log_mass, log_conc, statistic="median", bins=bin_edges
    )
    bin_16th, _, _ = stats.binned_statistic(
        log_mass,
        log_conc,
        statistic=lambda x: np.percentile(x, 16),
        bins=bin_edges,
    )
    bin_84th, _, _ = stats.binned_statistic(
        log_mass,
        log_conc,
        statistic=lambda x: np.percentile(x, 84),
        bins=bin_edges,
    )
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    yerr_low = bin_medians - bin_16th
    yerr_high = bin_84th - bin_medians
    valid = ~np.isnan(bin_medians) & ~np.isnan(yerr_low) & ~np.isnan(yerr_high)
    return bin_centers[valid], bin_medians[valid], yerr_low[valid], yerr_high[valid]


def mark_particle_thresholds(ax, annotate=False):
    """Show the low-particle structural caution region without line labels."""
    x_strict = np.log10(MASS_NPART_STRICT_MSUN)
    ax.axvspan(8.0, x_strict, color="0.78", alpha=0.16, lw=0, zorder=0)


def plot_simulation(ax, snap, model):
    path = Path(str(model["template"]).format(snap=snap))
    log_mass, conc, n_valid, n_total = load_data(path)
    bins, logc_binned, yerr_low, yerr_high = bin_stats(log_mass, conc)
    ax.errorbar(
        bins,
        logc_binned,
        yerr=[yerr_low, yerr_high],
        fmt=model["marker"],
        color=model["color"],
        markersize=4.8,
        alpha=0.95,
        capsize=2.8,
        capthick=1.35,
        elinewidth=1.35,
        markerfacecolor="white",
        markeredgewidth=1.15,
        label=f'{model["label"]} sim.',
    )
    print(f"{snap} {model['label']}: kept {n_valid}/{n_total} halos")


def plot_theory(ax, redshift, model, theory_model, mass_msun):
    mass_msun_h = mass_msun * 0.6736
    ps_args = {"model": model["ps_model"]}

    conc_model, valid = concentration.concentration(
        mass_msun_h,
        "200c",
        redshift,
        model=theory_model,
        ps_args=ps_args,
        range_return=True,
    )
    valid = np.asarray(valid, dtype=bool) & np.isfinite(conc_model) & (conc_model > 0)
    theory_style = THEORY_MODELS[theory_model]
    ax.plot(
        np.log10(mass_msun[valid]),
        np.log10(conc_model[valid]),
        theory_style["linestyle"],
        color=model["color"],
        linewidth=theory_style["linewidth"],
        alpha=theory_style["alpha"],
        label=f'{model["label"]} {theory_style["label"]}',
    )


def emphasize_panel_text(ax):
    ax.tick_params(axis="both", which="major", labelsize=12.2, width=1.55, length=6.2)
    ax.tick_params(axis="both", which="minor", width=1.25, length=3.8)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontweight("bold")
    for spine in ax.spines.values():
        spine.set_linewidth(1.55)


def main():
    apply_journal_style(base_fontsize=13.0)
    fig, axs = plt.subplots(2, 2, figsize=(9.6, 7.8), sharey=False)
    axs = axs.flatten()
    mass_msun = 10 ** np.arange(8.0, 13.5, 0.1)

    for i, snap in enumerate(SNAPSHOTS):
        redshift = REDSHIFT_BY_SNAPSHOT[snap]
        ax = axs[i]

        for model in MODELS.values():
            plot_simulation(ax, snap, model)

        for theory_model in THEORY_MODELS:
            for model in MODELS.values():
                plot_theory(ax, redshift, model, theory_model, mass_msun)

        ax.set_xlim(8.0, 13.5)
        ax.set_xticks([8, 9, 10, 11, 12, 13])
        y_max = 1.8 if redshift <= 1.1 else 1.3
        ax.set_ylim(0.0, y_max)
        format_axes(ax)
        emphasize_panel_text(ax)
        mark_particle_thresholds(ax, annotate=(i == 0))
        if i >= 2:
            ax.set_xlabel(r"$\log_{10}(M_{200c}/M_{\odot})$", fontweight="bold", labelpad=5)
        else:
            ax.set_xlabel("")
        if i % 2 == 0:
            ax.set_ylabel(r"$\log_{10}(c_{200c})$", fontweight="bold", labelpad=5)
        else:
            ax.tick_params(axis="y", labelleft=False)
        ax.text(
            0.95,
            0.92,
            rf"$z={format_redshift(redshift, 2)}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=14.0,
            fontweight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 2.0},
        )

        if i == 0:
            ax.legend(
                loc="lower left",
                ncol=3,
                fontsize=8.8,
                frameon=True,
                framealpha=0.72,
                edgecolor="none",
                borderpad=0.25,
                labelspacing=0.24,
                handletextpad=0.38,
                columnspacing=0.85,
                markerscale=1.15,
            )

    fig.subplots_adjust(
        left=0.09, right=0.985, bottom=0.09, top=0.985, wspace=0.10, hspace=0.15
    )

    output_dir = PAPERPLOT_ROOT / "figures"
    os.makedirs(output_dir, exist_ok=True)
    save_publication_figure(fig, output_dir / "concentration-qc.png")


if __name__ == "__main__":
    main()
