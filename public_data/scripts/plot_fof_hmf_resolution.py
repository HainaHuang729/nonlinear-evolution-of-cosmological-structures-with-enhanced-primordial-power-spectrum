"""FOF halo-mass-function resolution and volume check for the appendix.

The script streams the SWIFT FOF catalogues so that the fiducial
25 h^-1 Mpc, 1024^3 z=0 catalogue does not have to be loaded into memory.
It writes a reduced data table, a compact summary table, and the manuscript
appendix figure.
"""

from pathlib import Path
import csv
import os
import sys

import h5py
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists())
PROJECT_ROOT = next(parent for parent in SCRIPT_DIR.parents if (parent / "data" / "PL").exists())
DATA_ROOT = PROJECT_ROOT / "data" / "PL"
OUTPUT_ROOT = Path(os.environ.get("FOF_HMF_RESOLUTION_OUTPUT_ROOT", ARTICLE_ROOT))
OUTPUT_DATA_DIR = OUTPUT_ROOT / "public_data" / "figure_data" / "fof_hmf_resolution"
OUTPUT_FIGURE = OUTPUT_ROOT / "fof-hmf-resolution-volume.png"

JOURNAL_COLORS = {
    "blue": "#0072B2",
    "orange": "#D55E00",
    "green": "#009E73",
    "black": "#000000",
}


SNAPSHOTS = [56, 32]
LOGM_EDGES = np.arange(7.0, 14.5 + 1.0 / 6.0, 1.0 / 6.0)
RATIO_MIN_COUNT = 10
SUMMARY_MIN_COUNT = 20

RUNS = {
    "PL-25-1024": {
        "directory": DATA_ROOT / "PL_25_1024",
        "snapshot_stem": "PL_25_1024",
        "label": r"PL-25-$1024^3$",
        "color": JOURNAL_COLORS["black"],
        "marker": "o",
    },
    "PL-25-512": {
        "directory": DATA_ROOT / "PL_25_512",
        "snapshot_stem": "PL_25_512",
        "label": r"PL-25-$512^3$",
        "color": JOURNAL_COLORS["blue"],
        "marker": "s",
    },
    "PL-25-256": {
        "directory": DATA_ROOT / "PL_25_256",
        "snapshot_stem": "PL_25_256",
        "label": r"PL-25-$256^3$",
        "color": JOURNAL_COLORS["orange"],
        "marker": "^",
    },
    "PL-50-512": {
        "directory": DATA_ROOT / "PL_50_512",
        "snapshot_stem": "PL_50_512",
        "label": r"PL-50-$512^3$",
        "color": JOURNAL_COLORS["green"],
        "marker": "D",
    },
}


def warren_correct_mass(mass_msun, particle_mass_msun):
    """Apply the Warren et al. low-particle FOF correction."""
    particle_number = mass_msun / particle_mass_msun
    return mass_msun * (1.0 - np.power(particle_number, -0.6))


def snapshot_path(config, snap):
    return config["directory"] / f"{config['snapshot_stem']}_{snap:04d}.hdf5"


def fof_path(config, snap):
    return config["directory"] / f"fof_output_{snap:04d}.hdf5"


def read_snapshot_metadata(config, snap):
    with h5py.File(snapshot_path(config, snap), "r") as handle:
        header = handle["Header"].attrs
        redshift = float(np.asarray(header["Redshift"]).flat[0])
        box_size_mpc = float(np.asarray(header["BoxSize"]).flat[0])
        particle_mass_msun = float(np.asarray(header["InitialMassTable"])[1]) * 1.0e10
    return redshift, box_size_mpc, particle_mass_msun


def stream_hmf(config, snap, chunk_size=100_000):
    redshift, box_size_mpc, particle_mass_msun = read_snapshot_metadata(config, snap)
    counts = np.zeros(len(LOGM_EDGES) - 1, dtype=np.float64)
    mass_sums = np.zeros_like(counts)

    with h5py.File(fof_path(config, snap), "r") as handle:
        mass_dataset = handle["Groups/Masses"]
        for start in range(0, len(mass_dataset), chunk_size):
            raw_mass = np.asarray(mass_dataset[start:start + chunk_size], dtype=np.float64) * 1.0e10
            corrected_mass = warren_correct_mass(raw_mass, particle_mass_msun)
            valid = (
                np.isfinite(corrected_mass)
                & (corrected_mass >= 10.0 ** LOGM_EDGES[0])
                & (corrected_mass <= 10.0 ** LOGM_EDGES[-1])
            )
            if not np.any(valid):
                continue
            log_mass = np.log10(corrected_mass[valid])
            counts += np.histogram(log_mass, bins=LOGM_EDGES)[0]
            mass_sums += np.histogram(log_mass, bins=LOGM_EDGES, weights=corrected_mass[valid])[0]

    dlogm = np.diff(LOGM_EDGES)
    volume = box_size_mpc ** 3
    hmf = counts / (volume * dlogm)
    hmf_err = np.sqrt(counts) / (volume * dlogm)

    logm_centers = 0.5 * (LOGM_EDGES[:-1] + LOGM_EDGES[1:])
    nonzero = counts > 0
    logm_centers[nonzero] = np.log10(mass_sums[nonzero] / counts[nonzero])

    return {
        "redshift": redshift,
        "box_size_mpc": box_size_mpc,
        "particle_mass_msun": particle_mass_msun,
        "counts": counts,
        "hmf": hmf,
        "hmf_err": hmf_err,
        "logm_centers": logm_centers,
    }


def load_all_results():
    results = {}
    for snap in SNAPSHOTS:
        results[snap] = {}
        for run_name, config in RUNS.items():
            print(f"Reading {run_name} snapshot {snap:04d}", flush=True)
            results[snap][run_name] = stream_hmf(config, snap)
    return results


def write_points_csv(results):
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DATA_DIR / "fof_hmf_resolution_points.csv"
    fieldnames = [
        "model",
        "snapshot",
        "redshift",
        "box_size_mpc",
        "particle_mass_msun",
        "log10_M_FOF_Msun",
        "dn_dlog10M",
        "poisson_err",
        "counts",
        "log10_bin_left",
        "log10_bin_right",
        "source_fof_file",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for snap in SNAPSHOTS:
            for run_name, config in RUNS.items():
                data = results[snap][run_name]
                for index, logm in enumerate(data["logm_centers"]):
                    writer.writerow({
                        "model": run_name,
                        "snapshot": f"{snap:04d}",
                        "redshift": f"{data['redshift']:.10g}",
                        "box_size_mpc": f"{data['box_size_mpc']:.10g}",
                        "particle_mass_msun": f"{data['particle_mass_msun']:.10e}",
                        "log10_M_FOF_Msun": f"{logm:.10e}",
                        "dn_dlog10M": f"{data['hmf'][index]:.10e}",
                        "poisson_err": f"{data['hmf_err'][index]:.10e}",
                        "counts": f"{int(data['counts'][index])}",
                        "log10_bin_left": f"{LOGM_EDGES[index]:.10e}",
                        "log10_bin_right": f"{LOGM_EDGES[index + 1]:.10e}",
                        "source_fof_file": str(fof_path(config, snap)),
                    })
    return path


def ratio_to_fiducial(results, snap, run_name, min_count):
    reference = results[snap]["PL-25-1024"]
    data = results[snap][run_name]
    ratio = np.divide(
        data["hmf"],
        reference["hmf"],
        out=np.full_like(data["hmf"], np.nan),
        where=reference["hmf"] > 0.0,
    )
    ratio_err = ratio * np.sqrt(
        np.divide(data["hmf_err"], data["hmf"], out=np.zeros_like(data["hmf"]), where=data["hmf"] > 0.0) ** 2
        + np.divide(reference["hmf_err"], reference["hmf"], out=np.zeros_like(reference["hmf"]), where=reference["hmf"] > 0.0) ** 2
    )
    bin_mass = 10.0 ** (0.5 * (LOGM_EDGES[:-1] + LOGM_EDGES[1:]))
    valid = (
        np.isfinite(ratio)
        & (ratio > 0.0)
        & (data["counts"] >= min_count)
        & (reference["counts"] >= min_count)
    )
    return bin_mass, ratio, ratio_err, valid


def write_summary_csv(results):
    path = OUTPUT_DATA_DIR / "fof_hmf_resolution_summary.csv"
    fieldnames = [
        "model",
        "snapshot",
        "redshift",
        "particle_mass_msun",
        "mass_50_particle_msun",
        "n_ratio_bins",
        "log10_mass_min",
        "log10_mass_max",
        "median_ratio_to_PL_25_1024",
        "p16_ratio_to_PL_25_1024",
        "p84_ratio_to_PL_25_1024",
        "max_abs_fractional_deviation",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for snap in SNAPSHOTS:
            reference = results[snap]["PL-25-1024"]
            for run_name in ["PL-25-512", "PL-25-256", "PL-50-512"]:
                data = results[snap][run_name]
                bin_mass, ratio, _ratio_err, valid = ratio_to_fiducial(results, snap, run_name, SUMMARY_MIN_COUNT)
                min_mass = max(50.0 * data["particle_mass_msun"], 50.0 * reference["particle_mass_msun"])
                valid &= bin_mass >= min_mass
                if np.any(valid):
                    values = ratio[valid]
                    row = {
                        "n_ratio_bins": int(np.sum(valid)),
                        "log10_mass_min": f"{np.log10(np.min(bin_mass[valid])):.4f}",
                        "log10_mass_max": f"{np.log10(np.max(bin_mass[valid])):.4f}",
                        "median_ratio_to_PL_25_1024": f"{np.median(values):.4f}",
                        "p16_ratio_to_PL_25_1024": f"{np.percentile(values, 16):.4f}",
                        "p84_ratio_to_PL_25_1024": f"{np.percentile(values, 84):.4f}",
                        "max_abs_fractional_deviation": f"{np.max(np.abs(values - 1.0)):.4f}",
                    }
                else:
                    row = {
                        "n_ratio_bins": 0,
                        "log10_mass_min": "",
                        "log10_mass_max": "",
                        "median_ratio_to_PL_25_1024": "",
                        "p16_ratio_to_PL_25_1024": "",
                        "p84_ratio_to_PL_25_1024": "",
                        "max_abs_fractional_deviation": "",
                    }
                writer.writerow({
                    "model": run_name,
                    "snapshot": f"{snap:04d}",
                    "redshift": f"{data['redshift']:.10g}",
                    "particle_mass_msun": f"{data['particle_mass_msun']:.10e}",
                    "mass_50_particle_msun": f"{50.0 * data['particle_mass_msun']:.10e}",
                    **row,
                })
    return path


def set_log_ticks(ax):
    from matplotlib.ticker import FixedLocator, LogFormatterMathtext, LogLocator, NullFormatter

    ax.xaxis.set_major_locator(FixedLocator(10.0 ** np.arange(8, 15)))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.yaxis.set_minor_formatter(NullFormatter())


def mark_particle_thresholds(ax, results, snap):
    seen_thresholds = set()
    for run_name, config in RUNS.items():
        data = results[snap][run_name]
        threshold = 50.0 * data["particle_mass_msun"]
        key = round(np.log10(threshold), 3)
        if key in seen_thresholds:
            continue
        seen_thresholds.add(key)
        ax.axvline(
            threshold,
            color=config["color"],
            linestyle=":",
            linewidth=0.8,
            alpha=0.75,
            zorder=0,
        )


def make_figure(results):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, LogFormatterMathtext, LogLocator, NullFormatter

    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))

    from cosmology_plot_style import apply_journal_style, format_axes, format_redshift

    apply_journal_style(base_fontsize=8.4)
    fig, axes = plt.subplots(
        2,
        len(SNAPSHOTS),
        figsize=(7.1, 4.8),
        sharex="col",
        gridspec_kw={"height_ratios": [3.0, 1.35], "hspace": 0.06, "wspace": 0.18},
    )

    for column, snap in enumerate(SNAPSHOTS):
        ax_hmf = axes[0, column]
        ax_ratio = axes[1, column]
        redshift = results[snap]["PL-25-1024"]["redshift"]

        for run_name, config in RUNS.items():
            data = results[snap][run_name]
            mass = 10.0 ** data["logm_centers"]
            valid = data["counts"] > 0
            ax_hmf.errorbar(
                mass[valid],
                data["hmf"][valid],
                yerr=data["hmf_err"][valid],
                fmt=config["marker"],
                color=config["color"],
                markerfacecolor="white",
                markeredgewidth=0.8,
                markersize=3.0,
                capsize=1.0,
                elinewidth=0.55,
                linewidth=0.7,
                alpha=0.92,
                label=config["label"] if column == 0 else None,
            )

            if run_name == "PL-25-1024":
                continue
            bin_mass, ratio, ratio_err, ratio_valid = ratio_to_fiducial(results, snap, run_name, RATIO_MIN_COUNT)
            ax_ratio.errorbar(
                bin_mass[ratio_valid],
                ratio[ratio_valid],
                yerr=ratio_err[ratio_valid],
                fmt=config["marker"],
                color=config["color"],
                markerfacecolor="white",
                markeredgewidth=0.8,
                markersize=3.0,
                capsize=1.0,
                elinewidth=0.55,
                linewidth=0.7,
                alpha=0.92,
            )

        mark_particle_thresholds(ax_hmf, results, snap)
        mark_particle_thresholds(ax_ratio, results, snap)

        format_axes(ax_hmf, grid=True)
        format_axes(ax_ratio, grid=True)
        set_log_ticks(ax_hmf)
        set_log_ticks(ax_ratio)

        ax_hmf.set_xscale("log")
        ax_hmf.set_yscale("log")
        ax_ratio.set_xscale("log")
        ax_ratio.axhline(1.0, color="0.25", linewidth=0.8)
        ax_ratio.axhspan(0.9, 1.1, color="0.8", alpha=0.24, lw=0)
        ax_ratio.set_ylim(0.55, 1.35)
        ax_ratio.set_xlim(5.0e7, 3.0e14)

        ax_hmf.text(
            0.04,
            0.92,
            rf"$z={format_redshift(redshift, 2)}$",
            transform=ax_hmf.transAxes,
            ha="left",
            va="top",
            fontsize=9.2,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.4},
        )

        if column == 0:
            ax_hmf.set_ylabel(r"$dn/d\log_{10}M_{\rm FOF}\,[{\rm Mpc}^{-3}]$")
            ax_ratio.set_ylabel(r"ratio")
        else:
            ax_hmf.tick_params(labelleft=False)
            ax_ratio.tick_params(labelleft=False)

        ax_ratio.set_xlabel(r"$M_{\rm FOF}\,[M_\odot]$")
        ax_hmf.tick_params(labelbottom=False)

    axes[0, 0].legend(loc="lower left", fontsize=7.0, handlelength=1.2)
    fig.text(0.975, 0.35, r"Ratios are to PL-25-$1024^3$", rotation=90, va="center", ha="right", fontsize=8.0)
    fig.savefig(OUTPUT_FIGURE)
    plt.close(fig)
    return OUTPUT_FIGURE


def main():
    results = load_all_results()
    points_path = write_points_csv(results)
    summary_path = write_summary_csv(results)
    figure_path = make_figure(results)
    print(f"Wrote {points_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {figure_path}")


if __name__ == "__main__":
    main()
