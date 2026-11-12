"""Plot the manuscript halo–matter bias comparison from the reduced tables."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter
import numpy as np
from colossus.cosmology import cosmology
from colossus.lss import bias, peaks

from cosmology_plot_style import MODEL_COLORS, apply_journal_style, format_axes, format_redshift, panel_label

ARTICLE = Path(__file__).resolve().parents[2]
DATA = ARTICLE / "public_data" / "figure_data"
MODELS = {"PL": "PL", "BT1": "BT_soft", "BT10": "BT_deep"}
SNAPS = (56, 48, 44, 40, 35, 30)
H = 0.6736
SIGMA8 = 0.8111
DELTA_C = 1.686
SAMPLES = (("FOF", 256, "o"), ("FOF", 25, "^"), ("M200m", 25, "D"))


def variance(radius, k, power):
    x = np.multiply.outer(np.atleast_1d(radius), k)
    window = 3 * (np.sin(x) - x * np.cos(x)) / x**3
    small = x < 0.01
    window[small] = 1 - x[small]**2 / 10 + x[small]**4 / 280
    integrate = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return integrate(k**3 * power * window**2 / (2 * np.pi**2), np.log(k), axis=-1)


def main(output):
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

    apply_journal_style()
    fig, axes = plt.subplots(2, 3, figsize=(7.8, 4.9), sharex=True)
    fig.subplots_adjust(left=0.083, right=0.986, bottom=0.12, top=0.83, wspace=0.28, hspace=0.20)
    xmin, xmax = 1.4e8, 1.3 * points["mass_median"].max()
    for ax, snap in zip(axes.flat, SNAPS):
        panel = points[points["snap"] == snap]
        z = max(0.0, panel["redshift"][0])
        if not np.allclose(panel["redshift"], z, atol=1e-5):
            raise ValueError(f"Inconsistent redshift for snapshot {snap}")
        grid = np.geomspace(xmin, min(xmax, 2 * panel["mass_median"].max()), 230)
        for model, color in MODEL_COLORS.items():
            k, p = linear_power[model]
            nu = DELTA_C / (np.sqrt(variance(peaks.lagrangianR(grid), k, p)) * sim.growthFactor(z))
            anu2 = 0.707 * nu**2
            st = 1 + (anu2 - 1) / DELTA_C + 0.6 / (DELTA_C * (1 + anu2**0.3))
            ax.plot(grid / H, bias.modelTinker10(nu, z, "200m"), color=color, lw=1.15)
            ax.plot(grid / H, st, color=color, ls="--", lw=1.05)
            for kind, box, marker in SAMPLES:
                rows = panel[(panel["model"] == model) & (panel["box_hMpc"] == box) &
                             (panel["mass_definition"] == kind)]
                ax.errorbar(rows["mass_median"] / H, rows["bias"], yerr=rows["bias_err"],
                            fmt=marker, color=color, mfc=color if box == 256 else "white",
                            ms=2.9, mew=0.65, elinewidth=0.6, capsize=1, zorder=3)
        ax.set(xscale="log", yscale="log", xlim=(xmin / H, xmax / H))
        ax.yaxis.set_major_locator(FixedLocator((0.5, 0.6, 0.8, 1, 1.5, 2, 3, 4, 6, 8, 10)))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%g"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        format_axes(ax)
        panel_label(ax, rf"$z={format_redshift(z)}$", loc=(0.05, 0.94), fontsize=9)
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$b_{\rm hm}$")
    for ax in axes[-1, :]:
        ax.set_xlabel(r"$M_{\rm h}\ [M_\odot]$")
    models = [Line2D([], [], color=MODEL_COLORS[m], label=label)
              for m, label in zip(MODELS, ("PL", r"BT $k_p=1$", r"BT $k_p=10$"))]
    samples = [Line2D([], [], color="0.25", ls="none", marker=marker,
                      mfc="0.25" if box == 256 else "white", label=label)
               for (_, box, marker), label in zip(SAMPLES, ("FOF 256", "FOF 25", r"SOAP $M_{200m}$ 25"))]
    curves = [Line2D([], [], color="0.25", ls=ls, label=label)
              for ls, label in (("-", "Tinker10"), ("--", "ST99"))]
    fig.legend(handles=models, loc="upper center", ncol=3, bbox_to_anchor=(0.52, 0.985))
    fig.legend(handles=samples + curves, loc="upper center", ncol=5, bbox_to_anchor=(0.52, 0.925))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches=None)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTICLE / "halo-bias.pdf")
    main(parser.parse_args().output)
