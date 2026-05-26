#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晕密度轮廓分析脚本
Halo density profile analysis script
分析PL和Bluetilted模拟中的晕密度轮廓和NFW拟合

本脚本同时绘制两类曲线（请在论文图注中保持一致）：
1) mean-c NFW:
   对每个质量 bin，先计算该 bin 内晕的平均参数 <C200>, <R200>，
   再用这组平均参数计算一条 NFW 轮廓。
2) median-c NFW:
   对每个质量 bin 内的每个晕，使用其自身 C200 在统一 r/R200 网格上
   计算 NFW 轮廓，再在每个半径点取中位数，得到堆叠“模拟统计”曲线。

因此，mean-c NFW 与 median-c NFW 的主要区别是统计方式不同（均值参数单曲线 vs
逐晕计算后中位数堆叠），而非采用了不同的密度公式。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import h5py
import sys
from pathlib import Path
from colossus.cosmology import cosmology
from colossus.halo import profile_nfw

SCRIPT_PATH = Path(__file__).resolve()
WORKSPACE_ROOT = next(
    (
        p
        for p in (SCRIPT_PATH.parent, *SCRIPT_PATH.parents, Path.cwd(), *Path.cwd().parents)
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

# 设置宇宙学
cosmo = cosmology.setCosmology('planck18')

# ===================================================
# 配置参数
# ===================================================
H0 = 67.4  # 哈勃常数 (km/s/Mpc)
omega_m = 0.315  # 物质密度参数 (Planck 2018)

DATA_ROOT = WORKSPACE_ROOT / "data"
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
CDM_SOAP_PATH = DATA_ROOT / "PL/PL_25_1024/SOAP/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"
BT_SOAP_PATH = DATA_ROOT / "bluetilted/kp_1_ms_1.5_25_1024/SOAP/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"
BT_KP10_SOAP_PATH = DATA_ROOT / "bluetilted/kp_10_ms_1.5_25_1024/SOAP/simulation_test/SOAP_uncompressed/HBTplus/halo_properties_0056.hdf5"

# 物理参数
MASS_TOLERANCE = 0.2
TARGET_MASSES = [1e8, 1e9, 1e10, 1e11]
PANEL_COLUMNS = 2
MAIN_PARTICLE_MASS_MSUN = 1.89e6
SOFTENING_KPC_Z0 = 0.725

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

def calculate_nfw_profile(C200, R200, delta_vir=200):
    """计算NFW密度轮廓"""
    # 计算NFW参数
    A_NFW = np.log(1 + C200) - C200 / (1 + C200)
    delta_s = (C200**3 * delta_vir) / (3 * A_NFW)
    r_s = R200 / C200

    # 计算密度轮廓
    r = np.logspace(-2, 0, 100) * R200
    y = r / r_s
    rho_r = delta_s / (y * (1 + y)**2)

    # 乘以临界密度和omega_m
    rho_crit = cosmo.rho_c(0.0)  # kg/m³
    rho_r_final = rho_r * rho_crit * omega_m

    return r, rho_r_final

def calculate_stacked_sim_profile(C200_array, delta_vir=200, n_points=24, max_halos=3000):
    """
    用模拟晕浓度分布构建堆叠曲线（图中 "median-c NFW"）。
    做法：逐晕计算 NFW 归一化密度，再在每个 r/R200 点取中位数。
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

    rho_crit = cosmo.rho_c(0.0)
    rho = rho_norm * rho_crit * omega_m
    rho_med = np.nanmedian(rho, axis=0)
    return x, rho_med

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
    - mean-c NFW:   使用每个质量 bin 的平均 C200/R200 计算单条 NFW 曲线。
    - median-c NFW: 使用该 bin 全部晕的 C200 逐晕计算后做中位数堆叠。
    """
    apply_journal_style(base_fontsize=11.2)
    n_panels = len(TARGET_MASSES)
    n_cols = min(PANEL_COLUMNS, n_panels)
    n_rows = int(np.ceil(n_panels / n_cols))
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(7.2, 2.45 * n_rows),
        sharex=True,
        sharey=True,
        squeeze=False,
    )

    colors = [JOURNAL_COLORS["black"], JOURNAL_COLORS["blue"], JOURNAL_COLORS["green"]]
    labels = ['PL', 'BT(soft)', 'BT(deep)']
    legend_handles = None
    legend_labels = None

    for i, target_mass in enumerate(TARGET_MASSES):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]
        panel_counts = []
        panel_npart = []
        panel_softening_marks = []

        # 计算NFW轮廓
        for j, (model_data, color, label) in enumerate(zip([cdm_data, bt_data, bt_kp10_data], colors, labels)):
            stats = find_mass_group(model_data['M200'], model_data['C200'], model_data['R200'], target_mass)

            if stats[0] is not None:
                c_mean, r_mean, _, num_halos, group_mask = stats
                panel_counts.append(num_halos)
                panel_npart.append(np.nanmedian(model_data['N200'][group_mask]))
                if np.isfinite(r_mean) and r_mean > 0:
                    panel_softening_marks.append(SOFTENING_KPC_Z0 / r_mean)
                r, rho = calculate_nfw_profile(c_mean, r_mean)
                mean_label = f"{label} mean-c NFW" if i == 0 else None
                ax.loglog(r / r_mean, rho, color=color, label=mean_label, linewidth=1.0)

                x_sim, rho_sim = calculate_stacked_sim_profile(model_data['C200'][group_mask])
                if x_sim is not None:
                    sim_label = f"{label} median-c NFW" if i == 0 else None
                    ax.loglog(
                        x_sim,
                        rho_sim,
                        color=color,
                        linestyle='none',
                        marker='o',
                        markersize=2.6,
                        markerfacecolor='white',
                        markeredgewidth=0.8,
                        alpha=0.9,
                        label=sim_label,
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
        ax.text(0.13, 0.02, title_text, transform=ax.transAxes,
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
                ax.axvline(softening_x, color='0.35', linestyle='--', linewidth=0.85, alpha=0.9)

        # 只在最下边显示x轴标题
        if row == n_rows - 1:
            ax.set_xlabel(r'$r/R_{200}$')
        else:
            ax.set_xlabel('')

        # 只在最左边显示y轴标题
        if col == 0:  # 第一列
            ax.set_ylabel(r'$\rho(r)\,[h^2\,M_\odot\,{\rm kpc}^{-3}]$')
        else:
            ax.set_ylabel('')

        format_axes(ax, grid=True)
        if i == 0:
            legend_handles, legend_labels = ax.get_legend_handles_labels()

    for j in range(n_panels, n_rows * n_cols):
        axes[j // n_cols, j % n_cols].set_visible(False)

    if legend_handles is not None:
        legend_handles = list(legend_handles)
        legend_labels = list(legend_labels)
        legend_handles.append(Line2D([0], [0], color='0.35', linestyle='--', linewidth=0.85))
        legend_labels.append(r'$\epsilon/R_{200}$ marker')
        fig.legend(
            legend_handles,
            legend_labels,
            loc='upper center',
            bbox_to_anchor=(0.5, 0.985),
            ncol=4,
            fontsize=6.8,
            frameon=True,
            framealpha=0.78,
            edgecolor='none',
            borderpad=0.18,
            labelspacing=0.10,
            handlelength=1.20,
            columnspacing=0.70,
            handletextpad=0.28,
        )

    fig.subplots_adjust(top=0.88, bottom=0.07, left=0.10, right=0.99, hspace=0.04, wspace=0.04)
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
