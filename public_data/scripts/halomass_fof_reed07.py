import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import h5py
from pathlib import Path
from matplotlib.legend_handler import HandlerTuple
from matplotlib.ticker import FixedLocator, FuncFormatter, LogFormatterMathtext, LogLocator, NullFormatter
from scipy.interpolate import interp1d
import matplotlib.gridspec as gridspec

SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ANALYSIS_ROOT = SCRIPT_DIR.parent


def find_project_root(script_dir):
    for parent in script_dir.parents:
        if (parent / "data").exists() and (parent / "software" / "colossus").exists():
            return parent
    return script_dir.parents[2]


PROJECT_ROOT = find_project_root(SCRIPT_DIR)
WORKSPACE_ROOT = PROJECT_ROOT
CACHE_DIR = SCRIPT_DIR / "output" / "fof_reed07_highz_cache"
COLOSSUS_ROOT = PROJECT_ROOT / "software" / "colossus"


def colossus_has_project_models():
    try:
        from colossus.cosmology import power_spectrum as colossus_power_spectrum
    except Exception:
        return False
    required = {"eisenstein98_pl", "eisenstein98_bt", "eisenstein98_bt_soft"}
    return required.issubset(colossus_power_spectrum.models)


if not colossus_has_project_models() and COLOSSUS_ROOT.exists() and str(COLOSSUS_ROOT) not in sys.path:
    sys.path.insert(0, str(COLOSSUS_ROOT))
STYLE_CANDIDATES = list(Path(__file__).resolve().parents) + [
    PROJECT_ROOT / "papers" / "article_nonlinear_evolution_pps" / "public_data" / "scripts"
]
STYLE_ROOT = next(
    (p for p in STYLE_CANDIDATES if (p / "cosmology_plot_style.py").exists()),
    WORKSPACE_ROOT,
)
if str(STYLE_ROOT) not in sys.path:
    sys.path.insert(0, str(STYLE_ROOT))

from cosmology_plot_style import JOURNAL_COLORS, apply_journal_style, format_axes, format_redshift, panel_label, save_publication_figure
from colossus.cosmology import cosmology
from colossus.lss import mass_function

# z=0 and z=3.44 plus high-z snapshots nearest to z ~= 8.5, 10, 15, and 20.
snap_numbers = [56, 40, 32, 30, 27, 24]
PANEL_COLUMNS = 3

# 功率谱文件路径 - 更新为包含3个模型
DATA_ROOT = PROJECT_ROOT / "data"
PAPERPLOT_ROOT = ARTICLE_ANALYSIS_ROOT / "paperplot"

base_paths = {
    'BT_soft': {
        'snapshot_base': str(DATA_ROOT / "bluetilted/kp_1_ms_1.5_25_1024/kp_1_ms_1.5_25_1024_{:04d}.hdf5"),
        'fof_base': str(DATA_ROOT / "bluetilted/kp_1_ms_1.5_25_1024/fof_output_{:04d}.hdf5")
    },
    'PL': {
        'snapshot_base': str(DATA_ROOT / "PL/PL_25_1024/PL_25_1024_{:04d}.hdf5"),
        'fof_base': str(DATA_ROOT / "PL/PL_25_1024/fof_output_{:04d}.hdf5")
    },
    'BT_deep': {
        'snapshot_base': str(DATA_ROOT / "bluetilted/kp_10_ms_1.5_25_1024/kp_10_ms_1.5_25_1024_{:04d}.hdf5"),
        'fof_base': str(DATA_ROOT / "bluetilted/kp_10_ms_1.5_25_1024/fof_output_{:04d}.hdf5")
    }
}

sim_configs = {
    'PL': {'name': 'PL', 'color': JOURNAL_COLORS["black"], 'marker': 'o', 'linestyle': '-', 'markerfacecolor': 'white'},
    'BT_soft': {'name': r'BT $k_p=1$', 'color': JOURNAL_COLORS["blue"], 'marker': '^', 'linestyle': '--', 'markerfacecolor': 'white'},
    'BT_deep': {'name': r'BT $k_p=10$', 'color': JOURNAL_COLORS["green"], 'marker': 's', 'linestyle': '-.', 'markerfacecolor': 'white'}
}

cosmo_params = {
    'omega_m': 0.3153, 'om_lam': 0.68462, 'sig_8_z0': 0.8111,
    'h': 0.6736, 'Ob0': 0.0493, 'ns': 0.9649
}

MAIN_PARTICLE_MASS_MSUN = 1.89e6
HMF_N20_MASS_MSUN = 20.0 * MAIN_PARTICLE_MASS_MSUN
HMF_CATALOG_CUT_MSUN = 1.0e8
HMF_XMIN_MSUN = 5.0e7
HMF_BINS_PER_DEX = 6
HMF_X_MAJOR_TICKS = 10.0 ** np.arange(8, 12)
HMF_RATIO_TICK_POOL = np.array([0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0])


def hmf_log_edges(bins_per_dex=HMF_BINS_PER_DEX):
    return np.arange(8.0, 13.0 + 1.0 / bins_per_dex, 1.0 / bins_per_dex)


def plain_ratio_tick_label(value, _pos):
    return f"{value:g}"


def set_hmf_log_ticks(ax, *, y_decades=None, ratio_axis=False):
    ax.xaxis.set_major_locator(FixedLocator(HMF_X_MAJOR_TICKS))
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.xaxis.set_minor_formatter(NullFormatter())

    if y_decades is not None:
        y_ticks = 10.0 ** np.arange(y_decades[0], y_decades[1] + 1)
        ax.yaxis.set_major_locator(FixedLocator(y_ticks))
        ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
    elif ratio_axis:
        ymin, ymax = ax.get_ylim()
        if ymax / ymin > 30:
            y_ticks = 10.0 ** np.arange(np.floor(np.log10(ymin)), np.ceil(np.log10(ymax)) + 1)
            y_ticks = y_ticks[(y_ticks >= ymin) & (y_ticks <= ymax)]
        else:
            y_ticks = HMF_RATIO_TICK_POOL[(HMF_RATIO_TICK_POOL >= ymin) & (HMF_RATIO_TICK_POOL <= ymax)]
        if len(y_ticks) >= 2:
            ax.yaxis.set_major_locator(FixedLocator(y_ticks))
            ax.yaxis.set_major_formatter(FuncFormatter(plain_ratio_tick_label))

    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=100))
    ax.yaxis.set_minor_formatter(NullFormatter())


def mark_hmf_resolution(ax, annotate=False):
    """Mark the particle-count range that brackets the catalog mass cut."""
    ax.axvspan(
        HMF_N20_MASS_MSUN,
        HMF_CATALOG_CUT_MSUN,
        color="0.82",
        alpha=0.22,
        lw=0,
        zorder=0,
    )
    ax.axvline(
        HMF_CATALOG_CUT_MSUN,
        color="0.35",
        linestyle="--",
        linewidth=0.85,
        alpha=0.9,
        zorder=1,
    )
    if annotate:
        ax.text(
            0.045,
            0.80,
            r"$20$--$50$ p.",
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=7.0,
            color="0.35",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 0.8},
        )


def correct_mass(m, Mp):
    """Warren-like correction: m_corrected = m * (1 - (m/Mp)^-0.6)."""
    return m - m * (m / Mp)**(-0.6)

# 辅助函数
def calculate_hmf(M, boxsize, particle_mass, bins_per_dex=6):
    if len(M) == 0:
        return None, None, None, None

    M = correct_mass(M, particle_mass)
    M = M[np.isfinite(M) & (M > 0)]
    if len(M) == 0:
        return None, None, None, None

    logM_edges = np.linspace(np.log10(M.min()), np.log10(M.max()),
                            int(bins_per_dex * (np.log10(M.max()) - np.log10(M.min()))) + 1)

    # 使用积分平均法计算
    logM = np.log10(M)
    n_bins = len(logM_edges) - 1

    # 初始化数组
    hmf = np.zeros(n_bins)
    hmf_err = np.zeros(n_bins)
    logM_centers = np.zeros(n_bins)
    dN = np.zeros(n_bins)

    volume = boxsize**3

    # 对每个区间计算积分
    for i in range(n_bins):
        # 找出在区间内的晕
        mask = (logM >= logM_edges[i]) & (logM < logM_edges[i+1])

        # 计算 ∫dn (区间内的晕数量)
        dn_sum = np.sum(mask)
        dN[i] = dn_sum

        # 计算 ∫M dn (质量加权和)
        if dn_sum > 0:
            M_dn_sum = np.sum(M[mask])

            # 计算 F̄ = (∫dn) / (ΔlogM)
            dlogM = logM_edges[i+1] - logM_edges[i]
            hmf[i] = dn_sum / (volume * dlogM)

            # 计算 M̄ = (∫M dn) / (∫dn)
            M_bar = M_dn_sum / dn_sum
            logM_centers[i] = np.log10(M_bar)
        else:
            hmf[i] = 0
            logM_centers[i] = (logM_edges[i+1] + logM_edges[i]) / 2

        # 计算误差
        hmf_err[i] = np.sqrt(dN[i]) / (volume * (logM_edges[i+1] - logM_edges[i]))

    return hmf, hmf_err, logM_centers, logM_edges

def load_snapshot_metadata(snapshot_file):
    """Read only the small metadata needed for the mass-function plot."""
    with h5py.File(snapshot_file, "r") as f:
        header = f["Header"].attrs
        cosmo_attrs = f["Cosmology"].attrs if "Cosmology" in f else {}
        redshift = float(np.asarray(header.get("Redshift", cosmo_attrs.get("Redshift", 0.0))).flat[0])
        box_size_mpc = float(np.asarray(header["BoxSize"]).flat[0])
        initial_mass_table = np.asarray(header["InitialMassTable"])
        particle_mass = float(initial_mass_table[1]) * 1e10
    return redshift, box_size_mpc, particle_mass


def open_fof_mass_dataset(fof_file):
    f = h5py.File(fof_file, "r")
    dataset_key = None
    for key in f.keys():
        if 'Group' in key or 'FOF' in key:
            dataset_key = key
            break
    if dataset_key is None:
        dataset_key = list(f.keys())[2] if len(f.keys()) > 2 else list(f.keys())[0]
    for mass_key in ['Masses', 'Mass', 'M200', 'M200m', 'M200c']:
        if mass_key in f[dataset_key]:
            return f, f[dataset_key][mass_key]
    f.close()
    return None, None


def calculate_hmf_from_fof(fof_file, boxsize, particle_mass, bins_per_dex=6, chunk_size=500_000, progress_label=None):
    """Stream the FOF mass dataset to avoid loading tens of millions of halos."""
    h5_file, mass_ds = open_fof_mass_dataset(fof_file)
    if mass_ds is None:
        return None, None, None, None

    logM_edges = hmf_log_edges(bins_per_dex)
    counts = np.zeros(len(logM_edges) - 1, dtype=np.float64)
    mass_sum = np.zeros_like(counts)

    try:
        n_mass = len(mass_ds)
        for start in range(0, n_mass, chunk_size):
            if progress_label and start and start % (5_000_000) == 0:
                print(f"{progress_label}: processed {start}/{n_mass} masses", flush=True)
            raw = np.asarray(mass_ds[start:start + chunk_size], dtype=np.float64) * 1e10
            mass = correct_mass(raw, particle_mass)
            valid = np.isfinite(mass) & (mass >= 1e8) & (mass <= 1e13)
            if not np.any(valid):
                continue
            mass = mass[valid]
            log_mass = np.log10(mass)
            counts += np.histogram(log_mass, bins=logM_edges)[0]
            mass_sum += np.histogram(log_mass, bins=logM_edges, weights=mass)[0]
    finally:
        h5_file.close()

    volume = boxsize ** 3
    dlogM = np.diff(logM_edges)
    hmf = counts / (volume * dlogM)
    hmf_err = np.sqrt(counts) / (volume * dlogM)
    logM_centers = 0.5 * (logM_edges[:-1] + logM_edges[1:])
    nonzero = counts > 0
    logM_centers[nonzero] = np.log10(mass_sum[nonzero] / counts[nonzero])
    return hmf, hmf_err, logM_centers, logM_edges

# 主处理逻辑
sim_results = {code: {} for code in sim_configs.keys()}
theory_results = {code: {} for code in sim_configs.keys()}
colors = plt.cm.viridis(np.linspace(0, 1, len(snap_numbers)))

# 设置宇宙学参数
cosmology.setCosmology('my_cosmo_reed07_without_nu_corrected', {
    'flat': True, 'H0': 100 * cosmo_params['h'], 'Om0': cosmo_params['omega_m'],
    'Ob0': cosmo_params['Ob0'], 'sigma8': cosmo_params['sig_8_z0'], 'ns': cosmo_params['ns'], 'relspecies': False
})

for idx, snap_num in enumerate(snap_numbers):
    for code in sim_configs.keys():
        snapshot_file = base_paths[code]['snapshot_base'].format(snap_num)
        fof_file = base_paths[code]['fof_base'].format(snap_num)

        if not all(os.path.exists(f) for f in [snapshot_file, fof_file]):
            print(f"文件不存在: {code} snap {snap_num}")
            continue

        try:
            cache_file = CACHE_DIR / f"{code}_snap{snap_num:04d}_fof_reed07_input.npz"
            if cache_file.exists():
                cached = np.load(cache_file)
                sim_redshift = float(cached['redshift'])
                hmf = cached['hmf']
                hmf_err = cached['hmf_err']
                logM_centers = cached['logM_centers']
                print(f"{snap_num:04d} {code}: loaded cached FoF HMF", flush=True)
            else:
                print(f"{snap_num:04d} {code}: reading FoF catalog", flush=True)
                sim_redshift, box_size_mpc, particle_mass = load_snapshot_metadata(snapshot_file)
                hmf, hmf_err, logM_centers, _ = calculate_hmf_from_fof(
                    fof_file, box_size_mpc, particle_mass, 6, progress_label=f"{snap_num:04d} {code}"
                )
            if hmf is None:
                print(f"无法加载质量数据: {code} snap {snap_num}")
                continue
            if not cache_file.exists():
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(
                    cache_file,
                    redshift=sim_redshift,
                    hmf=hmf,
                    hmf_err=hmf_err,
                    logM_centers=logM_centers,
                )
            print(f"{snap_num:04d} {code}: {int(np.count_nonzero(hmf))} non-empty FoF bins", flush=True)

            sim_results[code][snap_num] = {
                'redshift': sim_redshift, 'hmf': hmf, 'hmf_err': hmf_err,
                'logM_centers': logM_centers, 'color': colors[idx],
                'config': sim_configs[code]
            }

            # 计算理论质量函数
            M_theory = 10**np.arange(7.0, 13, 0.1)

            # 对于不同模型使用不同的功率谱
            if code == 'BT_soft':
                mfunc = mass_function.massFunction(
                    M_theory,
                    sim_redshift,
                    mdef='fof',
                    model='reed07',
                    q_out='dndlnM',
                    ps_args={'model': 'eisenstein98_bt'}  # 使用原来的BT功率谱
                )
            elif code == 'PL':
                mfunc = mass_function.massFunction(
                    M_theory,
                    sim_redshift,
                    mdef='fof',
                    model='reed07',
                    q_out='dndlnM',
                    ps_args={'model': 'eisenstein98_pl'}
                )
            elif code == 'BT_deep':
                mfunc = mass_function.massFunction(
                    M_theory,
                    sim_redshift,
                    mdef='fof',
                    model='reed07',
                    q_out='dndlnM',
                    ps_args={'model': 'eisenstein98_bt_soft'}  # 使用BT_soft功率谱
                )

            theory_results[code][snap_num] = {
                'M': M_theory/ cosmo_params['h'],
                'hmf': mfunc * cosmo_params['h']**3 / np.log10(np.exp(1)),
                'redshift': sim_redshift, 'color': colors[idx],
                'config': sim_configs[code]
            }
            print(f"{snap_num:04d} {code}: Reed07 reference ready", flush=True)

        except Exception as e:
            print(f"处理 {code} snap {snap_num} 时出错: {e}")
            continue

# 为所有模型和快照计算差值
for code in sim_configs.keys():
    for snap_num in snap_numbers:
        if snap_num in theory_results.get(code, {}) and snap_num in sim_results.get(code, {}):
            theory_data = theory_results[code][snap_num]
            sim_data = sim_results[code][snap_num]
            sim_mass = 10**sim_data['logM_centers']

            theory_valid = np.isfinite(theory_data['M']) & np.isfinite(theory_data['hmf']) & (theory_data['hmf'] > 0)
            sim_valid = np.isfinite(sim_mass) & np.isfinite(sim_data['hmf']) & (sim_data['hmf'] > 0)
            interp_func = interp1d(
                np.log10(theory_data['M'][theory_valid]),
                np.log10(theory_data['hmf'][theory_valid]),
                bounds_error=False,
                fill_value=np.nan,
            )

            theory_hmf_interp = 10**interp_func(np.log10(sim_mass[sim_valid]))
            ratio_valid = np.isfinite(theory_hmf_interp) & (theory_hmf_interp > 0)

            sim_data['diff_data'] = {
                'mass': sim_mass[sim_valid][ratio_valid],
                'relative_diff': sim_data['hmf'][sim_valid][ratio_valid] / theory_hmf_interp[ratio_valid] - 1,
                'diff_err': sim_data['hmf_err'][sim_valid][ratio_valid] / theory_hmf_interp[ratio_valid]
            }

n_panels = len(snap_numbers)
n_cols = min(PANEL_COLUMNS, n_panels)
n_rows = int(np.ceil(n_panels / n_cols))

bt_pl_ratio_results = {code: {} for code in ["BT_soft", "BT_deep"]}
bt_pl_ratio_values_by_row = {row: [] for row in range(n_rows)}
ratio_logm_edges = hmf_log_edges()
ratio_mass = 10 ** (0.5 * (ratio_logm_edges[:-1] + ratio_logm_edges[1:]))
for idx, snap_num in enumerate(snap_numbers):
    row = idx // n_cols
    pl_data = sim_results.get("PL", {}).get(snap_num)
    if pl_data is None:
        continue
    pl_hmf = pl_data["hmf"]
    pl_err = pl_data["hmf_err"]

    for code in ["BT_soft", "BT_deep"]:
        bt_data = sim_results.get(code, {}).get(snap_num)
        if bt_data is None:
            continue

        n_common = min(len(ratio_mass), len(pl_hmf), len(bt_data["hmf"]))
        bt_hmf = bt_data["hmf"][:n_common]
        bt_err = bt_data["hmf_err"][:n_common]
        pl_hmf_common = pl_hmf[:n_common]
        pl_err_common = pl_err[:n_common]

        valid = (
            np.isfinite(bt_hmf)
            & np.isfinite(pl_hmf_common)
            & np.isfinite(bt_err)
            & np.isfinite(pl_err_common)
            & (bt_hmf > 0)
            & (pl_hmf_common > 0)
        )
        if not np.any(valid):
            continue

        ratio = bt_hmf[valid] / pl_hmf_common[valid]
        ratio_err = ratio * np.sqrt(
            (bt_err[valid] / bt_hmf[valid]) ** 2
            + (pl_err_common[valid] / pl_hmf_common[valid]) ** 2
        )
        bt_pl_ratio_results[code][snap_num] = {
            "mass": ratio_mass[:n_common][valid],
            "ratio": ratio,
            "ratio_err": ratio_err,
            "config": sim_configs[code],
        }
        bt_pl_ratio_values_by_row[row].extend(ratio[np.isfinite(ratio) & (ratio > 0)])

bt_pl_ratio_ylims = {}
for row in range(n_rows):
    row_values = np.asarray(bt_pl_ratio_values_by_row.get(row, []), dtype=float)
    row_values = row_values[np.isfinite(row_values) & (row_values > 0)]
    if len(row_values):
        ymin = max(0.3, min(0.75, np.nanmin(row_values) * 0.8))
        ymax = 10 ** np.ceil(np.log10(max(2.0, np.nanmax(row_values) * 1.15)))
        bt_pl_ratio_ylims[row] = (ymin, ymax)
    else:
        bt_pl_ratio_ylims[row] = (0.75, 10.0)

apply_journal_style(base_fontsize=12.8)

# 创建主图形，每个单元格内包含质量函数和BT/PL比值两个子图
fig = plt.figure(figsize=(3.20 * n_cols, 3.45 * n_rows))
outer_grid = gridspec.GridSpec(
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

# 创建图例元素列表
legend_elements_upper = []

# 遍历所有快照
for idx, snap_num in enumerate(snap_numbers):
    # 创建内部网格：每个单元格内2行1列
    inner_grid = gridspec.GridSpecFromSubplotSpec(
        2,
        1,
        subplot_spec=outer_grid[idx],
        height_ratios=[4.0, 1.25],
        hspace=0.08,
    )

    # 获取两个子图
    ax_upper = fig.add_subplot(inner_grid[0])  # 上：质量函数
    ax_ratio = fig.add_subplot(inner_grid[1], sharex=ax_upper)  # 下：BT/PL

    # 获取红移信息
    redshift = None
    for code in sim_configs.keys():
        if snap_num in theory_results.get(code, {}):
            redshift = theory_results[code][snap_num]['redshift']
            break

    row = idx // n_cols
    col = idx % n_cols

    # 绘制上子图：质量函数
    for code in sim_configs.keys():
        # 绘制理论曲线
        if snap_num in theory_results.get(code, {}):
            theory_data = theory_results[code][snap_num]
            config = theory_data['config']
            theory_valid = np.isfinite(theory_data['M']) & np.isfinite(theory_data['hmf']) & (theory_data['hmf'] > 0)

            label = f'{config["name"]} Theory' if idx == 0 else None
            ax_upper.plot(theory_data['M'][theory_valid], theory_data['hmf'][theory_valid],
                         color=config['color'], linestyle=config['linestyle'],
                         linewidth=1.25, alpha=0.95, label=label)

            if idx == 0 and f'{config["name"]} Theory' not in [l.get_label() for l in legend_elements_upper]:
                legend_elements_upper.append(
                    plt.Line2D([0], [0], color=config['color'], linestyle=config['linestyle'],
                              linewidth=1.25, label=f'{config["name"]} theory')
                )

        # 绘制模拟数据点
        if snap_num in sim_results.get(code, {}):
            sim_data = sim_results[code][snap_num]
            config = sim_data['config']
            sim_mass = 10**sim_data['logM_centers']
            sim_valid = np.isfinite(sim_mass) & np.isfinite(sim_data['hmf']) & (sim_data['hmf'] > 0)

            label = f'{config["name"]} Simulation' if idx == 0 else None
            ax_upper.errorbar(sim_mass[sim_valid], sim_data['hmf'][sim_valid],
                            yerr=sim_data['hmf_err'][sim_valid],
                            fmt=config['marker'], color=config['color'],
                            markersize=3.5, capsize=1.6, alpha=0.9,
                            markerfacecolor=config['markerfacecolor'],
                            markeredgecolor=config['color'],
                            markeredgewidth=0.8, elinewidth=0.7, label=label)

            if idx == 0 and f'{config["name"]} Simulation' not in [l.get_label() for l in legend_elements_upper]:
                legend_elements_upper.append(
                    plt.Line2D([0], [0], color=config['color'], marker=config['marker'],
                              markersize=3.5, markeredgecolor=config['color'],
                              markeredgewidth=0.8, markerfacecolor=config['markerfacecolor'],
                              linestyle='', label=f'{config["name"]} simulation')
                )

    # 设置上子图属性
    format_axes(ax_upper, grid=True)
    y_min = 1e-7 if redshift is not None and redshift >= 8.0 else 1e-4
    ax_upper.set(xscale='log', yscale='log', xlim=(HMF_XMIN_MSUN, 2e11), ylim=(y_min, 1e2))
    set_hmf_log_ticks(ax_upper, y_decades=(int(np.log10(y_min)), 2))
    mark_hmf_resolution(ax_upper, annotate=False)

    panel_label(ax_upper, rf'$z={format_redshift(redshift, 2)}$', loc=(0.95, 0.92), ha="right", fontsize=12.4)

    # 绘制下子图：直接的BT/PL质量函数比值
    for code in ["BT_soft", "BT_deep"]:
        if snap_num in bt_pl_ratio_results.get(code, {}):
            ratio_data = bt_pl_ratio_results[code][snap_num]
            config = ratio_data["config"]
            ax_ratio.errorbar(
                ratio_data["mass"],
                ratio_data["ratio"],
                yerr=ratio_data["ratio_err"],
                fmt=config["marker"],
                color=config["color"],
                markersize=3.3,
                capsize=1.5,
                alpha=0.9,
                markerfacecolor=config["markerfacecolor"],
                markeredgecolor=config["color"],
                markeredgewidth=0.8,
                elinewidth=0.65,
            )

    format_axes(ax_ratio, grid=True)
    ax_ratio.axhline(y=1.0, color='black', linestyle='-', linewidth=0.7, alpha=0.6)
    ax_ratio.axhline(y=2.0, color='gray', linestyle=':', linewidth=0.6, alpha=0.55)
    ax_ratio.axhline(y=5.0, color='gray', linestyle=':', linewidth=0.6, alpha=0.55)
    ax_ratio.set(xscale='log', yscale='log', xlim=(HMF_XMIN_MSUN, 2e11), ylim=bt_pl_ratio_ylims[row])
    set_hmf_log_ticks(ax_ratio, ratio_axis=True)
    mark_hmf_resolution(ax_ratio, annotate=(idx == 0))

    # 只在最后一行的下子图显示x轴标签
    if row == n_rows - 1:
        ax_ratio.set_xlabel(r'$M_{\mathrm{FOF}}\,[M_\odot]$')
        ax_upper.tick_params(labelbottom=False)
    else:
        ax_upper.tick_params(labelbottom=False)
        ax_ratio.tick_params(labelbottom=False)

    # 只在第一列的上子图显示y轴标签
    if col == 0:
        ax_upper.set_ylabel(r'$dn/d\log_{10}M\,[{\rm Mpc}^{-3}]$')
        ax_ratio.set_ylabel(r'$f_{\rm BT}/f_{\rm PL}$')
    else:
        ax_upper.tick_params(labelleft=False)
        ax_ratio.tick_params(labelleft=False)

model_handles = []
model_labels = []
for config in sim_configs.values():
    line_handle = plt.Line2D(
        [0],
        [0],
        color=config['color'],
        linestyle=config['linestyle'],
        linewidth=1.25,
    )
    marker_handle = plt.Line2D(
        [0],
        [0],
        color=config['color'],
        marker=config['marker'],
        markersize=3.7,
        markeredgecolor=config['color'],
        markeredgewidth=0.8,
        markerfacecolor=config['markerfacecolor'],
        linestyle='',
    )
    model_handles.append((line_handle, marker_handle))
    model_labels.append(config['name'])

fig.axes[0].legend(
    model_handles,
    model_labels,
    title=r"Reed07 FoF; BT: $m_s=1.5$",
    handler_map={tuple: HandlerTuple(ndivide=None)},
    loc='lower left',
    ncol=1,
    fontsize=10.3,
    title_fontsize=10.0,
    frameon=True,
    framealpha=0.75,
    edgecolor='none',
    handlelength=2.1,
    borderpad=0.25,
    labelspacing=0.25,
    handletextpad=0.35,
)

fof_output_path = Path(os.environ.get("FOF_OUTPUT_PATH", PAPERPLOT_ROOT / "figures" / "mass-function.png"))
print(f"Saving FoF/Reed07 figure: {fof_output_path}", flush=True)
fof_output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(fof_output_path, dpi=320, bbox_inches="tight", pad_inches=0.08)
plt.close(fig)
print(f"Saved FoF/Reed07 figure: {fof_output_path}", flush=True)
