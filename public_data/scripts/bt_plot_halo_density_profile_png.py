#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晕密度轮廓分析脚本
Halo density profile analysis script
分析PL和Bluetilted模拟中的晕密度轮廓和NFW拟合

本脚本绘制 median-c stack 和内置功率谱模型驱动的理论参考曲线（请在论文图注中保持一致）：
1) median-c stack:
   对每个质量 bin 内的每个晕，使用其自身 C200 在统一 r/R200 网格上
   计算 NFW 轮廓，再在每个半径点取中位数，得到堆叠“模拟统计”曲线。
   注意 SOAP catalog 这里只提供 SO 标量属性，不提供逐粒子径向密度 bin；
   因此该曲线不是直接的粒子分箱 density profile。
2) theory NFW:
   使用 Colossus 的 Diemer19 c(M) 关系，并分别传入内置 PL/BT 功率谱模型，
   给出三条 NFW 理论参考。

arXiv:2412.16072 的 Fig. 5 画法是：simulation = 实线粒子分箱密度轮廓，
reference = 虚线 NFW fitting；纵轴为物理密度 rho [M_sun/kpc^3]，
横轴为 r/R200m。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import h5py
import sys
from pathlib import Path
from colossus import settings as colossus_settings
from colossus.cosmology import cosmology
from colossus.halo import concentration

SCRIPT_PATH = Path(__file__).resolve()
PROJECT_BIG_SIM_ENV = os.environ.get("PROJECT_BIG_SIM_ROOT")
_ROOT_ANCHORS = (SCRIPT_PATH.parent, *SCRIPT_PATH.parents, Path.cwd(), *Path.cwd().parents)
_ROOT_CANDIDATES = []
if PROJECT_BIG_SIM_ENV:
    _ROOT_CANDIDATES.append(Path(PROJECT_BIG_SIM_ENV).expanduser())
for _anchor in _ROOT_ANCHORS:
    _ROOT_CANDIDATES.extend((_anchor, _anchor / "project_big_sim", _anchor.parent / "project_big_sim"))
WORKSPACE_ROOT = next(
    (
        p
        for p in _ROOT_CANDIDATES
        if p.name == "project_big_sim" and (p / "data" / "PL").exists()
    ),
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

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes, save_publication_figure

# ===================================================
# 配置参数
# ===================================================
H0 = 67.4  # 哈勃常数 (km/s/Mpc)
omega_m = 0.315  # 物质密度参数 (Planck 2018)

DATA_ROOT = WORKSPACE_ROOT / "data"
PAPERPLOT_ROOT_ENV = os.environ.get("PAPERPLOT_ROOT")
if PAPERPLOT_ROOT_ENV:
    PAPERPLOT_ROOT = Path(PAPERPLOT_ROOT_ENV).expanduser().resolve()
else:
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

COLOSSUS_BASE_DIR = PAPERPLOT_ROOT / "cache" / "colossus"
COLOSSUS_BASE_DIR.mkdir(parents=True, exist_ok=True)
colossus_settings.BASE_DIR = str(COLOSSUS_BASE_DIR)

# 设置宇宙学。必须在设置 Colossus cache 目录后初始化，避免写入只读 home。
cosmology.setCosmology('planck18')

CDM_SOAP_PATH = DATA_ROOT / "PL/PL_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"
BT_SOAP_PATH = DATA_ROOT / "bluetilted/kp_1_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"
BT_KP10_SOAP_PATH = DATA_ROOT / "bluetilted/kp_10_ms_1.5_25_1024/SOAP_full_000_056/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"

# 物理参数
MASS_TOLERANCE = 0.2
TARGET_MASSES = [1e8, 1e9, 1e10, 1e11]
PANEL_COLUMNS = 2
MAIN_PARTICLE_MASS_MSUN = 1.89e6
SOFTENING_KPC_Z0 = 0.725
THEORY_CONCENTRATION_MODEL = "diemer19"
THEORY_CONCENTRATION_LABEL = "Diemer19"
THEORY_PS_SPECS = [
    ("PL", {"model": "eisenstein98_pl"}),
    ("BTKP1", {"model": "eisenstein98_bt"}),
    ("BTKP10", {"model": "eisenstein98_bt_soft"}),
]

# ===================================================
# 核心函数
# ===================================================
def calculate_critical_density(H0=67.4):
    """计算宇宙临界密度"""
    G = 6.67430e-11      # 万有引力常数 (m³ kg⁻¹ s⁻²)
    km_to_m = 1000.0     # 千米到米转换
    Mpc_to_m = 3.0856775814671916e22  # 兆秒差距到米转换
    Msun = 1.98847e30    # 太阳质量 (kg)

    # 计算H0的SI单位 (s⁻¹)
    H0_SI = H0 * km_to_m / Mpc_to_m

    # 计算临界密度 (kg/m³)
    rho_c_kg_m3 = 3 * H0_SI**2 / (8 * np.pi * G)

    # 转换为太阳质量/兆秒差距³
    rho_c_Msun_Mpc3 = rho_c_kg_m3 * (Mpc_to_m**3) / Msun

    return rho_c_Msun_Mpc3

def load_halo_data(soap_path):
    """从SOAP文件加载晕数据"""
    if not soap_path.exists():
        raise FileNotFoundError(f"SOAP halo catalog not found: {soap_path}")
    with h5py.File(soap_path, 'r') as soap_file:
        M200 = np.array(soap_file['/SO/200_mean/TotalMass'])
        C200 = np.array(soap_file['/SO/200_mean/Concentration'])
        R200 = np.array(soap_file['/SO/200_mean/SORadius'])
        if '/SO/200_mean/NumberOfDarkMatterParticles' in soap_file:
            N200 = np.array(soap_file['/SO/200_mean/NumberOfDarkMatterParticles'])
        else:
            N200 = M200 * 1e10 / MAIN_PARTICLE_MASS_MSUN

        # 转换为物理单位
        M200_Msun = M200 * 1e10  # 转换为 M☉
        R200_kpc = R200 * 1000   # 转换为 kpc

        return M200_Msun, C200, R200_kpc, N200

def rho_mean_z0_msun_kpc3():
    """Mean matter density at z=0 in physical Msun/kpc^3."""
    return omega_m * calculate_critical_density(H0) / 1.0e9

def calculate_nfw_profile(C200, R200, delta_vir=200, n_points=100):
    """计算 NFW 密度轮廓，返回物理单位 Msun/kpc^3。"""
    # 计算NFW参数
    A_NFW = np.log(1 + C200) - C200 / (1 + C200)
    delta_s = (C200**3 * delta_vir) / (3 * A_NFW)
    r_s = R200 / C200

    # 计算密度轮廓
    r = np.logspace(-2, 0, n_points) * R200
    y = r / r_s
    rho_r = delta_s / (y * (1 + y)**2)

    # /SO/200_mean uses 200 times the mean matter density.
    rho_r_final = rho_r * rho_mean_z0_msun_kpc3()

    return r, rho_r_final

def calculate_stacked_sim_profile(C200_array, delta_vir=200, n_points=24, max_halos=3000):
    """
    用模拟晕浓度分布构建堆叠曲线（图中 "median-c stack"）。
    做法：逐晕计算 NFW 归一化密度，再在每个 r/R200 点取中位数。
    误差棒为 bootstrap median 的 16-84 percentile uncertainty。
    """
    c = np.asarray(C200_array, dtype=float)
    c = c[np.isfinite(c) & (c > 0)]
    if c.size == 0:
        return None, None
    if c.size > max_halos:
        rng = np.random.default_rng(42)
        c = c[rng.choice(c.size, size=max_halos, replace=False)]

    x = np.logspace(-2, 0, n_points)  # r/R200
    c2 = c[:, None]
    a_nfw = np.log(1.0 + c2) - c2 / (1.0 + c2)
    valid = a_nfw > 0
    delta_s = np.full_like(a_nfw, np.nan, dtype=float)
    delta_s[valid] = (c2[valid] ** 3 * delta_vir) / (3.0 * a_nfw[valid])
    y = x[None, :] * c2
    rho_norm = delta_s / (y * (1.0 + y) ** 2)

    rho = rho_norm * rho_mean_z0_msun_kpc3()
    rho_med = np.nanmedian(rho, axis=0)
    if c.size > 1:
        rng = np.random.default_rng(12345)
        boot_idx = rng.integers(0, c.size, size=(160, c.size))
        boot_med = np.nanmedian(rho[boot_idx, :], axis=1)
        rho_lo, rho_hi = np.nanpercentile(boot_med, [16.0, 84.0], axis=0)
    else:
        rho_lo = rho_med.copy()
        rho_hi = rho_med.copy()
    return x, rho_med, rho_lo, rho_hi

def calculate_ratio_profile(numerator, denominator):
    """Compute BT/PL median ratio with asymmetric percentile-band propagation."""
    x_num, med_num, lo_num, hi_num = numerator
    x_den, med_den, lo_den, hi_den = denominator
    if not np.allclose(x_num, x_den):
        med_den = np.interp(x_num, x_den, med_den)
        lo_den = np.interp(x_num, x_den, lo_den)
        hi_den = np.interp(x_num, x_den, hi_den)

    valid = (med_num > 0) & (med_den > 0) & (lo_den > 0) & (hi_den > 0)
    ratio = np.full_like(med_num, np.nan, dtype=float)
    ratio_lo = np.full_like(med_num, np.nan, dtype=float)
    ratio_hi = np.full_like(med_num, np.nan, dtype=float)
    ratio[valid] = med_num[valid] / med_den[valid]
    ratio_lo[valid] = lo_num[valid] / hi_den[valid]
    ratio_hi[valid] = hi_num[valid] / lo_den[valid]
    yerr_low = np.maximum(ratio - ratio_lo, 0.0)
    yerr_high = np.maximum(ratio_hi - ratio, 0.0)
    return x_num, ratio, yerr_low, yerr_high

def calculate_theory_nfw_profile(target_mass, ps_args, delta_vir=200, n_points=100):
    """Diemer19 c(M) NFW reference for SO/200_mean at z=0."""
    c_theory = concentration.concentration(
        target_mass,
        '200m',
        0.0,
        model=THEORY_CONCENTRATION_MODEL,
        ps_args=ps_args,
    )
    if not np.isfinite(c_theory) or c_theory <= 0:
        return None, None

    rho_mean = rho_mean_z0_msun_kpc3()
    r200 = (3.0 * target_mass / (4.0 * np.pi * delta_vir * rho_mean)) ** (1.0 / 3.0)
    r, rho = calculate_nfw_profile(float(c_theory), r200, delta_vir=delta_vir, n_points=n_points)
    return r / r200, rho

def find_mass_group(M200, C200, R200, target_mass, mass_tolerance=0.2):
    """找到指定质量范围内的晕群"""
    lower_bound = target_mass * (1 - mass_tolerance)
    upper_bound = target_mass * (1 + mass_tolerance)

    group_mask = (M200 >= lower_bound) & (M200 <= upper_bound)
    num_halos = np.sum(group_mask)

    if num_halos > 0:
        C200_mean = np.mean(C200[group_mask])
        R200_mean = np.mean(R200[group_mask])
        M200_mean = np.mean(M200[group_mask])

        print(f"Found {num_halos} halos in mass range {lower_bound:.2e} - {upper_bound:.2e} Msun")
        print(f"Mean mass: {M200_mean:.2e} Msun")
        print(f"平均浓度: {C200_mean:.2f}")
        print(f"平均半径: {R200_mean:.2f} kpc")

        return C200_mean, R200_mean, M200_mean, num_halos, group_mask
    else:
        print(f"No halos found in mass range {lower_bound:.2e} - {upper_bound:.2e} Msun")
        return None, None, None, 0, None

def calculate_halo_average_density(M200_array, R200_array):
    """计算晕群的平均密度 (总质量 / 总体积)"""
    total_mass = np.sum(M200_array)
    total_volume = np.sum(4/3 * np.pi * R200_array**3)
    average_density = total_mass / total_volume
    return average_density

def calculate_rho_mean(M200, R200):
    """计算单个晕的平均密度"""
    volume = 4/3 * np.pi * R200**3
    rho_mean = M200 / volume
    return rho_mean

def plot_halo_profiles(cdm_data, bt_data, bt_kp10_data):
    """
    绘制晕密度轮廓对比图。
    - median-c stack: 使用该 bin 全部晕的 C200 逐晕计算后做中位数堆叠。
    - theory NFW:     使用 Diemer19 c(M) 关系和内置 PL/BT 功率谱模型给出理论参考。
    """
    apply_journal_style(base_fontsize=11.2)
    n_panels = len(TARGET_MASSES)
    n_cols = min(PANEL_COLUMNS, n_panels)
    n_rows = int(np.ceil(n_panels / n_cols))
    plot_rows = n_rows * 2
    fig, axes = plt.subplots(
        plot_rows,
        n_cols,
        figsize=(7.2, 3.15 * n_rows),
        gridspec_kw={"height_ratios": [3.0, 1.05] * n_rows},
        sharex=False,
        sharey=False,
        squeeze=False,
    )

    colors = [JOURNAL_COLORS["black"], JOURNAL_COLORS["blue"], JOURNAL_COLORS["green"]]
    labels = ['PL', 'BTKP1', 'BTKP10']
    model_items = list(zip([cdm_data, bt_data, bt_kp10_data], colors, labels))
    stack_legend_handles = [
        Line2D([0], [0], color=colors[0], linestyle='none', marker='o',
               markerfacecolor='white', markeredgewidth=0.8, markersize=3.0),
        Line2D([0], [0], color=colors[1], linestyle='none', marker='o',
               markerfacecolor='white', markeredgewidth=0.8, markersize=3.0),
        Line2D([0], [0], color=colors[2], linestyle='none', marker='o',
               markerfacecolor='white', markeredgewidth=0.8, markersize=3.0),
    ]
    stack_legend_labels = [
        'PL median-c stack',
        'BTKP1 median-c stack',
        'BTKP10 median-c stack',
    ]
    theory_legend_handles = [
        Line2D([0], [0], color=colors[0], linestyle='--', linewidth=1.0),
        Line2D([0], [0], color=colors[1], linestyle='--', linewidth=1.0),
        Line2D([0], [0], color=colors[2], linestyle='--', linewidth=1.0),
        Line2D([0], [0], color='0.45', linestyle=':', linewidth=0.9),
    ]
    theory_legend_labels = [
        f'PL {THEORY_CONCENTRATION_LABEL} theory',
        f'BTKP1 {THEORY_CONCENTRATION_LABEL} theory',
        f'BTKP10 {THEORY_CONCENTRATION_LABEL} theory',
        r'$\epsilon/R_{200m}$ marker',
    ]

    for i, target_mass in enumerate(TARGET_MASSES):
        panel_row = i // n_cols
        col = i % n_cols
        ax = axes[2 * panel_row, col]
        ratio_ax = axes[2 * panel_row + 1, col]
        panel_counts = []
        panel_npart = []
        panel_softening_marks = []
        panel_profiles = {}
        theory_profiles = {}

        # 计算 median-c stack。SOAP catalog 不含逐粒子 radial density bins。
        for model_data, color, label in model_items:
            stats = find_mass_group(model_data['M200'], model_data['C200'], model_data['R200'], target_mass)

            if stats[0] is not None:
                _, r_mean, _, num_halos, group_mask = stats
                panel_counts.append(num_halos)
                panel_npart.append(np.nanmedian(model_data['N200'][group_mask]))
                if np.isfinite(r_mean) and r_mean > 0:
                    panel_softening_marks.append(SOFTENING_KPC_Z0 / r_mean)

                profile = calculate_stacked_sim_profile(model_data['C200'][group_mask])
                if profile[0] is not None:
                    x_sim, rho_med, rho_lo, rho_hi = profile
                    panel_profiles[label] = profile
                    sim_label = f"{label} median-c stack" if i == 0 else None
                    ax.errorbar(
                        x_sim,
                        rho_med,
                        yerr=np.vstack((rho_med - rho_lo, rho_hi - rho_med)),
                        color=color,
                        linestyle='none',
                        marker='o',
                        markersize=2.6,
                        markerfacecolor='white',
                        markeredgewidth=0.8,
                        elinewidth=0.45,
                        capsize=1.1,
                        capthick=0.45,
                        alpha=0.9,
                        label=sim_label,
                    )

        for (theory_label_base, ps_args), color in zip(THEORY_PS_SPECS, colors):
            x_theory, rho_theory = calculate_theory_nfw_profile(target_mass, ps_args)
            if x_theory is not None:
                theory_profiles[theory_label_base] = (x_theory, rho_theory)
                theory_label = (
                    f"{theory_label_base} {THEORY_CONCENTRATION_LABEL} theory"
                    if i == 0
                    else None
                )
                ax.loglog(
                    x_theory,
                    rho_theory,
                    color=color,
                    linestyle='--',
                    linewidth=1.0,
                    alpha=0.95,
                    label=theory_label,
                )

        pl_profile = panel_profiles.get('PL')
        if pl_profile is not None:
            for label, color in [('BTKP1', colors[1]), ('BTKP10', colors[2])]:
                bt_profile = panel_profiles.get(label)
                if bt_profile is None:
                    continue
                x_ratio, ratio, yerr_low, yerr_high = calculate_ratio_profile(bt_profile, pl_profile)
                ratio_label = f"{label}/PL median" if i == 0 else None
                ratio_ax.errorbar(
                    x_ratio,
                    ratio,
                    yerr=np.vstack((yerr_low, yerr_high)),
                    color=color,
                    linestyle='none',
                    marker='o',
                    markersize=2.3,
                    markerfacecolor='white',
                    markeredgewidth=0.75,
                    elinewidth=0.42,
                    capsize=1.0,
                    capthick=0.42,
                    alpha=0.9,
                    label=ratio_label,
                )

        theory_pl = theory_profiles.get('PL')
        if theory_pl is not None:
            x_pl, rho_pl = theory_pl
            for label, color in [('BTKP1', colors[1]), ('BTKP10', colors[2])]:
                theory_bt = theory_profiles.get(label)
                if theory_bt is None:
                    continue
                x_bt, rho_bt = theory_bt
                rho_pl_on_bt = np.interp(x_bt, x_pl, rho_pl)
                valid = rho_pl_on_bt > 0
                theory_ratio = np.full_like(rho_bt, np.nan, dtype=float)
                theory_ratio[valid] = rho_bt[valid] / rho_pl_on_bt[valid]
                ratio_ax.plot(
                    x_bt,
                    theory_ratio,
                    color=color,
                    linestyle='--',
                    linewidth=0.9,
                    alpha=0.95,
                )

        # 设置子图属性 - 标题移到左下角
        if target_mass >= 1e12:
            mass_label = rf"{target_mass/1e12:.1f}\times10^{{12}}\,M_\odot"
        elif target_mass >= 1e11:
            mass_label = rf"{target_mass/1e11:.1f}\times10^{{11}}\,M_\odot"
        elif target_mass >= 1e10:
            mass_label = rf"{target_mass/1e10:.1f}\times10^{{10}}\,M_\odot"
        elif target_mass >= 1e9:
            mass_label = rf"{target_mass/1e9:.1f}\times10^{{9}}\,M_\odot"
        elif target_mass >= 1e8:
            mass_label = rf"{target_mass/1e8:.1f}\times10^{{8}}\,M_\odot"
        else:
            mass_label = rf"{target_mass/1e7:.1f}\times10^{{7}}\,M_\odot"

        # Compact per-panel labels keep the resolution notes visible after column scaling.
        npart_text = ""
        if panel_npart:
            npart_text = rf"; $N_p\simeq{np.nanmedian(panel_npart):.0f}$"
        title_text = rf'$\log_{{10}}M={np.log10(target_mass):.1f}$ (${mass_label}$){npart_text}'
        ax.text(0.04, 0.04, title_text, transform=ax.transAxes,
                verticalalignment='bottom', horizontalalignment='left',
                fontsize=7.8,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.88, pad=0.8))
        if panel_counts:
            ax.text(
                0.98,
                0.96,
                "N halos: " + "/".join(f"{n:g}" for n in panel_counts),
                transform=ax.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                fontsize=6.8,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.86, pad=0.7),
            )
        if panel_softening_marks:
            softening_x = float(np.nanmedian(panel_softening_marks))
            if 1.0e-2 <= softening_x <= 1.0:
                ax.axvline(softening_x, color='0.45', linestyle=':', linewidth=0.9, alpha=0.9)
                ratio_ax.axvline(softening_x, color='0.45', linestyle=':', linewidth=0.85, alpha=0.85)

        ax.set_xscale('log')
        ax.set_yscale('log')
        ratio_ax.set_xscale('log')
        ratio_ax.set_yscale('log')
        ratio_ax.axhline(1.0, color='0.55', linewidth=0.7, alpha=0.85)
        ratio_ax.set_ylim(0.35, 6.0)

        if panel_row == n_rows - 1:
            ratio_ax.set_xlabel(r'$r/R_{200m}$')
        else:
            ratio_ax.set_xlabel('')
            ratio_ax.tick_params(labelbottom=False)
        ax.set_xlabel('')
        ax.tick_params(labelbottom=False)

        # 只在最左边显示y轴标题
        if col == 0:  # 第一列
            ax.set_ylabel(r'$\rho(r)\,[M_\odot\,{\rm kpc}^{-3}]$')
            ratio_ax.set_ylabel(r'BT/PL')
        else:
            ax.set_ylabel('')
            ratio_ax.set_ylabel('')

        format_axes(ax, grid=True)
        format_axes(ratio_ax, grid=True)
        ax.tick_params(labelleft=(col == 0), labelright=False, labeltop=False)
        ratio_ax.tick_params(labelleft=(col == 0), labelright=False, labeltop=False)

    for j in range(n_panels, n_rows * n_cols):
        axes[2 * (j // n_cols), j % n_cols].set_visible(False)
        axes[2 * (j // n_cols) + 1, j % n_cols].set_visible(False)

    stack_legend_ax = axes[0, 0]
    theory_legend_ax = axes[0, min(1, n_cols - 1)]
    legend_kwargs = dict(
        loc='upper right',
        bbox_to_anchor=(0.985, 0.84),
        fontsize=6.1,
        frameon=True,
        framealpha=0.80,
        edgecolor='none',
        borderpad=0.16,
        labelspacing=0.08,
        handlelength=1.05,
        handletextpad=0.25,
    )
    stack_legend_ax.legend(stack_legend_handles, stack_legend_labels, **legend_kwargs)
    theory_legend_ax.legend(theory_legend_handles, theory_legend_labels, **legend_kwargs)

    fig.subplots_adjust(top=0.965, bottom=0.075, left=0.10, right=0.99, hspace=0.08, wspace=0.06)
    save_publication_figure(fig, PAPERPLOT_ROOT / "figures" / "halo-density.png")
    print("Figure saved: halo-density.png")

# ===================================================
# 主程序
# ===================================================
def main():
    """主函数"""
    print("Starting halo density profile analysis...")

    try:
        # 1. 加载模型数据
        print("Loading model data...")
        cdm_M200, cdm_C200, cdm_R200, cdm_N200 = load_halo_data(CDM_SOAP_PATH)
        bt_M200, bt_C200, bt_R200, bt_N200 = load_halo_data(BT_SOAP_PATH)
        bt_kp10_M200, bt_kp10_C200, bt_kp10_R200, bt_kp10_N200 = load_halo_data(BT_KP10_SOAP_PATH)

        print(f"PL: {len(cdm_M200)} halos")
        print(f"BT (kp=1): {len(bt_M200)} halos")
        print(f"BT (kp=10): {len(bt_kp10_M200)} halos")

        # 2. 计算宇宙临界密度
        rho_crit = calculate_critical_density(H0)
        print(f"\nCritical density: {rho_crit:.3e} Msun/Mpc^3")

        # 3. 计算晕群平均密度
        print("\nHalo sample mean densities:")
        cdm_avg_density = calculate_halo_average_density(cdm_M200, cdm_R200)
        bt_avg_density = calculate_halo_average_density(bt_M200, bt_R200)
        bt_kp10_avg_density = calculate_halo_average_density(bt_kp10_M200, bt_kp10_R200)

        print(f"PL mean density: {cdm_avg_density:.3e} Msun/kpc^3")
        print(f"BT (kp=1) mean density: {bt_avg_density:.3e} Msun/kpc^3")
        print(f"BT (kp=10) mean density: {bt_kp10_avg_density:.3e} Msun/kpc^3")

        # 4. 分析目标质量组
        print("\nAnalyzing target mass bins...")
        for target_mass in TARGET_MASSES:
            print(f"\nMass bin: {target_mass:.3e} Msun")

            # PL模型
            cdm_stats = find_mass_group(cdm_M200, cdm_C200, cdm_R200, target_mass, MASS_TOLERANCE)
            if cdm_stats[0] is not None:
                rho_mean_cdm = calculate_rho_mean(cdm_stats[2], cdm_stats[1])
                print(f"  PL: {cdm_stats[3]} halos, mean density: {rho_mean_cdm:.3e} Msun/kpc^3")

            # BT模型
            bt_stats = find_mass_group(bt_M200, bt_C200, bt_R200, target_mass, MASS_TOLERANCE)
            if bt_stats[0] is not None:
                rho_mean_bt = calculate_rho_mean(bt_stats[2], bt_stats[1])
                print(f"  BT (kp=1): {bt_stats[3]} halos, mean density: {rho_mean_bt:.3e} Msun/kpc^3")

            # BT KP10模型
            bt_kp10_stats = find_mass_group(bt_kp10_M200, bt_kp10_C200, bt_kp10_R200, target_mass, MASS_TOLERANCE)
            if bt_kp10_stats[0] is not None:
                rho_mean_bt_kp10 = calculate_rho_mean(bt_kp10_stats[2], bt_kp10_stats[1])
                print(f"  BT (kp=10): {bt_kp10_stats[3]} halos, mean density: {rho_mean_bt_kp10:.3e} Msun/kpc^3")

        # 5. 绘制图表
        print("\nPlotting density profiles...")
        cdm_data = {'M200': cdm_M200, 'C200': cdm_C200, 'R200': cdm_R200, 'N200': cdm_N200}
        bt_data = {'M200': bt_M200, 'C200': bt_C200, 'R200': bt_R200, 'N200': bt_N200}
        bt_kp10_data = {'M200': bt_kp10_M200, 'C200': bt_kp10_C200, 'R200': bt_kp10_R200, 'N200': bt_kp10_N200}
        plot_halo_profiles(cdm_data, bt_data, bt_kp10_data)

        print("\nAnalysis complete.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
