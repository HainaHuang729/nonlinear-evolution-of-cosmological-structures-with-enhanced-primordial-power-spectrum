import os
import sys
import csv
import gc
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerTuple
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
ARTICLE_ROOT = next(
    (p for p in Path(__file__).resolve().parents if (p / "main.tex").exists()),
    WORKSPACE_ROOT / "papers" / "article_nonlinear_evolution_pps",
)
PUBLIC_DATA_ROOT = ARTICLE_ROOT / "public_data"
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
    (
        p
        for p in [
            *Path(__file__).resolve().parents,
            WORKSPACE_ROOT / "papers" / "article_nonlinear_evolution_pps" / "public_data" / "scripts",
        ]
        if (p / "cosmology_plot_style.py").exists()
    ),
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
OUTER_PANEL_HSPACE = 0.07
LEFT_LABEL_X = -0.095
THEORY_MODELS = {
    "diemer19": {
        "label": "D19",
        "math_label": r"\mathrm{D19}",
        "title_label": "Diemer & Joyce (2019)",
        "full_label": "Diemer & Joyce (2019)",
        "colossus_model": "diemer19",
        "colossus_kwargs": {},
        "slug": "d19",
        "linestyle": ":",
        "linewidth": 2.15,
        "alpha": 0.95,
    },
    "ishiyama21_fit": {
        "label": "I21 fit",
        "math_label": r"\mathrm{I21}_{\rm fit}",
        "title_label": "Ishiyama et al. (2021) fit",
        "full_label": "Ishiyama et al. (2021), NFW-fit concentrations",
        "colossus_model": "ishiyama21",
        "colossus_kwargs": {"c_type": "fit", "halo_sample": "all"},
        "slug": "i21-fit",
        "linestyle": "-.",
        "linewidth": 1.95,
        "alpha": 0.85,
    },
    "ludlow16": {
        "label": "L16",
        "math_label": r"\mathrm{L16}",
        "title_label": "Ludlow et al. (2016)",
        "full_label": "Ludlow et al. (2016)",
        "colossus_model": "ludlow16",
        "colossus_kwargs": {},
        "slug": "l16",
        "linestyle": "--",
        "linewidth": 1.95,
        "alpha": 0.88,
    },
}
CONCENTRATION_OUTPUT_PATHS = {
    "diemer19": ARTICLE_ROOT / "concentration-qc-d19.png",
    "ishiyama21_fit": ARTICLE_ROOT / "concentration-qc-i21-fit.png",
    "ludlow16": ARTICLE_ROOT / "concentration-qc-l16.png",
}
CONCENTRATION_RESIDUAL_CSV_PATH = Path(os.environ.get(
    "CONCENTRATION_RESIDUAL_CSV_PATH",
    PUBLIC_DATA_ROOT / "figure_data" / "concentration" / "concentration_qc_theory_ratios.csv",
))
CONCENTRATION_SCATTER_CSV_PATH = Path(os.environ.get(
    "CONCENTRATION_SCATTER_CSV_PATH",
    PUBLIC_DATA_ROOT / "figure_data" / "concentration" / "concentration_qc_scatter.csv",
))
CONCENTRATION_BINNED_CSV_PATH = Path(os.environ.get(
    "CONCENTRATION_BINNED_CSV_PATH",
    PUBLIC_DATA_ROOT / "figure_data" / "concentration" / "concentration_qc_binned_points.csv",
))
USE_PUBLIC_BINNED_POINTS = os.environ.get("CONCENTRATION_READ_RAW", "0") != "1"

MODELS = {
    "PL": {
        "label": "PL",
        "figure_label": "PL",
        "template": BASE_PATH
        / "PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_pl",
        "color": JOURNAL_COLORS["black"],
        "marker": "o",
    },
    "BT_kp1": {
        "label": "BTKP1",
        "figure_label": r"BT $k_p=1$",
        "template": BASE_PATH
        / "bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_bt",
        "color": JOURNAL_COLORS["blue"],
        "marker": "^",
    },
    "BT_kp10": {
        "label": "BTKP10",
        "figure_label": r"BT $k_p=10$",
        "template": BASE_PATH
        / "bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_{snap}.hdf5",
        "ps_model": "eisenstein98_bt_soft",
        "color": JOURNAL_COLORS["green"],
        "marker": "s",
    },
}
PUBLIC_MODEL_ALIASES = {
    "PL": "PL",
    "BT_soft": "BT_kp1",
    "BT_deep": "BT_kp10",
    "BT_kp1": "BT_kp1",
    "BT_kp10": "BT_kp10",
    "BTKP1": "BT_kp1",
    "BTKP10": "BT_kp10",
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
    bin_counts, _, _ = stats.binned_statistic(
        log_mass, log_conc, statistic="count", bins=bin_edges
    )
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    valid = (
        ~np.isnan(bin_medians)
        & ~np.isnan(bin_16th)
        & ~np.isnan(bin_84th)
        & np.isfinite(bin_counts)
        & (bin_counts > 0)
    )
    return (
        bin_centers[valid],
        bin_medians[valid],
        bin_16th[valid],
        bin_84th[valid],
        bin_counts[valid].astype(int),
    )


def mark_particle_thresholds(ax, annotate=False):
    """Show the low-particle structural caution region without line labels."""
    x_strict = np.log10(MASS_NPART_STRICT_MSUN)
    ax.axvspan(8.0, x_strict, color="0.78", alpha=0.16, lw=0, zorder=0)


def collect_simulation_stats(snap, model_key, model):
    path = Path(str(model["template"]).format(snap=snap))
    log_mass, conc, n_valid, n_total = load_data(path)
    bins, logc_binned, logc_p16, logc_p84, n_halos = bin_stats(log_mass, conc)
    yerr_low = logc_binned - logc_p16
    yerr_high = logc_p84 - logc_binned
    print(f"{snap} {model['label']}: kept {n_valid}/{n_total} halos")
    return {
        "model_key": model_key,
        "model": model,
        "snapshot": snap,
        "redshift": REDSHIFT_BY_SNAPSHOT[snap],
        "source_file": str(path),
        "bins": bins,
        "logc_median": logc_binned,
        "logc_p16": logc_p16,
        "logc_p84": logc_p84,
        "yerr_low": yerr_low,
        "yerr_high": yerr_high,
        "sigma_68_log10_c": 0.5 * (logc_p84 - logc_p16),
        "n_halos": n_halos,
        "n_valid_snapshot": n_valid,
        "n_total_snapshot": n_total,
    }


def collect_public_binned_stats():
    df = pd.read_csv(CONCENTRATION_BINNED_CSV_PATH)
    stats_by_snap = {snap: {} for snap in SNAPSHOTS}
    for (model_name, snap), group in df.groupby(["model", "snapshot"], sort=False):
        model_key = PUBLIC_MODEL_ALIASES.get(str(model_name))
        snap = str(snap).zfill(4)
        if model_key not in MODELS or snap not in stats_by_snap:
            continue
        group = group.sort_values("log10_M200c_center_Msun")
        logc_median = group["log10_c200c_median"].to_numpy(dtype=float)
        logc_p16 = group["log10_c200c_p16"].to_numpy(dtype=float)
        logc_p84 = group["log10_c200c_p84"].to_numpy(dtype=float)
        n_halos = group["n_halos_bin"].to_numpy(dtype=int)
        n_valid = int(group["n_valid_snapshot"].iloc[0]) if "n_valid_snapshot" in group else int(n_halos.sum())
        n_total = int(group["n_total_snapshot"].iloc[0]) if "n_total_snapshot" in group else n_valid
        stats_by_snap[snap][model_key] = {
            "model_key": model_key,
            "model": MODELS[model_key],
            "snapshot": snap,
            "redshift": float(group["redshift"].iloc[0]),
            "source_file": str(group["source_file"].iloc[0]) if "source_file" in group else str(CONCENTRATION_BINNED_CSV_PATH),
            "bins": group["log10_M200c_center_Msun"].to_numpy(dtype=float),
            "logc_median": logc_median,
            "logc_p16": logc_p16,
            "logc_p84": logc_p84,
            "yerr_low": logc_median - logc_p16,
            "yerr_high": logc_p84 - logc_median,
            "sigma_68_log10_c": 0.5 * (logc_p84 - logc_p16),
            "n_halos": n_halos,
            "n_valid_snapshot": n_valid,
            "n_total_snapshot": n_total,
        }
        print(f"{snap} {MODELS[model_key]['label']}: loaded {len(group)} public binned points")
    return stats_by_snap


def plot_simulation(ax, stat):
    model = stat["model"]
    ax.errorbar(
        stat["bins"],
        stat["logc_median"],
        yerr=[stat["yerr_low"], stat["yerr_high"]],
        fmt=model["marker"],
        color=model["color"],
        markersize=4.8,
        alpha=0.95,
        capsize=2.8,
        capthick=1.35,
        elinewidth=1.35,
        markerfacecolor="white",
        markeredgewidth=1.15,
        label="_nolegend_",
    )


def evaluate_theory(redshift, model, theory_model, mass_msun):
    mass_msun_h = mass_msun * 0.6736
    ps_args = {"model": model["ps_model"]}
    theory_style = THEORY_MODELS[theory_model]
    theory_kwargs = dict(theory_style.get("colossus_kwargs", {}))

    conc_model, valid = concentration.concentration(
        mass_msun_h,
        "200c",
        redshift,
        model=theory_style.get("colossus_model", theory_model),
        ps_args=ps_args,
        **theory_kwargs,
        range_return=True,
    )
    valid = np.asarray(valid, dtype=bool) & np.isfinite(conc_model) & (conc_model > 0)
    return conc_model, valid


def plot_theory(ax, redshift, model, theory_model, mass_msun):
    conc_model, valid = evaluate_theory(redshift, model, theory_model, mass_msun)
    theory_style = THEORY_MODELS[theory_model]
    ax.plot(
        np.log10(mass_msun[valid]),
        np.log10(conc_model[valid]),
        theory_style["linestyle"],
        color=model["color"],
        linewidth=theory_style["linewidth"],
        alpha=theory_style["alpha"],
        label="_nolegend_",
    )


def add_theory_ratios(stat, theory_models=None):
    if theory_models is None:
        theory_models = THEORY_MODELS
    model = stat["model"]
    mass_msun = 10 ** stat["bins"]
    sim_c = 10 ** stat["logc_median"]
    sim_c_low = 10 ** stat["logc_p16"]
    sim_c_high = 10 ** stat["logc_p84"]
    stat.setdefault("theory_ratios", {})
    for theory_model in theory_models:
        conc_model, valid = evaluate_theory(
            stat["redshift"], model, theory_model, mass_msun
        )
        valid = np.asarray(valid, dtype=bool)
        ratio = np.full_like(sim_c, np.nan, dtype=float)
        ratio_low = np.full_like(sim_c, np.nan, dtype=float)
        ratio_high = np.full_like(sim_c, np.nan, dtype=float)
        good = valid & np.isfinite(conc_model) & (conc_model > 0)
        ratio[good] = sim_c[good] / conc_model[good]
        ratio_low[good] = ratio[good] - sim_c_low[good] / conc_model[good]
        ratio_high[good] = sim_c_high[good] / conc_model[good] - ratio[good]
        stat["theory_ratios"][theory_model] = {
            "concentration": conc_model,
            "valid": good,
            "ratio": ratio,
            "ratio_low": ratio_low,
            "ratio_high": ratio_high,
        }


def write_residual_table(stats_by_snap, output_path):
    reference_labels = {
        "diemer19": "DiemerJoyce19",
        "ishiyama21_fit": "Ishiyama21Fit",
        "ludlow16": "Ludlow16",
    }
    rows = []
    for snap in SNAPSHOTS:
        for stat in stats_by_snap[snap].values():
            for theory_model, ratio_data in stat["theory_ratios"].items():
                good = ratio_data["valid"] & np.isfinite(ratio_data["ratio"])
                indices = np.where(good)[0]
                for i in indices:
                    rows.append({
                        "model": stat["model"]["label"],
                        "snapshot": stat["snapshot"],
                        "redshift": f"{stat['redshift']:.10e}",
                        "theory_model": theory_model,
                        "reference_model": reference_labels[theory_model],
                        "log10_M200c_center_Msun": f"{stat['bins'][i]:.10e}",
                        "log10_c200c_median": f"{stat['logc_median'][i]:.10e}",
                        "theory_c200c": f"{ratio_data['concentration'][i]:.10e}",
                        "sim_over_theory": f"{ratio_data['ratio'][i]:.10e}",
                        "sim_over_theory_minus_1": f"{ratio_data['ratio'][i] - 1.0:.10e}",
                        "ratio_low_16th": f"{ratio_data['ratio_low'][i]:.10e}",
                        "ratio_high_84th": f"{ratio_data['ratio_high'][i]:.10e}",
                        "n_halos_bin": int(stat["n_halos"][i]),
                        "source_file": stat["source_file"],
                    })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "model",
                "snapshot",
                "redshift",
                "theory_model",
                "reference_model",
                "log10_M200c_center_Msun",
                "log10_c200c_median",
                "theory_c200c",
                "sim_over_theory",
                "sim_over_theory_minus_1",
                "ratio_low_16th",
                "ratio_high_84th",
                "n_halos_bin",
                "source_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote concentration residual table: {output_path}")


def write_scatter_table(stats_by_snap, output_path):
    rows = []
    for snap in SNAPSHOTS:
        for stat in stats_by_snap[snap].values():
            for i in range(len(stat["bins"])):
                rows.append({
                    "model": stat["model"]["label"],
                    "snapshot": stat["snapshot"],
                    "redshift": f"{stat['redshift']:.10e}",
                    "log10_M200c_center_Msun": f"{stat['bins'][i]:.10e}",
                    "log10_c200c_p16": f"{stat['logc_p16'][i]:.10e}",
                    "log10_c200c_p84": f"{stat['logc_p84'][i]:.10e}",
                    "sigma_68_log10_c": f"{stat['sigma_68_log10_c'][i]:.10e}",
                    "n_halos_bin": int(stat["n_halos"][i]),
                    "source_file": stat["source_file"],
                })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "model",
                "snapshot",
                "redshift",
                "log10_M200c_center_Msun",
                "log10_c200c_p16",
                "log10_c200c_p84",
                "sigma_68_log10_c",
                "n_halos_bin",
                "source_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote concentration scatter table: {output_path}")


def emphasize_panel_text(ax):
    ax.tick_params(axis="both", which="major", labelsize=13.2, width=1.55, length=6.2)
    ax.tick_params(axis="both", which="minor", width=1.25, length=3.8)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontweight("bold")
    for spine in ax.spines.values():
        spine.set_linewidth(1.55)


def ratio_ylim_from_values(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return 0.0, 2.0
    span = max(0.45, np.nanmax(values) - np.nanmin(values))
    return max(0.0, np.nanmin(values) - 0.08 * span), max(1.6, np.nanmax(values) + 0.08 * span)


def output_path_for_theory(theory_model):
    slug = THEORY_MODELS[theory_model]["slug"].upper().replace("-", "_")
    env_key = f"CONCENTRATION_OUTPUT_PATH_{slug}"
    return Path(os.environ.get(env_key, CONCENTRATION_OUTPUT_PATHS[theory_model]))


def plot_theory_figure(theory_model, stats_by_snap, mass_msun):
    theory_style = THEORY_MODELS[theory_model]
    fig = plt.figure(figsize=(9.6, 10.8))
    outer_grid = fig.add_gridspec(
        2,
        2,
        left=0.09,
        right=0.985,
        bottom=0.075,
        top=0.985,
        wspace=0.10,
        hspace=OUTER_PANEL_HSPACE,
    )

    for i, snap in enumerate(SNAPSHOTS):
        redshift = REDSHIFT_BY_SNAPSHOT[snap]
        row = i // 2
        col = i % 2
        inner_grid = outer_grid[row, col].subgridspec(
            3, 1, height_ratios=[3.25, 1.15, 1.15], hspace=0.07
        )
        ax = fig.add_subplot(inner_grid[0])
        ax_residual = fig.add_subplot(inner_grid[1], sharex=ax)
        ax_scatter = fig.add_subplot(inner_grid[2], sharex=ax)

        ratio_values = []
        scatter_values = []

        for model_key, model in MODELS.items():
            stat = stats_by_snap[snap][model_key]
            plot_simulation(ax, stat)
            plot_theory(ax, redshift, model, theory_model, mass_msun)

            ratio_data = stat["theory_ratios"][theory_model]
            good = ratio_data["valid"] & np.isfinite(ratio_data["ratio"])
            if np.any(good):
                ax_residual.errorbar(
                    stat["bins"][good],
                    ratio_data["ratio"][good],
                    yerr=[
                        ratio_data["ratio_low"][good],
                        ratio_data["ratio_high"][good],
                    ],
                    fmt=model["marker"],
                    color=model["color"],
                    markersize=3.6,
                    alpha=0.92,
                    capsize=2.4,
                    capthick=1.05,
                    elinewidth=1.05,
                    markerfacecolor="white",
                    markeredgewidth=0.9,
                    label="_nolegend_",
                )
                ratio_values.extend(ratio_data["ratio"][good])
                ratio_values.extend(ratio_data["ratio"][good] - ratio_data["ratio_low"][good])
                ratio_values.extend(ratio_data["ratio"][good] + ratio_data["ratio_high"][good])
            ax_scatter.plot(
                stat["bins"],
                stat["sigma_68_log10_c"],
                model["marker"],
                color=model["color"],
                markersize=3.6,
                alpha=0.92,
                markerfacecolor="white",
                markeredgewidth=0.9,
            )
            scatter_values.extend(
                stat["sigma_68_log10_c"][np.isfinite(stat["sigma_68_log10_c"])]
            )

        ax.set_xlim(8.0, 13.5)
        ax.set_xticks([8, 9, 10, 11, 12, 13])
        y_max = 1.8 if redshift <= 1.1 else 1.3
        ax.set_ylim(0.0, y_max)
        format_axes(ax)
        format_axes(ax_residual)
        format_axes(ax_scatter)
        emphasize_panel_text(ax)
        emphasize_panel_text(ax_residual)
        emphasize_panel_text(ax_scatter)
        mark_particle_thresholds(ax, annotate=(i == 0))
        mark_particle_thresholds(ax_residual, annotate=False)
        mark_particle_thresholds(ax_scatter, annotate=False)

        ax_residual.axhline(1.0, color="0.25", linestyle="-", linewidth=0.85, alpha=0.75)
        ax_residual.set_ylim(*ratio_ylim_from_values(ratio_values))

        scatter_values = np.asarray(scatter_values, dtype=float)
        scatter_values = scatter_values[np.isfinite(scatter_values)]
        ax_scatter.set_ylim(0.0, max(0.35, 1.12 * np.nanmax(scatter_values)) if len(scatter_values) else 0.35)

        if row == 1:
            ax_scatter.set_xlabel(r"$\log_{10}(M_{200c}/M_{\odot})$", fontweight="bold", labelpad=5)
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax_residual.get_xticklabels(), visible=False)
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax_residual.get_xticklabels(), visible=False)
            plt.setp(ax_scatter.get_xticklabels(), visible=False)
        if col == 0:
            ax.set_ylabel(r"$\log_{10}(c_{200c})$", fontweight="bold", labelpad=5)
            ax_residual.set_ylabel(
                rf"$c_{{\rm sim}}/{theory_style['math_label']}$",
                fontweight="bold",
                labelpad=5,
            )
            ax_scatter.set_ylabel(r"$\sigma_{68}(\log_{10}c)$", fontweight="bold", labelpad=5)
            for label_axis in (ax, ax_residual, ax_scatter):
                label_axis.yaxis.set_label_coords(LEFT_LABEL_X, 0.5)
        else:
            ax.tick_params(axis="y", labelleft=False)
            ax_residual.tick_params(axis="y", labelleft=False)
            ax_scatter.tick_params(axis="y", labelleft=False)
        ax.text(
            0.95,
            0.92,
            rf"$z={format_redshift(redshift, 2)}$",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=15.2,
            fontweight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 2.0},
        )

        if i == 0:
            handles = []
            labels = []
            for legend_model in MODELS.values():
                line = plt.Line2D(
                    [0],
                    [0],
                    color=legend_model["color"],
                    linestyle=theory_style["linestyle"],
                    linewidth=theory_style["linewidth"],
                )
                marker = plt.Line2D(
                    [0],
                    [0],
                    color=legend_model["color"],
                    marker=legend_model["marker"],
                    markersize=4.8,
                    markerfacecolor="white",
                    markeredgewidth=1.0,
                    linestyle="",
                )
                handles.append((line, marker))
                labels.append(legend_model["figure_label"])
            ax.legend(
                handles,
                labels,
                title=rf"{theory_style['label']}; BT: $m_s=1.5$",
                handler_map={tuple: HandlerTuple(ndivide=None)},
                loc="lower left",
                ncol=1,
                fontsize=10.6,
                title_fontsize=10.6,
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
        left=0.09,
        right=0.985,
        bottom=0.075,
        top=0.985,
        wspace=0.10,
        hspace=OUTER_PANEL_HSPACE,
    )

    fig.savefig(output_path_for_theory(theory_model), dpi=100, bbox_inches=None)
    plt.close(fig)
    gc.collect()


def main():
    apply_journal_style(base_fontsize=14.2)
    mass_msun = 10 ** np.arange(8.0, 13.5, 0.1)
    theory_keys = [
        key.strip()
        for key in os.environ.get("CONCENTRATION_THEORY_KEYS", ",".join(THEORY_MODELS)).split(",")
        if key.strip()
    ]
    if USE_PUBLIC_BINNED_POINTS and CONCENTRATION_BINNED_CSV_PATH.exists():
        stats_by_snap = collect_public_binned_stats()
    else:
        stats_by_snap = {snap: {} for snap in SNAPSHOTS}
        for snap in SNAPSHOTS:
            for model_key, model in MODELS.items():
                stat = collect_simulation_stats(snap, model_key, model)
                stats_by_snap[snap][model_key] = stat

    for snap in SNAPSHOTS:
        for stat in stats_by_snap[snap].values():
            add_theory_ratios(stat)

    write_residual_table(stats_by_snap, CONCENTRATION_RESIDUAL_CSV_PATH)
    write_scatter_table(stats_by_snap, CONCENTRATION_SCATTER_CSV_PATH)
    for snap in SNAPSHOTS:
        for stat in stats_by_snap[snap].values():
            stat["theory_ratios"].clear()
    gc.collect()

    for theory_model in theory_keys:
        if theory_model not in THEORY_MODELS:
            raise ValueError(f"Unknown concentration theory model: {theory_model}")
        for snap in SNAPSHOTS:
            for stat in stats_by_snap[snap].values():
                add_theory_ratios(stat, [theory_model])
        plot_theory_figure(theory_model, stats_by_snap, mass_msun)
        for snap in SNAPSHOTS:
            for stat in stats_by_snap[snap].values():
                stat["theory_ratios"].clear()
        gc.collect()


if __name__ == "__main__":
    main()
