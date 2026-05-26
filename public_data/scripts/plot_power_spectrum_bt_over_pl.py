#!/usr/bin/env python
"""Paperplot BT/PL nonlinear matter power-spectrum response."""

from pathlib import Path
import sys

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pyccl as ccl
import pyhmcode
from scipy.interpolate import interp1d


SCRIPT_PATH = Path(__file__).resolve()
ANALYSIS_ROOT = next(
    (p for p in SCRIPT_PATH.parents if (p / "paperplot").exists() and (p / "powerspectrum").exists()),
    next(
        (
            p / "analysis" / "_used_by_article_nonlinear_evolution_pps"
            for p in SCRIPT_PATH.parents
            if (
                p
                / "analysis"
                / "_used_by_article_nonlinear_evolution_pps"
                / "powerspectrum"
            ).exists()
        ),
        Path.cwd(),
    ),
)
WORKSPACE_ROOT = next(
    (p for p in SCRIPT_PATH.parents if (p / "data" / "PL").exists()),
    Path.cwd(),
)
STYLE_ROOT = next(
    (
        p
        for p in (
            SCRIPT_PATH.parent,
            *SCRIPT_PATH.parents,
            WORKSPACE_ROOT,
            WORKSPACE_ROOT.parent / "tools",
        )
        if (p / "cosmology_plot_style.py").exists()
    ),
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


SNAP_LIST = ["0056", "0048", "0040", "0032"]
N_PLOT_BINS = 42
DATA_DIR = ANALYSIS_ROOT / "powerspectrum" / "sim_power_data"
OUTPUT_PATH = ANALYSIS_ROOT / "paperplot" / "figures" / "power-spectrum.png"
BOX_LABEL = r"$25$ and $256\,h^{-1}\,\mathrm{Mpc}$ matched boxes"

OMEGA_C = 0.26458
OMEGA_B = 0.0493
H_VAL = 0.6736
N_S = 0.9649
SIGMA8 = 0.8111
OMEGA_M = OMEGA_C + OMEGA_B
MESH_N = 1024
K_NY_25 = np.pi * MESH_N / 25.0
K_NY_256 = np.pi * MESH_N / 256.0

K_THEORY = np.logspace(-4, 3, 300)
K_CCL = K_THEORY * H_VAL

THEORY_STYLES = {
    "PL": {"color": JOURNAL_COLORS["black"], "linestyle": "-", "label": "PL theory"},
    "BT_kp1": {
        "kp": 1.0,
        "ms": 1.5,
        "color": JOURNAL_COLORS["blue"],
        "linestyle": "--",
        "label": r"BT $k_p=1$ theory",
    },
    "BT_kp10": {
        "kp": 10.0,
        "ms": 1.5,
        "color": JOURNAL_COLORS["green"],
        "linestyle": "-.",
        "label": r"BT $k_p=10$ theory",
    },
}

BOX_MODELS = {
    "25": {
        "pl_label": "PL 25",
        "pl_template": DATA_DIR / "cdm_25_snap{}.npz",
        "pl_marker": "o",
        "pl_color": JOURNAL_COLORS["black"],
        "bt_models": {
            "BT_kp1": {
                "bt_label": r"BT $k_p=1$ 25",
                "ratio_label": r"BT $k_p=1$ 25 / PL 25",
                "bt_template": DATA_DIR / "bluetilted_kp1_ms1.5_25_snap{}.npz",
                "bt_marker": "^",
                "bt_color": JOURNAL_COLORS["blue"],
                "optional": False,
            },
            "BT_kp10": {
                "bt_label": r"BT $k_p=10$ 25",
                "ratio_label": r"BT $k_p=10$ 25 / PL 25",
                "bt_template": DATA_DIR / "bluetilted_kp10_ms1.5_25_snap{}.npz",
                "bt_marker": "v",
                "bt_color": JOURNAL_COLORS["green"],
                "optional": True,
            },
        },
    },
    "256": {
        "pl_label": "PL 256",
        "pl_template": DATA_DIR / "new_PL_256_1024_snap{}.npz",
        "pl_marker": "s",
        "pl_color": JOURNAL_COLORS["gray"],
        "bt_models": {
            "BT_kp1": {
                "bt_label": r"BT $k_p=1$ 256",
                "ratio_label": r"BT $k_p=1$ 256 / PL 256",
                "bt_template": DATA_DIR / "bluetilted_kp1_ms1.5_256_snap{}.npz",
                "bt_marker": "D",
                "bt_color": JOURNAL_COLORS["sky"],
                "optional": False,
            },
            "BT_kp10": {
                "bt_label": r"BT $k_p=10$ 256",
                "ratio_label": r"BT $k_p=10$ 256 / PL 256",
                "bt_template": DATA_DIR / "bluetilted_kp10_ms1.5_256_snap{}.npz",
                "bt_marker": "P",
                "bt_color": JOURNAL_COLORS["green"],
                "optional": True,
            },
        },
    },
}


def build_theory_interpolators(z_targets):
    cosmo_ccl = ccl.Cosmology(
        Omega_c=OMEGA_C,
        Omega_b=OMEGA_B,
        h=H_VAL,
        n_s=N_S,
        sigma8=SIGMA8,
        matter_power_spectrum="halofit",
        transfer_function="eisenstein_hu",
    )

    z_min = min(z_targets) * 0.9 if min(z_targets) > 0 else 0.0
    z_max = max(z_targets) * 1.1
    z_grid = np.linspace(z_min, z_max, max(50, len(z_targets) * 10))
    z_all = np.sort(np.unique(np.concatenate([z_grid, z_targets])))

    a_arr = 1.0 / (1.0 + z_all)
    pofk_lin_pl = np.array(
        [ccl.linear_matter_power(cosmo_ccl, k=K_CCL, a=a_) for a_ in a_arr]
    )
    pofk_lin_pl *= H_VAL**3

    hmcode_model = pyhmcode.Halomodel(pyhmcode.HMcode2020)

    hmc_pl = pyhmcode.Cosmology()
    hmc_pl.omega_m = OMEGA_M
    hmc_pl.omega_b = OMEGA_B
    hmc_pl.h = H_VAL
    hmc_pl.n_s = N_S
    hmc_pl.sigma8 = SIGMA8
    hmc_pl.log10_T_heat = 0
    hmc_pl.log10_M_min = 7.0
    hmc_pl.nu_min = 0.02
    hmc_pl.set_linear_power_spectrum(K_THEORY, z_all, pofk_lin_pl)
    pofk_nl_pl = pyhmcode.calculate_nonlinear_power_spectrum(
        cosmology=hmc_pl,
        halomodel=hmcode_model,
        fields=[pyhmcode.field_dmonly],
    )

    bt_interpolators = {}
    for key, style in THEORY_STYLES.items():
        if key == "PL":
            continue
        kp_bt = style["kp"]
        ms_bt = style["ms"]
        pofk_lin_bt = pofk_lin_pl.copy()
        bt_mask = K_THEORY > kp_bt
        pofk_lin_bt[:, bt_mask] *= (kp_bt ** (N_S - ms_bt)) * (
            K_THEORY[bt_mask] ** (ms_bt - N_S)
        )

        hmc_bt = pyhmcode.Cosmology()
        hmc_bt.omega_m = OMEGA_M
        hmc_bt.omega_b = OMEGA_B
        hmc_bt.h = H_VAL
        hmc_bt.n_s = N_S
        hmc_bt.sigma8 = SIGMA8
        hmc_bt.log10_T_heat = 0
        hmc_bt.log10_M_min = 6.0
        hmc_bt.nu_min = 0.02
        hmc_bt.set_linear_power_spectrum(K_THEORY, z_all, pofk_lin_bt)
        pofk_nl_bt = pyhmcode.calculate_nonlinear_power_spectrum(
            cosmology=hmc_bt,
            halomodel=hmcode_model,
            fields=[pyhmcode.field_dmonly],
        )
        bt_interpolators[key] = interp1d(
            z_all, np.log10(pofk_nl_bt), axis=0, kind="linear", fill_value="extrapolate"
        )

    return (
        interp1d(z_all, np.log10(pofk_nl_pl), axis=0, kind="linear", fill_value="extrapolate"),
        bt_interpolators,
    )


def theory_at_z(interpolator, z, k_values):
    logp_at_z = interpolator(z)
    logp = np.interp(np.log10(k_values), np.log10(K_THEORY), logp_at_z)
    return 10**logp


def load_power(template, snap):
    path = Path(str(template).format(snap))
    with np.load(path) as data:
        return data["k"], data["P"], float(data["z"]), path


def series_is_available(bt_key):
    for snap in SNAP_LIST:
        for box in BOX_MODELS.values():
            template = box["bt_models"][bt_key]["bt_template"]
            if not Path(str(template).format(snap)).exists():
                return False
    return True


def log_bin_for_plot(k, y, n_bins=N_PLOT_BINS):
    k = np.asarray(k)
    y = np.asarray(y)
    valid = np.isfinite(k) & np.isfinite(y) & (k > 0) & (y > 0)
    k = k[valid]
    y = y[valid]
    if len(k) == 0:
        return k, y

    edges = np.logspace(np.log10(k.min()), np.log10(k.max()), n_bins + 1)
    k_binned = []
    y_binned = []
    for left, right in zip(edges[:-1], edges[1:]):
        mask = (k >= left) & (k < right)
        if np.any(mask):
            k_binned.append(10 ** np.mean(np.log10(k[mask])))
            y_binned.append(np.median(y[mask]))
    return np.asarray(k_binned), np.asarray(y_binned)


def interpolate_ratio(k_target, k_ref, p_ref, p_target):
    k_target = np.asarray(k_target)
    k_ref = np.asarray(k_ref)
    p_ref = np.asarray(p_ref)
    p_target = np.asarray(p_target)

    ref_valid = np.isfinite(k_ref) & np.isfinite(p_ref) & (k_ref > 0) & (p_ref > 0)
    k_ref = k_ref[ref_valid]
    p_ref = p_ref[ref_valid]
    target_valid = (
        np.isfinite(k_target)
        & np.isfinite(p_target)
        & (k_target > 0)
        & (p_target > 0)
        & (k_target >= k_ref.min())
        & (k_target <= k_ref.max())
    )
    k_target = k_target[target_valid]
    p_target = p_target[target_valid]
    ref_interp = 10 ** np.interp(np.log10(k_target), np.log10(k_ref), np.log10(p_ref))
    return k_target, p_target / ref_interp


def mark_reliability(ax_top, ax_ratio, annotate=False):
    for ax in (ax_top, ax_ratio):
        ax.axvline(K_NY_256, color="0.35", linestyle=":", linewidth=0.8, alpha=0.8, zorder=1)
        ax.axvline(K_NY_25, color="0.25", linestyle="--", linewidth=0.85, alpha=0.85, zorder=1)
        ax.axvspan(K_NY_25, 1.0e3, color="0.82", alpha=0.16, lw=0, zorder=0)
    ax_ratio.axhspan(0.9, 1.1, color="0.45", alpha=0.10, lw=0, zorder=0)
    if annotate:
        ax_top.text(
            0.96,
            0.72,
            r"dotted/dashed: $k_{\rm Ny}$",
            transform=ax_top.transAxes,
            ha="right",
            va="top",
            fontsize=7.0,
            color="0.25",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.80, "pad": 0.9},
        )


def main():
    apply_journal_style(base_fontsize=9.0)
    z_targets = []
    for snap in SNAP_LIST:
        _, _, pl_z, _ = load_power(BOX_MODELS["25"]["pl_template"], snap)
        z_targets.append(pl_z)
    interp_pl, bt_interpolators = build_theory_interpolators(sorted(set(z_targets)))
    active_bt_keys = [
        key
        for key in THEORY_STYLES
        if key != "PL" and (key == "BT_kp1" or series_is_available(key))
    ]

    fig = plt.figure(figsize=(8.8, 6.2))
    outer_grid = gridspec.GridSpec(
        2,
        2,
        figure=fig,
        left=0.105,
        right=0.985,
        bottom=0.105,
        top=0.965,
        hspace=0.12,
        wspace=0.10,
    )

    source_paths = []
    for idx, snap in enumerate(SNAP_LIST):
        first_box = BOX_MODELS["25"]
        _, _, pl_z, _ = load_power(first_box["pl_template"], snap)

        pl_theory_full = theory_at_z(interp_pl, pl_z, K_THEORY)
        bt_theory_full = {
            key: theory_at_z(bt_interpolators[key], pl_z, K_THEORY) for key in active_bt_keys
        }

        inner_grid = gridspec.GridSpecFromSubplotSpec(
            2,
            1,
            subplot_spec=outer_grid[idx],
            height_ratios=[3, 1],
            hspace=0.03,
        )
        ax_top = fig.add_subplot(inner_grid[0])
        ax_ratio = fig.add_subplot(inner_grid[1], sharex=ax_top)

        row = idx // 2
        col = idx % 2

        ax_top.loglog(
            K_THEORY,
            pl_theory_full,
            THEORY_STYLES["PL"]["linestyle"],
            color=THEORY_STYLES["PL"]["color"],
            linewidth=1.25,
            alpha=0.9,
            label=THEORY_STYLES["PL"]["label"],
        )
        for bt_key in active_bt_keys:
            style = THEORY_STYLES[bt_key]
            ax_top.loglog(
                K_THEORY,
                bt_theory_full[bt_key],
                style["linestyle"],
                color=style["color"],
                linewidth=1.25,
                alpha=0.9,
                label=style["label"],
            )
            ax_ratio.semilogx(
                K_THEORY,
                bt_theory_full[bt_key] / pl_theory_full,
                style["linestyle"],
                color=style["color"],
                linewidth=1.2,
                alpha=0.85,
                label=style["label"].replace(" theory", r" theory / PL"),
            )

        for box in BOX_MODELS.values():
            pl_k, pl_p, box_pl_z, pl_path = load_power(box["pl_template"], snap)
            k_pl, p_pl = log_bin_for_plot(pl_k, pl_p)
            source_paths.append(pl_path)

            ax_top.loglog(
                k_pl,
                p_pl,
                box["pl_marker"],
                color=box["pl_color"],
                markersize=3.1,
                markerfacecolor="none",
                markeredgewidth=0.75,
                alpha=0.9,
                label=box["pl_label"],
            )
            for bt_key in active_bt_keys:
                bt_config = box["bt_models"][bt_key]
                bt_k, bt_p, box_bt_z, bt_path = load_power(bt_config["bt_template"], snap)
                source_paths.append(bt_path)
                if abs(box_pl_z - box_bt_z) > 1e-5:
                    print(
                        f"Warning: redshift mismatch for snap {snap}: "
                        f"{box['pl_label']}={box_pl_z}, {bt_config['bt_label']}={box_bt_z}"
                    )

                k_bt, p_bt = log_bin_for_plot(bt_k, bt_p)
                k_ratio_raw, ratio_bt_pl = interpolate_ratio(bt_k, pl_k, pl_p, bt_p)
                k_ratio, ratio_plot = log_bin_for_plot(k_ratio_raw, ratio_bt_pl)

                ax_top.loglog(
                    k_bt,
                    p_bt,
                    bt_config["bt_marker"],
                    color=bt_config["bt_color"],
                    markersize=3.1,
                    markerfacecolor="none",
                    markeredgewidth=0.75,
                    alpha=0.9,
                    label=bt_config["bt_label"],
                )
                ax_ratio.semilogx(
                    k_ratio,
                    ratio_plot,
                    bt_config["bt_marker"],
                    color=bt_config["bt_color"],
                    markersize=2.9,
                    markerfacecolor="none",
                    markeredgewidth=0.75,
                    alpha=0.9,
                    label=bt_config["ratio_label"],
                )
        ax_ratio.axhline(1.0, color="0.45", linestyle=":", linewidth=0.8)
        mark_reliability(ax_top, ax_ratio, annotate=(idx == 0))

        ax_top.set_xlim(1e-2, 1e3)
        ax_top.set_ylim(1e-5, 1e5)
        ax_ratio.set_ylim(0.0, 7.2)
        format_axes(ax_top)
        format_axes(ax_ratio)

        if col == 0:
            ax_top.set_ylabel(r"$P(k)\,[(\mathrm{Mpc}/h)^3]$")
            ax_ratio.set_ylabel("BT/PL")
        else:
            ax_top.tick_params(labelleft=False)
            ax_ratio.tick_params(labelleft=False)
        if row == 1:
            ax_ratio.set_xlabel(r"$k\,[h\,\mathrm{Mpc}^{-1}]$")
        else:
            ax_ratio.tick_params(labelbottom=False)

        panel_label(
            ax_top,
            rf"$z={format_redshift(pl_z, 2)}$",
            loc=(0.94, 0.90),
            ha="right",
            fontsize=9.5,
        )
        plt.setp(ax_top.get_xticklabels(), visible=False)

        if idx == 0:
            panel_label(
                ax_top,
                BOX_LABEL,
                loc=(0.50, 0.90),
                ha="center",
                fontsize=8.7,
            )
            ax_top.legend(
                loc="lower left",
                ncol=3,
                fontsize=7.0,
                frameon=True,
                framealpha=0.72,
                edgecolor="none",
                borderpad=0.25,
                labelspacing=0.18,
                handletextpad=0.35,
            )
            ax_ratio.legend(
                loc="upper left",
                ncol=2,
                fontsize=6.8,
                frameon=True,
                framealpha=0.72,
                edgecolor="none",
                borderpad=0.2,
                handlelength=1.5,
            )

    save_publication_figure(fig, OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")
    print("Sources:")
    for path in sorted(set(source_paths)):
        print(f"  {path}")


if __name__ == "__main__":
    main()
