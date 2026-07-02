#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
非线性功率谱理论（halofit + BT-HMcode）与模拟数据对比（多快照版本）
- 对比 cdm_25、cdm_256 和 BT 三个模拟数据集
- 每个子图包含上、下两部分：
  上：功率谱对比（理论halofit谱 + BT-HMcode理论谱 + 三个模拟数据散点）
  下：模拟/理论比值（三条曲线，其中 BT 模拟/BT 理论单独显示）
- 标注红移及各自比值中位数
单位处理与原脚本完全一致。
"""

import numpy as np
import matplotlib.pyplot as plt
import pyccl as ccl
import matplotlib.gridspec as gridspec
import pyhmcode
import os
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
ANALYSIS_ROOT = next(
    (p for p in SCRIPT_PATH.parents if (p / "paperplot").exists() and (p / "powerspectrum").exists()),
    Path.cwd(),
)
STYLE_ROOT = next(
    (p for p in SCRIPT_PATH.parents if (p / "cosmology_plot_style.py").exists()),
    ANALYSIS_ROOT,
)
if str(STYLE_ROOT) not in sys.path:
    sys.path.insert(0, str(STYLE_ROOT))

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes, format_redshift, panel_label, save_publication_figure

# ================= 宇宙学参数 =================
Omega_c = 0.26458
Omega_b = 0.0493
h_val = 0.6736
n_s = 0.9649
sigma8 = 0.8111
Omega_m = Omega_c + Omega_b

# ================= 波数网格（理论计算用） =================
k_min = 1e-4
k_max = 1e3
n_k = 300
k_h = np.logspace(np.log10(k_min), np.log10(k_max), n_k)  # h/Mpc, for plotting and simulation comparison
k_ccl = k_h * h_val  # 1/Mpc, as expected by CCL
N_PLOT_BINS = 35
MESH_N = 1024
BOX_25_HMPC = 25.0
BOX_128_HMPC = 128.0
BOX_256_HMPC = 256.0
BOX_512_HMPC = 512.0
BOX_5_HMPC = 5.0
BOX_2P5_HMPC = 2.5
K_NY_25 = np.pi * MESH_N / BOX_25_HMPC
K_NY_128 = np.pi * MESH_N / BOX_128_HMPC
K_NY_256 = np.pi * MESH_N / BOX_256_HMPC
K_NY_512 = np.pi * MESH_N / BOX_512_HMPC
K_NY_5 = np.pi * MESH_N / BOX_5_HMPC
K_NY_2P5 = np.pi * MESH_N / BOX_2P5_HMPC
K_HIGHK_CAUTION_25 = 0.5 * K_NY_25

# ================= 模拟快照列表 =================
snap_list = ['0056', '0048', '0040', '0032']
SIM_POWER_DIR = ANALYSIS_ROOT / "powerspectrum" / "sim_power_data"
PAPERPLOT_ROOT = ANALYSIS_ROOT / "paperplot"
file_template_256 = str(SIM_POWER_DIR / "new_PL_256_1024_snap{}.npz")
file_template_pl_128 = str(SIM_POWER_DIR / "PL_128_1024_snap{}.npz")
file_template_pl_512 = str(SIM_POWER_DIR / "PL_512_1024_snap{}.npz")
file_template_25 = str(SIM_POWER_DIR / "cdm_25_snap{}.npz")
file_template_bt = str(SIM_POWER_DIR / "bluetilted_kp1_ms1.5_25_snap{}.npz")
file_template_bt_256 = str(SIM_POWER_DIR / "bluetilted_kp1_ms1.5_256_snap{}.npz")
file_template_bt_5 = str(SIM_POWER_DIR / "bluetilted_kp1_ms1.5_5_snap{}.npz")
file_template_bt_2p5 = str(SIM_POWER_DIR / "bluetilted_kp1_ms1.5_2p5_snap{}.npz")
PL512_SNAP_MAP = {
    '0056': '0005',
    '0048': '0004',
    '0040': '0003',
    '0032': '0002',
    '0024': '0001',
    '0016': '0000',
}

# ================= 创建CCL宇宙学对象（用于 halofit） =================
cosmo_ccl = ccl.Cosmology(
    Omega_c=Omega_c,
    Omega_b=Omega_b,
    h=h_val,
    n_s=n_s,
    sigma8=sigma8,
    matter_power_spectrum='halofit',
    transfer_function='eisenstein_hu'
)

try:
    nl_power = ccl.nonlinear_matter_power
except AttributeError:
    nl_power = ccl.nonlin_matter_power

def compute_theory_halofit(z, k_h_array):
    """halofit 理论谱，返回 (Mpc/h)^3"""
    a = 1.0 / (1.0 + z)
    P_Mpc3 = nl_power(cosmo_ccl, k_h_array * h_val, a)
    return P_Mpc3 * (h_val ** 3)

# ================= 计算 BT 理论谱（HMcode + 倾斜修正） =================
# 获取所有模拟红移（从 BT 数据文件中读取，避免重复）
z_sim_list = []
for snap in snap_list:
    fname = file_template_bt.format(snap)
    with np.load(fname) as data:
        z_sim_list.append(float(data['z']))
z_targets = sorted(set(z_sim_list))

# 红移网格（覆盖所有目标红移，并稍微外扩）
z_min = min(z_targets) * 0.9 if min(z_targets) > 0 else 0.0
z_max = max(z_targets) * 1.1
z_grid = np.linspace(z_min, z_max, max(50, len(z_targets)*10))
z_all = np.sort(np.unique(np.concatenate([z_grid, z_targets])))
# print(z_all)
print("计算 BT 理论谱（HMcode + 倾斜修正）...")
print(f"红移网格点数: {len(z_all)}, 范围 [{format_redshift(z_all[0], 2)}, {format_redshift(z_all[-1], 2)}]")

# 线性功率谱（标准 CDM）
a_arr = 1 / (1 + z_all)
pofk_lin_CDM = np.array([ccl.linear_matter_power(cosmo_ccl, k=k_ccl, a=a_) for a_ in a_arr])
pofk_lin_CDM *= (h_val ** 3)   # 转换为 (Mpc/h)^3

# 构造 BT 修正的线性谱
kp_bt = 1        # h/Mpc
ms_bt = 1.5
ns_bt = n_s        # 使用原初谱指数
pofk_lin_BT = pofk_lin_CDM.copy()
for i in range(pofk_lin_BT.shape[0]):
    mask = k_h > kp_bt
    pofk_lin_BT[i, mask] = pofk_lin_BT[i, mask] * (kp_bt**(ns_bt - ms_bt)) * (k_h[mask]**(ms_bt - ns_bt))

# 设置 HMcode 宇宙学对象（CDM 版本）
hmc_cdm = pyhmcode.Cosmology()
hmc_cdm.omega_m = Omega_m
hmc_cdm.omega_b = Omega_b
hmc_cdm.h = h_val
hmc_cdm.n_s = n_s
hmc_cdm.sigma8 = sigma8
hmc_cdm.log10_T_heat = 0          # 无喷流加热
hmc_cdm.log10_M_min = 7.0
hmc_cdm.nu_min = 0.02
hmc_cdm.set_linear_power_spectrum(k_h, z_all, pofk_lin_CDM)

hmcode_model = pyhmcode.Halomodel(pyhmcode.HMcode2020)
print("计算 HMcode (CDM) 非线性谱（备用）...")
pofk_nl_CDM = pyhmcode.calculate_nonlinear_power_spectrum(
    cosmology=hmc_cdm,
    halomodel=hmcode_model,
    fields=[pyhmcode.field_dmonly]
)

# 设置 BT 宇宙学对象（使用修正后的线性谱）
hmc_bt = pyhmcode.Cosmology()
hmc_bt.omega_m = Omega_m
hmc_bt.omega_b = Omega_b
hmc_bt.h = h_val
hmc_bt.n_s = n_s
hmc_bt.sigma8 = sigma8
hmc_bt.log10_T_heat = 0        # 典型 BT 加热参数
hmc_bt.log10_M_min = 6.0
hmc_bt.nu_min = 0.02
hmc_bt.set_linear_power_spectrum(k_h, z_all, pofk_lin_BT)

print("计算 BT 模型非线性谱（HMcode + tilt）...")
pofk_nl_BT = pyhmcode.calculate_nonlinear_power_spectrum(
    cosmology=hmc_bt,
    halomodel=hmcode_model,
    fields=[pyhmcode.field_dmonly]
)  # 形状 (n_z, n_k)

# 插值函数：给定红移 z，返回 BT 理论谱在 k_h 上的值
from scipy.interpolate import interp1d
logP_bt_grid = np.log10(pofk_nl_BT)   # (n_z, n_k)
interp_bt = interp1d(z_all, logP_bt_grid, axis=0, kind='linear', fill_value='extrapolate')
logP_pl_grid = np.log10(pofk_nl_CDM)   # (n_z, n_k)
interp_pl = interp1d(z_all, logP_pl_grid, axis=0, kind='linear', fill_value='extrapolate')

def compute_theory_bt(z, k_h_array):
    """返回 BT 理论谱在红移 z 和波数 k_h (h/Mpc) 处的值，单位 (Mpc/h)^3"""
    logP_interp = interp_bt(z)   # 形状 (n_k,)
    # 由于 interp1d 对每个 k 返回一维数组，需要对 k_h_array 插值
    # 更简单：直接使用预计算的网格插值到任意 k_h
    # 这里使用全局 k_h 网格，然后对每个目标 k 线性插值
    logP_at_z = np.interp(np.log10(k_h_array), np.log10(k_h), logP_interp)
    return 10**logP_at_z
def compute_theory_pl(z, k_h_array):
    """返回 PL 理论谱在红移 z 和波数 k_h (h/Mpc) 处的值，单位 (Mpc/h)^3"""
    logP_interp = interp_pl(z)   # 形状 (n_k,)
    # 由于 interp1d 对每个 k 返回一维数组，需要对 k_h_array 插值
    # 更简单：直接使用预计算的网格插值到任意 k_h
    # 这里使用全局 k_h 网格，然后对每个目标 k 线性插值
    logP_at_z = np.interp(np.log10(k_h_array), np.log10(k_h), logP_interp)
    return 10**logP_at_z

# ================= 加载模拟数据函数 =================
def load_simulation_data(file_template, snap):
    fname = file_template.format(snap)
    data = np.load(fname)
    k_sim = data['k']          # h/Mpc
    P_sim = data['P']          # (Mpc/h)^3
    z_sim = float(data['z'])
    return k_sim, P_sim, z_sim

def load_optional_simulation_data(file_template, snap):
    fname = file_template.format(snap)
    if not os.path.exists(fname):
        return None
    return load_simulation_data(file_template, snap)

def log_bin_for_plot(k, y, n_bins=N_PLOT_BINS):
    """Down-sample simulation points in log-k bins for clearer plotting."""
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


def mark_power_reliability(ax_top, ax_bottom, annotate=False):
    """Mark mesh Nyquist scales and a ratio tolerance band."""
    for ax in (ax_top, ax_bottom):
        ax.axvspan(K_NY_25, 1.0e3, color="0.82", alpha=0.18, lw=0, zorder=0)
        ax.axvspan(K_HIGHK_CAUTION_25, K_NY_25, color="0.75", alpha=0.08, lw=0, zorder=0)
        ax.axvline(K_NY_256, color="0.35", linestyle=":", linewidth=0.85, alpha=0.9, zorder=1)
        ax.axvline(K_NY_128, color="0.45", linestyle=":", linewidth=0.75, alpha=0.75, zorder=1)
        ax.axvline(K_NY_512, color="0.55", linestyle=":", linewidth=0.7, alpha=0.7, zorder=1)
        ax.axvline(K_NY_5, color="0.62", linestyle=":", linewidth=0.7, alpha=0.6, zorder=1)
        ax.axvline(K_NY_2P5, color="0.68", linestyle=":", linewidth=0.7, alpha=0.55, zorder=1)
        ax.axvline(K_NY_25, color="0.25", linestyle="--", linewidth=0.85, alpha=0.9, zorder=1)
    ax_bottom.axhspan(0.9, 1.1, color="0.45", alpha=0.10, lw=0, zorder=0)
    if annotate:
        ax_top.text(
            0.965,
            0.74,
            r"dotted/dashed: $k_{\rm Ny}$" + "\n" + r"gray: high-$k$ caution",
            transform=ax_top.transAxes,
            ha="right",
            va="top",
            fontsize=7.2,
            color="0.25",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 0.9},
        )


# ================= 绘图 =================
apply_journal_style(base_fontsize=11.2)

fig = plt.figure(figsize=(8.6, 5.8))
outer_grid = gridspec.GridSpec(
    2,
    2,
    figure=fig,
    left=0.075,
    right=0.99,
    bottom=0.08,
    top=0.90,
    hspace=0.07,
    wspace=0.06,
)

for idx, snap in enumerate(snap_list):
    # 加载模拟数据
    k_sim_256, P_sim_256, z_simpl256 = load_simulation_data(file_template_256, snap)
    k_sim_25,  P_sim_25,  z_simpl25 = load_simulation_data(file_template_25, snap)
    k_sim_bt,  P_sim_bt,  z_simbt25 = load_simulation_data(file_template_bt, snap)
    pl_128_data = load_optional_simulation_data(file_template_pl_128, snap)
    pl_512_label = PL512_SNAP_MAP.get(snap)
    pl_512_data = (
        load_optional_simulation_data(file_template_pl_512, pl_512_label)
        if pl_512_label is not None
        else None
    )
    bt_256_data = load_optional_simulation_data(file_template_bt_256, snap)
    bt_5_data = load_optional_simulation_data(file_template_bt_5, snap)
    bt_2p5_data = load_optional_simulation_data(file_template_bt_2p5, snap)
    if abs(z_simpl256 - z_simpl25) > 1e-5 or abs(z_simpl256 - z_simbt25) > 1e-5:
        print(
            f"Warning: redshift mismatch for snap {snap}: "
            f"{z_simpl256}, {z_simpl25}, {z_simbt25}"
        )
    

    P_bt_theory_full = compute_theory_bt(z_simbt25, k_h)
    P_pl_theory_25 = compute_theory_pl(z_simpl25, k_h)
    P_pl_theory_256 = compute_theory_pl(z_simpl256, k_h)



    P_theory_at_256 = 10**np.interp(np.log10(k_sim_256),  np.log10(k_h), np.log10(P_pl_theory_256))
    ratio_256 = P_sim_256 / P_theory_at_256
    
    P_theory_at_25 = 10**np.interp(np.log10(k_sim_25),  np.log10(k_h), np.log10(P_pl_theory_25))
    ratio_25 = P_sim_25 / P_theory_at_25
    
    
    # BT 模拟相对于 BT 理论（HMcode+tilt）的比值
    P_bt_theory_at_bt = 10**np.interp(np.log10(k_sim_bt), np.log10(k_h),np.log10(P_bt_theory_full))
    ratio_bt_vs_bttheory = P_sim_bt / P_bt_theory_at_bt

    k_plot_256, P_plot_256 = log_bin_for_plot(k_sim_256, P_sim_256)
    k_plot_25, P_plot_25 = log_bin_for_plot(k_sim_25, P_sim_25)
    k_plot_bt, P_plot_bt = log_bin_for_plot(k_sim_bt, P_sim_bt)
    k_ratio_256, ratio_plot_256 = log_bin_for_plot(k_sim_256, ratio_256)
    k_ratio_25, ratio_plot_25 = log_bin_for_plot(k_sim_25, ratio_25)
    k_ratio_bt, ratio_plot_bt = log_bin_for_plot(k_sim_bt, ratio_bt_vs_bttheory)

    pl_128_plot = None
    if pl_128_data is not None:
        k_sim_pl_128, P_sim_pl_128, z_simpl128 = pl_128_data
        if abs(z_simpl128 - z_simpl25) > 1e-5:
            print(
                f"Warning: redshift mismatch for snap {snap} PL 128: "
                f"{z_simpl128}, reference {z_simpl25}"
            )
        P_pl_theory_at_128 = 10**np.interp(
            np.log10(k_sim_pl_128),
            np.log10(k_h),
            np.log10(P_pl_theory_25),
        )
        ratio_pl_128 = P_sim_pl_128 / P_pl_theory_at_128
        k_plot_pl_128, P_plot_pl_128 = log_bin_for_plot(k_sim_pl_128, P_sim_pl_128)
        k_ratio_pl_128, ratio_plot_pl_128 = log_bin_for_plot(k_sim_pl_128, ratio_pl_128)
        pl_128_plot = (k_plot_pl_128, P_plot_pl_128, k_ratio_pl_128, ratio_plot_pl_128)

    pl_512_plot = None
    if pl_512_data is not None:
        k_sim_pl_512, P_sim_pl_512, z_simpl512 = pl_512_data
        if abs(z_simpl512 - z_simpl25) > 1e-5:
            print(
                f"Warning: redshift mismatch for snap {snap} PL 512: "
                f"{z_simpl512}, reference {z_simpl25}"
            )
        P_pl_theory_at_512 = 10**np.interp(
            np.log10(k_sim_pl_512),
            np.log10(k_h),
            np.log10(P_pl_theory_25),
        )
        ratio_pl_512 = P_sim_pl_512 / P_pl_theory_at_512
        k_plot_pl_512, P_plot_pl_512 = log_bin_for_plot(k_sim_pl_512, P_sim_pl_512)
        k_ratio_pl_512, ratio_plot_pl_512 = log_bin_for_plot(k_sim_pl_512, ratio_pl_512)
        pl_512_plot = (k_plot_pl_512, P_plot_pl_512, k_ratio_pl_512, ratio_plot_pl_512)

    bt_256_plot = None
    if bt_256_data is not None:
        k_sim_bt_256, P_sim_bt_256, z_simbt256 = bt_256_data
        P_bt_theory_at_bt_256 = 10**np.interp(
            np.log10(k_sim_bt_256),
            np.log10(k_h),
            np.log10(P_bt_theory_full),
        )
        ratio_bt_256_vs_bttheory = P_sim_bt_256 / P_bt_theory_at_bt_256
        k_plot_bt_256, P_plot_bt_256 = log_bin_for_plot(k_sim_bt_256, P_sim_bt_256)
        k_ratio_bt_256, ratio_plot_bt_256 = log_bin_for_plot(k_sim_bt_256, ratio_bt_256_vs_bttheory)
        bt_256_plot = (k_plot_bt_256, P_plot_bt_256, k_ratio_bt_256, ratio_plot_bt_256)

    bt_5_plot = None
    if bt_5_data is not None:
        k_sim_bt_5, P_sim_bt_5, z_simbt5 = bt_5_data
        if abs(z_simbt5 - z_simbt25) > 1e-5:
            print(
                f"Warning: redshift mismatch for snap {snap} BTKP1 5: "
                f"{z_simbt5}, reference {z_simbt25}"
            )
        P_bt_theory_at_bt_5 = 10**np.interp(
            np.log10(k_sim_bt_5),
            np.log10(k_h),
            np.log10(P_bt_theory_full),
        )
        ratio_bt_5_vs_bttheory = P_sim_bt_5 / P_bt_theory_at_bt_5
        k_plot_bt_5, P_plot_bt_5 = log_bin_for_plot(k_sim_bt_5, P_sim_bt_5)
        k_ratio_bt_5, ratio_plot_bt_5 = log_bin_for_plot(k_sim_bt_5, ratio_bt_5_vs_bttheory)
        bt_5_plot = (k_plot_bt_5, P_plot_bt_5, k_ratio_bt_5, ratio_plot_bt_5)

    bt_2p5_plot = None
    if bt_2p5_data is not None:
        k_sim_bt_2p5, P_sim_bt_2p5, z_simbt2p5 = bt_2p5_data
        if abs(z_simbt2p5 - z_simbt25) > 1e-5:
            print(
                f"Warning: redshift mismatch for snap {snap} BTKP1 2.5: "
                f"{z_simbt2p5}, reference {z_simbt25}"
            )
        P_bt_theory_at_bt_2p5 = 10**np.interp(
            np.log10(k_sim_bt_2p5),
            np.log10(k_h),
            np.log10(P_bt_theory_full),
        )
        ratio_bt_2p5_vs_bttheory = P_sim_bt_2p5 / P_bt_theory_at_bt_2p5
        k_plot_bt_2p5, P_plot_bt_2p5 = log_bin_for_plot(k_sim_bt_2p5, P_sim_bt_2p5)
        k_ratio_bt_2p5, ratio_plot_bt_2p5 = log_bin_for_plot(k_sim_bt_2p5, ratio_bt_2p5_vs_bttheory)
        bt_2p5_plot = (k_plot_bt_2p5, P_plot_bt_2p5, k_ratio_bt_2p5, ratio_plot_bt_2p5)
    
    
    # 创建内部子图
    inner_gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer_grid[idx],
                                                 height_ratios=[3, 1], hspace=0.05)
    ax_top = fig.add_subplot(inner_gs[0])
    ax_bottom = fig.add_subplot(inner_gs[1], sharex=ax_top)
    outer_row = idx // 2
    outer_col = idx % 2
    
    # ---- 上子图：功率谱 ----
    ax_top.loglog(k_h, P_pl_theory_25, '-', color=JOURNAL_COLORS["black"], lw=1.35, label='PL theory')
    ax_top.loglog(k_h, P_bt_theory_full, '--', color=JOURNAL_COLORS["blue"], lw=1.35, label='BTKP1 theory')
    # 修改：空心小标记
    ax_top.loglog(k_plot_256, P_plot_256, 'o', color=JOURNAL_COLORS["black"], ms=3.2, alpha=0.85,
                  markerfacecolor='none', markeredgewidth=0.7, label='PL 256')
    ax_top.loglog(k_plot_25,  P_plot_25,  's', color=JOURNAL_COLORS["gray"], ms=3.2, alpha=0.85,
                  markerfacecolor='none', markeredgewidth=0.7, label='PL 25')
    if pl_512_plot is not None:
        ax_top.loglog(
            pl_512_plot[0],
            pl_512_plot[1],
            'P',
            color=JOURNAL_COLORS["orange"],
            ms=3.0,
            alpha=0.9,
            markerfacecolor='none',
            markeredgewidth=0.75,
            label='PL 512',
        )
    if pl_128_plot is not None:
        ax_top.loglog(
            pl_128_plot[0],
            pl_128_plot[1],
            'v',
            color=JOURNAL_COLORS["gray"],
            ms=3.0,
            alpha=0.85,
            markerfacecolor='none',
            markeredgewidth=0.7,
            label='PL 128',
        )
    ax_top.loglog(k_plot_bt,  P_plot_bt,  '^', color=JOURNAL_COLORS["blue"], ms=3.2, alpha=0.85,
                  markerfacecolor='none', markeredgewidth=0.7, label='BTKP1 25')
    if bt_256_plot is not None:
        ax_top.loglog(
            bt_256_plot[0],
            bt_256_plot[1],
            'x',
            color=JOURNAL_COLORS["blue"],
            ms=3.2,
            alpha=0.9,
            markeredgewidth=0.7,
            label='BTKP1 256',
        )
    if bt_5_plot is not None:
        ax_top.loglog(
            bt_5_plot[0],
            bt_5_plot[1],
            'd',
            color=JOURNAL_COLORS["purple"],
            ms=2.8,
            alpha=0.9,
            markerfacecolor='none',
            markeredgewidth=0.7,
            label='BTKP1 5',
        )
    if bt_2p5_plot is not None:
        ax_top.loglog(
            bt_2p5_plot[0],
            bt_2p5_plot[1],
            'p',
            color=JOURNAL_COLORS["green"],
            ms=3.0,
            alpha=0.9,
            markerfacecolor='none',
            markeredgewidth=0.7,
            label='BTKP1 2.5',
        )
    if outer_col == 0:
        ax_top.set_ylabel(r'$P(k)\,[(\mathrm{Mpc}/h)^3]$')
    else:
        ax_top.tick_params(labelleft=False)
    ax_top.set_ylim(1e-5, 1e5)
    ax_top.set_xlim(1e-2, 1e3)
    format_axes(ax_top)
    if idx == 0:
        ax_top.legend(
            loc='lower left',
            ncol=2,
            frameon=True,
            framealpha=0.72,
            edgecolor='none',
            fontsize=7.8,
            borderpad=0.25,
            labelspacing=0.18,
            handlelength=1.2,
            handletextpad=0.35,
        )
    panel_label(ax_top, rf'$z={format_redshift(z_simpl25, 3)}$', loc=(0.72, 0.92), fontsize=11.0)
    
    # ---- 下子图：比值 ----
    # 修改：空心小标记
    ax_bottom.semilogx(k_ratio_256, ratio_plot_256, 'o', color=JOURNAL_COLORS["black"], ms=3.2, alpha=0.85,
                       markerfacecolor='none', markeredgewidth=0.7,
                       label='PL 256 / theory')
    ax_bottom.semilogx(k_ratio_25,  ratio_plot_25,  's', color=JOURNAL_COLORS["gray"], ms=3.2, alpha=0.85,
                       markerfacecolor='none', markeredgewidth=0.7,
                       label='PL 25 / theory')
    if pl_512_plot is not None:
        ax_bottom.semilogx(
            pl_512_plot[2],
            pl_512_plot[3],
            'P',
            color=JOURNAL_COLORS["orange"],
            ms=3.0,
            alpha=0.9,
            markerfacecolor='none',
            markeredgewidth=0.75,
            label='PL 512 / theory',
        )
    if pl_128_plot is not None:
        ax_bottom.semilogx(
            pl_128_plot[2],
            pl_128_plot[3],
            'v',
            color=JOURNAL_COLORS["gray"],
            ms=3.0,
            alpha=0.85,
            markerfacecolor='none',
            markeredgewidth=0.7,
            label='PL 128 / theory',
        )
    ax_bottom.semilogx(k_ratio_bt,  ratio_plot_bt,  '^', color=JOURNAL_COLORS["blue"], ms=3.2, alpha=0.85,
                       markerfacecolor='none', markeredgewidth=0.7,
                       label='BTKP1 25 / theory')
    if bt_256_plot is not None:
        ax_bottom.semilogx(
            bt_256_plot[2],
            bt_256_plot[3],
            'x',
            color=JOURNAL_COLORS["blue"],
            ms=3.2,
            alpha=0.9,
            markeredgewidth=0.7,
            label='BTKP1 256 / theory',
        )
    if bt_5_plot is not None:
        ax_bottom.semilogx(
            bt_5_plot[2],
            bt_5_plot[3],
            'd',
            color=JOURNAL_COLORS["purple"],
            ms=2.8,
            alpha=0.9,
            markerfacecolor='none',
            markeredgewidth=0.7,
            label='BTKP1 5 / theory',
        )
    if bt_2p5_plot is not None:
        ax_bottom.semilogx(
            bt_2p5_plot[2],
            bt_2p5_plot[3],
            'p',
            color=JOURNAL_COLORS["green"],
            ms=3.0,
            alpha=0.9,
            markerfacecolor='none',
            markeredgewidth=0.7,
            label='BTKP1 2.5 / theory',
        )
    ax_bottom.axhline(y=1, color='0.45', linestyle='--', linewidth=0.7, alpha=0.8)
    mark_power_reliability(ax_top, ax_bottom, annotate=(idx == 0))
    if outer_col == 0:
        ax_bottom.set_ylabel('Ratio', labelpad=1.5)
    else:
        ax_bottom.tick_params(labelleft=False)
    if outer_row == 1:
        ax_bottom.set_xlabel(r'$k\,[h\,\mathrm{Mpc}^{-1}]$')
    else:
        ax_bottom.set_xlabel('')
        ax_bottom.tick_params(labelbottom=False)
    ax_bottom.set_ylim(0, 1.5)
    format_axes(ax_bottom)
    # ax_bottom.legend(loc='upper right', fontsize=6, ncol=2)
    plt.setp(ax_top.get_xticklabels(), visible=False)

save_publication_figure(fig, PAPERPLOT_ROOT / "figures" / "power-spectrum.png")
