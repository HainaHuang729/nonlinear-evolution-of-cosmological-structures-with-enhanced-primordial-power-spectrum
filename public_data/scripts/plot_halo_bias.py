"""Plot the manuscript halo–matter bias comparison from the reduced tables."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FormatStrFormatter, MaxNLocator, NullLocator
import numpy as np
from colossus.cosmology import cosmology
from colossus.lss import bias, peaks

from cosmology_plot_style import MODEL_COLORS, apply_journal_style, format_axes, format_redshift, panel_label

ARTICLE = Path(__file__).resolve().parents[2]
DATA = ARTICLE / "public_data" / "figure_data"
MODELS = {"PL": "PL", "BT1": "BT_soft", "BT10": "BT_deep"}
SNAPS = (56, 48, 40, 32)
H = 0.6736
SIGMA8 = 0.8111
DELTA_C = 1.686
SAMPLES = (
    ("FOF", 256, "o", "FOF 256"),
    ("FOF", 25, "^", "FOF 25"),
    ("M200m", 256, "o", r"SOAP $M_{200m}$ 256"),
    ("M200m", 25, "^", r"SOAP $M_{200m}$ 25"),
)


def variance(radius, k, power):
    x = np.multiply.outer(np.atleast_1d(radius), k)
    window = 3 * (np.sin(x) - x * np.cos(x)) / x**3
    small = x < 0.01
    window[small] = 1 - x[small]**2 / 10 + x[small]**4 / 280
    integrate = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return integrate(k**3 * power * window**2 / (2 * np.pi**2), np.log(k), axis=-1)


def theory_bias(mass_msun_h, z, spectrum, growth):
    k, power = spectrum
    sigma = np.sqrt(variance(peaks.lagrangianR(mass_msun_h), k, power)) * growth
    nu = DELTA_C / sigma
    anu2 = 0.707 * nu**2
    st = 1 + (anu2 - 1) / DELTA_C + 0.6 / (DELTA_C * (1 + anu2**0.3))
    return bias.modelTinker10(nu, z, "200m"), st


def paired_bias_ratio(bt, pl):
    edges = ["mass_lo", "mass_hi"]
    # Independent CSV reductions can differ in the last digits of the same edge.
    bt_edges = np.rec.fromarrays([np.round(np.log10(bt[edge]), 10) for edge in edges])
    pl_edges = np.rec.fromarrays([np.round(np.log10(pl[edge]), 10) for edge in edges])
    _, bt_index, pl_index = np.intersect1d(bt_edges, pl_edges, return_indices=True)
    mass = np.sqrt(bt["mass_lo"][bt_index] * bt["mass_hi"][bt_index]) / H
    return mass, bt["bias"][bt_index] / pl["bias"][pl_index]


def main(output, *, split=False):
    sim = cosmology.setCosmology("paper_halo_bias", dict(
        flat=True, H0=100 * H, Om0=0.3153, Ob0=0.0493, ns=0.9649,
        sigma8=SIGMA8, relspecies=False,
    ))
    read = dict(delimiter=",", names=True, dtype=None, encoding="utf-8")
    points = np.genfromtxt(DATA / "halo_bias" / "halo_bias_measurements.csv", **read)
    spectra = np.genfromtxt(DATA / "input_power_spectra" / "input_power_spectra.csv", **read)
    linear_power = {}
    for model, spectrum in MODELS.items():
        rows = np.sort(spectra[spectra["model"] == spectrum], order="k_hMpc")
        k, p = rows["k_hMpc"], rows["P_k_Mpc_over_h_cubed"]
        # The common Fourier-convention factor cancels when normalizing each shape.
        linear_power[model] = (k, p * SIGMA8**2 / variance(8, k, p)[0])

    apply_journal_style(base_fontsize=10.6)
    if split:
        pairs = [draw_figure(points, linear_power, sim, kind) for kind in ("M200m", "FOF")]
        for groups in zip(*(axes for _, axes in pairs), strict=True):
            limits = [axes[0].get_ylim() for axes in groups]
            lo = min(limit[0] for limit in limits)
            hi = max(limit[1] for limit in limits)
            for axes in groups:
                axes[0].set_ylim(lo, hi)
        for (fig, _), suffix in zip(pairs, ("soap-tinker10", "fof-st99"), strict=True):
            save_figure(fig, output.with_stem(f"{output.stem}-{suffix}"))
    else:
        fig, _ = draw_figure(points, linear_power, sim)
        save_figure(fig, output)


def draw_figure(points, linear_power, sim, sample_kind=None):
    samples_to_plot = [sample for sample in SAMPLES if sample_kind in (None, sample[0])]
    model_labels = {"PL": "PL", "BT1": r"BT $k_p=1$", "BT10": r"BT $k_p=10$"}
    model_rows = points if sample_kind is None else points[points["mass_definition"] == sample_kind]
    active_models = [model for model in MODELS if model in model_rows["model"]]
    predictions = ((0, "-", "Tinker10"), (1, "--", "ST99"))
    if sample_kind == "M200m":
        predictions = predictions[:1]
    elif sample_kind == "FOF":
        predictions = predictions[1:]

    fig = plt.figure(figsize=(7.4, 6.5))
    layout = fig.add_gridspec(7, 2, left=.105, right=.985, bottom=.112, top=.976,
                              height_ratios=[3.15, 1.1, 1, .28, 3.15, 1.1, 1],
                              wspace=.085, hspace=.13)
    xmin = points["mass_lo"].min() / 1.12
    xmax = points["mass_hi"].max() * 1.12
    first_decade = int(np.ceil(np.log10(xmin / H)))
    last_decade = int(np.floor(np.log10(xmax / H)))
    mass_ticks = 10.0 ** np.arange(first_decade, last_decade + 1, 2)
    shared_x = None
    main_axes, ratio_axes, residual_axes = [], [], []
    for i, snap in enumerate(SNAPS):
        panel = points[points["snap"] == snap]
        z = max(0.0, panel["redshift"][0])
        if not np.allclose(panel["redshift"], z, atol=1e-5):
            raise ValueError(f"Inconsistent redshift for snapshot {snap}")
        row, col = divmod(i, 2)
        start = 4 * row
        ax = fig.add_subplot(layout[start, col], sharex=shared_x,
                             sharey=main_axes[0] if main_axes else None)
        if not main_axes:
            ax.set_yscale("log")
        shared_x = ax
        ratio_ax = fig.add_subplot(layout[start + 1, col], sharex=ax,
                                   sharey=ratio_axes[0] if ratio_axes else None)
        residual_ax = fig.add_subplot(layout[start + 2, col], sharex=ax,
                                      sharey=residual_axes[0] if residual_axes else None)
        main_axes.append(ax)
        ratio_axes.append(ratio_ax)
        residual_axes.append(residual_ax)
        # Draw theory over the mass range covered by the selected catalog at this epoch.
        extent = panel if sample_kind is None else panel[panel["mass_definition"] == sample_kind]
        if not len(extent):
            extent = panel
        grid = np.geomspace(extent["mass_lo"].min() / 1.12,
                            extent["mass_hi"].max() * 1.12, 230)
        growth = sim.growthFactor(z)
        curves = {model: theory_bias(grid, z, spectrum, growth) for model, spectrum in linear_power.items()}
        for model in active_models:
            color = MODEL_COLORS[model]
            for index, ls, _ in predictions:
                pred = curves[model][index]
                ax.plot(grid / H, pred, color=color, ls=ls, lw=1.1)
                if model != "PL":
                    ratio_ax.plot(grid / H, pred / curves["PL"][index], color=color, ls=ls, lw=1)
            for kind, box, marker, _ in samples_to_plot:
                sample = panel[(panel["box_hMpc"] == box) & (panel["mass_definition"] == kind)]
                rows = sample[sample["model"] == model]
                if not len(rows):
                    continue
                mass = rows["mass_median"] / H
                face = color if sample_kind is None and kind == "FOF" else "white"
                size = 3.1 if sample_kind is None and kind == "FOF" else 4.6
                marker_layer = 4 if kind == "FOF" else 3
                ax.errorbar(mass, rows["bias"], yerr=rows["bias_err"], fmt=marker, color=color,
                            mfc=face, ms=size, mew=.65, elinewidth=.6, capsize=1, zorder=marker_layer)
                if sample_kind is not None or kind == "FOF":
                    index = 0 if kind == "M200m" else 1
                    reference = theory_bias(rows["mass_median"], z, linear_power[model], growth)[index]
                    residual_ax.errorbar(mass, rows["bias"] / reference - 1, yerr=rows["bias_err"] / reference,
                                         fmt=marker, color=color, mfc=face,
                                         ms=2.9 if sample_kind is None else 3.8, mew=.65,
                                         elinewidth=.55, capsize=.8, zorder=3)
                if model != "PL":
                    x, ratio = paired_bias_ratio(rows, sample[sample["model"] == "PL"])
                    ratio_ax.plot(x, ratio, marker, ls="none", color=color, mfc=face,
                                  ms=size, mew=.65, zorder=marker_layer)
        ax.set(xscale="log", xlim=(xmin / H, xmax / H))
        ax.xaxis.set_major_locator(FixedLocator(mass_ticks))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_major_locator(FixedLocator((0.5, 1, 2, 4, 8)))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%g"))
        ax.yaxis.set_minor_locator(NullLocator())
        for panel_ax in (ax, ratio_ax, residual_ax):
            format_axes(panel_ax, grid=True)
            panel_ax.set_axisbelow(True)
            panel_ax.tick_params(which="major", length=3.8, labelbottom=False,
                                 labelleft=(col == 0))
        panel_label(ax, rf"$z={format_redshift(z)}$", loc=(.11, .92), fontsize=11.4)
        ratio_ax.axhline(1, color=".52", lw=.7, zorder=0)
        residual_ax.axhline(0, color=".52", lw=.7, zorder=0)
        if col == 0:
            ax.set_ylabel(r"$b_{\rm hm}$")
            ratio_ax.set_ylabel("BT/PL")
            residual_ax.set_ylabel(r"$\Delta b/b_{\rm th}$")
            for panel_ax in (ax, ratio_ax, residual_ax):
                panel_ax.yaxis.set_label_coords(-.16, .5)
        residual_ax.tick_params(labelbottom=(row == 1), labelsize=10.2)

    for axes in (main_axes, ratio_axes, residual_axes):
        lo, hi = axes[0].get_ylim()
        if axes is ratio_axes:
            hi = max(hi, 1.07)
        if axes is main_axes:
            lo = max(lo, .43)
            hi = max(hi, 16)
        axes[0].set_ylim(lo, hi)
        if axes is not main_axes:
            axes[0].yaxis.set_major_locator(MaxNLocator(nbins=3))
    mass_label = {None: r"M_{\rm h}", "FOF": r"M_{\rm FOF}", "M200m": r"M_{200m}"}[sample_kind]
    fig.supxlabel(rf"${mass_label}\ [M_\odot]$", x=.545, y=.032, fontsize=12.6)
    models = [Line2D([], [], color=MODEL_COLORS[m], label=model_labels[m]) for m in active_models]
    samples = [Line2D([], [], color="0.25", ls="none", marker=marker,
                      mfc="0.25" if sample_kind is None and kind == "FOF" else "white", label=label)
               for kind, _, marker, label in samples_to_plot]
    curves = [Line2D([], [], color="0.25", ls=ls, label=label)
              for _, ls, label in predictions]
    for ax, handles in zip((main_axes[2], main_axes[3], main_axes[1]),
                           (models, samples, curves), strict=True):
        ax.legend(handles=handles, loc="lower right", fontsize=9.5,
                  handlelength=1.8, handletextpad=.45, borderaxespad=.65,
                  labelspacing=.26, frameon=True, framealpha=1,
                  facecolor="white", edgecolor="none")
    return fig, (main_axes, ratio_axes, residual_axes)


def save_figure(fig, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches=None)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTICLE / "halo-bias.pdf")
    parser.add_argument("--split", action="store_true", help="Draw separate SOAP and FOF comparisons.")
    args = parser.parse_args()
    main(args.output, split=args.split)
