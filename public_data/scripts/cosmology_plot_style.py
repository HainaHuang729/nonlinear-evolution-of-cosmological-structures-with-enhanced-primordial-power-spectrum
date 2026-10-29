"""Shared plotting style for cosmology publication figures.

The defaults are intentionally conservative and should work on headless
clusters without requiring a full LaTeX installation.
"""

from pathlib import Path

import matplotlib as mpl


JOURNAL_COLORS = {
    "blue": "#0072B2",
    "orange": "#D55E00",
    "green": "#009E73",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "yellow": "#E69F00",
    "black": "#000000",
    "gray": "#666666",
}


def apply_journal_style(base_fontsize: float = 8.5) -> None:
    """Apply a compact ApJ/MNRAS-like Matplotlib style."""
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIXGeneral", "Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
            "font.size": base_fontsize,
            "axes.labelsize": base_fontsize + 1.6,
            "axes.labelweight": "bold",
            "axes.titlesize": base_fontsize + 1.8,
            "axes.titleweight": "bold",
            "axes.linewidth": 1.1,
            "legend.fontsize": base_fontsize - 1.0,
            "legend.frameon": False,
            "legend.handlelength": 1.8,
            "legend.borderaxespad": 0.4,
            "xtick.labelsize": base_fontsize + 1.0,
            "ytick.labelsize": base_fontsize + 1.0,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 5.2,
            "ytick.major.size": 5.2,
            "xtick.minor.size": 3.0,
            "ytick.minor.size": 3.0,
            "xtick.major.width": 1.1,
            "ytick.major.width": 1.1,
            "xtick.minor.width": 0.9,
            "ytick.minor.width": 0.9,
            "lines.linewidth": 1.35,
            "lines.markersize": 3.5,
            "errorbar.capsize": 2.0,
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def format_axes(ax, *, grid: bool = False) -> None:
    """Use consistent ticks, spines, and optional light grids on an axis."""
    ax.tick_params(
        which="major",
        direction="in",
        top=True,
        right=True,
        length=5.2,
        width=1.1,
    )
    ax.tick_params(
        which="minor",
        direction="in",
        top=True,
        right=True,
        length=3.0,
        width=0.9,
    )
    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
    if grid:
        ax.grid(True, which="major", color="0.88", linestyle="-", linewidth=0.5)


def sparse_errorbar(ax, *args, marker_stride=2, marker_offset=0, **kwargs):
    """Space large symbols while retaining every measurement and error bar.

    Small dots show all measured centres. The original interval segments are
    retained at every x coordinate, with no caps and lighter strokes. No input
    arrays, bin definitions, or uncertainty values are subsampled.
    """
    kwargs = dict(kwargs)
    kwargs["capsize"] = 0
    kwargs["elinewidth"] = min(kwargs.get("elinewidth", 0.5), 0.5)
    kwargs["markersize"] = min(kwargs.get("markersize", 3.0), 3.0)
    container = ax.errorbar(*args, **kwargs)
    line, _, bars = container.lines
    if line is not None:
        line.set_markevery((marker_offset, marker_stride))
        # Retain the smaller marker at every original centre, including values
        # with zero uncertainty or missing/nonfinite error extents.
        ax.plot(
            line.get_xdata(), line.get_ydata(), linestyle="none", marker=".",
            markersize=1.35, color=line.get_color(), alpha=0.65,
            zorder=line.get_zorder() - 0.05, label="_nolegend_",
        )
    for bar in bars:
        bar.set_alpha(0.60)
    return container


def panel_label(ax, text, loc=(0.05, 0.90), fontsize=None, ha="left"):
    """Place a small unobtrusive label inside a panel."""
    ax.text(
        loc[0],
        loc[1],
        text,
        transform=ax.transAxes,
        ha=ha,
        va="top",
        fontsize=fontsize,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
    )


def format_redshift(z, precision=2):
    """Format redshift labels without displaying negative zero."""
    z = float(z)
    if abs(z) < 0.5 * 10**(-precision):
        z = 0.0
    return f"{z:.{precision}f}"


def save_publication_figure(fig, output_path, close=True):
    """Save a PNG figure using journal-friendly settings."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    png_path = output_path.with_suffix(".png")
    fig.savefig(png_path)

    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)
