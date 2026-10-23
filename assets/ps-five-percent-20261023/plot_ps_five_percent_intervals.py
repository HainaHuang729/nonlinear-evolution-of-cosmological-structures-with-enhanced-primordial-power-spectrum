"""Plot verified agreement segments while retaining every adopted PS bin."""
import os
assert os.environ.get("SLURM_JOB_ID"), "Submit via Slurm"
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "article_figure_check_2026-07-08"
SOURCE = FIG / "ps_five_percent_job2269694"
VERIFIED = FIG / "ps_five_percent_verify_job2269696/summary.json"
OUT = FIG / ("ps_five_percent_plot_job"+os.environ["SLURM_JOB_ID"])
OUT.mkdir(exist_ok=False)
shutil.copyfile(__file__, OUT / Path(__file__).name)
summary = json.loads((SOURCE / "summary.json").read_text())
assert summary["passed"] and json.loads(VERIFIED.read_text())["passed"]
for path, expected in summary["hashes"].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
with (SOURCE / "per_bin.csv").open() as stream:
    rows = [r for r in csv.DictReader(stream) if r["kind"] == "phase_pair"]
style = FIG / "ps25_paper_format_job2249049"
sys.path.insert(0, str(style))
from cosmology_plot_style import apply_journal_style, JOURNAL_COLORS
apply_journal_style(base_fontsize=10.)
shutil.copyfile(style / "cosmology_plot_style.py", OUT / "cosmology_plot_style.py")
MODELS = [("pl", "PL", JOURNAL_COLORS["black"]),
          ("kp1", r"BT $k_p=1$", JOURNAL_COLORS["blue"]),
          ("kp10", r"BT $k_p=10$", JOURNAL_COLORS["green"])]
EPOCHS = [("0056", 0.), ("0048", 1.0717968600643704),
          ("0040", 3.4410805658271206), ("0032", 8.519850605215494)]
selected = {}
for snap, epoch in EPOCHS:
    for model, label, color in MODELS:
        group = sorted([r for r in rows if r["snapshot"] == snap and r["model"] == model],
                       key=lambda r: float(r["k_hMpc"]))
        if not group:
            continue
        k, power, theory = [np.array([float(r[key]) for r in group]) for key in ("k_hMpc", "P_sim", "P_HMcode")]
        assert len(k) == 118 and np.all(np.diff(k) > 0)
        np.testing.assert_allclose([float(r["z"]) for r in group], epoch, atol=1e-12, rtol=0)
        passing = abs(power/theory-1) <= summary["threshold"]
        np.testing.assert_array_equal(passing, [r["within_five_percent"] == "True" for r in group])
        selected[snap, model] = (k, power/theory, passing)
all_ratios = np.concatenate([ratio for k, ratio, good in selected.values()])
ylim = (float(np.floor((min(.95, all_ratios.min())-.03)/.05)*.05),
        float(np.ceil((max(1.05, all_ratios.max())+.03)/.05)*.05))
assert ylim[0] < all_ratios.min() and ylim[1] > all_ratios.max()


def record(snap, model, window):
    return next(r for r in summary["results"] if (r["snapshot"], r["model"], r["kind"], r["window"]) ==
                (snap, model, "phase_pair", window))


def make_plot(stem, upper):
    fig = plt.figure(figsize=(11.4, 10.2))
    grid = fig.add_gridspec(2, 2, left=.105, right=.98, bottom=.09, top=.89, wspace=.20, hspace=.35)
    metadata = []
    for panel, (snap, epoch) in enumerate(EPOCHS):
        inner = grid[panel//2, panel % 2].subgridspec(2, 1, height_ratios=[3.6, 1.2], hspace=.05)
        main = fig.add_subplot(inner[0])
        strip = fig.add_subplot(inner[1], sharex=main)
        main.axhspan(.95, 1.05, color="#eeeeee", zorder=0)
        main.axhline(1., color="#888888", lw=.65, zorder=1)
        main.set_ylim(*ylim)
        main.set_title(rf"$z={epoch:.4f}$", loc="left", fontsize=12)
        tail = record(snap, "pl", "HMcode_k_overlap")["terminal_interval"]
        label = "PL below 10: none" if tail is None else f"PL below 10: {tail['first_k']:.2f}-{tail['last_k']:.2f}"
        main.text(1., 1.025, label, transform=main.transAxes, ha="right", va="bottom", fontsize=9.)
        strip.set_yticks([2, 1, 0], [label for model, label, color in MODELS])
        strip.set_ylim(-.5, 2.5)
        for tick, (_, label, color) in zip(strip.get_yticklabels(), MODELS):
            tick.set_color(color)
            tick.set_fontsize(9.)
        for model_index, (model, label, color) in enumerate(MODELS):
            ypos = 2-model_index
            if (snap, model) not in selected:
                assert (snap, model) == ("0056", "kp10")
                strip.text(.5, ypos, "No phase pair", transform=strip.get_yaxis_transform(),
                           ha="center", va="center", color="#666666", fontsize=9.)
                continue
            k, ratio, good = selected[snap, model]
            mask = k <= upper
            x, y, passes = k[mask], ratio[mask], good[mask]
            main.plot(x, y, color=color, lw=.9, alpha=.45, zorder=2)
            strip.plot([x[0], x[-1]], [ypos, ypos], color="#dedede", lw=1., zorder=1)
            transitions = np.diff(np.r_[False, passes, False].astype(int))
            spans = list(zip(np.flatnonzero(transitions == 1), np.flatnonzero(transitions == -1)))
            for start, stop in spans:
                if stop-start == 1:
                    main.plot(x[start], y[start], "o", color=color, ms=3., zorder=4)
                    strip.plot(x[start], ypos, "o", color=color, ms=4., zorder=3)
                else:
                    main.plot(x[start:stop], y[start:stop], color=color, lw=2.1, zorder=3)
                    strip.plot([x[start], x[stop-1]], [ypos, ypos], color=color, lw=5.,
                               solid_capstyle="butt", zorder=3)
            if not passes.any():
                strip.text(.5, ypos, "None", transform=strip.get_yaxis_transform(), ha="center", va="center",
                           color="#777777", fontsize=8.5, bbox=dict(facecolor="white", edgecolor="none", pad=.3))
            metadata.append(dict(snapshot=snap, model=model, bins=len(x), passing_bins=int(passes.sum()),
                highlighted_runs=[dict(first_k=float(x[a]), last_k=float(x[b-1]), bins=int(b-a)) for a, b in spans]))
        for axis in (main, strip):
            axis.set_xscale("log")
            axis.set_xlim(2.4, upper*1.025)
            ticks = [2.5, 5, 10] if upper <= 10 else [2.5, 5, 10, 20, 32]
            axis.xaxis.set_major_locator(FixedLocator(ticks))
            axis.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:g}"))
            axis.xaxis.set_minor_formatter(NullFormatter())
            axis.grid(axis="x", which="major", alpha=.14)
        main.grid(axis="y", alpha=.16)
        main.tick_params(labelbottom=False)
        main.set_ylabel(r"$P_{\rm sim}/P_{\rm HMcode}$")
        strip.tick_params(axis="y", which="both", length=0, right=False)
        strip.spines[["top", "right", "left"]].set_visible(False)
        if panel >= 2:
            strip.set_xlabel(r"$k\ [h\,\mathrm{Mpc}^{-1}]$")
    handles = [Line2D([], [], color=color, lw=2., label=label) for model, label, color in MODELS]
    handles.append(Patch(facecolor="#eeeeee", edgecolor="#cccccc", label=r"$\pm5\%$"))
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.54, .965), ncol=4, fontsize=11.)
    fig.text(.54, .985, r"$25\,h^{-1}\,\mathrm{Mpc}$: phase-mean spectra / HMcode2020", ha="center", va="top", fontsize=14.)
    fig.text(.54, .025, "Thick curves and bars: every sampled bin within 5%. Thin curves: all adopted bins.",
             ha="center", fontsize=10.)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for axis in fig.axes:
        for label in [*axis.get_xticklabels(), *axis.get_yticklabels(), axis.xaxis.label, axis.yaxis.label]:
            if label.get_visible() and label.get_text():
                bounds = label.get_window_extent(renderer)
                assert bounds.x0 >= 0 and bounds.x1 <= fig.bbox.width+1 and bounds.y0 >= 0, label.get_text()
    path = OUT / (stem+".png")
    fig.savefig(path, dpi=260, bbox_inches=None)
    plt.close(fig)
    with Image.open(path) as image:
        image.load()
        size = list(image.size)
        pixels = np.asarray(image.convert("RGB"))
        assert size[0] > 2000 and size[1] > 2000 and pixels.std() > 10
        panel_checks = []
        for row in range(2):
            for col in range(2):
                area = pixels[int((.10+row*.43)*size[1]):int((.46+row*.43)*size[1]),
                              int((.10+col*.47)*size[0]):int((.50+col*.47)*size[0])]
                ink = float(np.mean(np.any(area < 180, axis=2)))
                assert ink > .01
                panel_checks.append(ink)
    return dict(file=path.name, upper_k=upper, size=size, panel_ink_fractions=panel_checks,
                plotted=metadata, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


figures = [make_plot("power-spectrum-five-percent-ranges", summary["current_limits"]["k_max"]),
           make_plot("power-spectrum-five-percent-k10", 10.)]
for name in ("summary.json", "intervals.csv", "per_bin.csv"):
    shutil.copyfile(SOURCE / name, OUT / ("audit-"+name))
shutil.copyfile(VERIFIED, OUT / "verification.json")
result = dict(passed=True, source=str(SOURCE), verified=str(VERIFIED), figures=figures,
              model_colors={model: color for model, label, color in MODELS},
              denominator="model-specific HMcode2020", all_adopted_bins_preserved=True,
              no_manuscript_changes=True, no_simulation_data_changes=True,
              caveat="Agreement on existing bins, not a demonstrated simulation trust interval or model calibration.")
(OUT / "summary.json").write_text(json.dumps(result, indent=2)+"\n")
print("OUTPUT", OUT, flush=True)
