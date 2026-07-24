#!/usr/bin/env python3
"""Add the manuscript labels to the released clean projection mosaic."""

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLE_ROOT = next(
    (parent for parent in SCRIPT_DIR.parents if (parent / "main.tex").exists()),
    SCRIPT_DIR.parents[2],
)
DATA_DIR = ARTICLE_ROOT / "public_data" / "figure_data" / "projection"
CLEAN_INPUT = Path(os.environ.get("PROJECTION_CLEAN_INPUT", DATA_DIR / "projection-clean.png"))
METADATA_INPUT = Path(
    os.environ.get("PROJECTION_METADATA_INPUT", DATA_DIR / "projection-panel-metadata.json")
)
OUTPUT_PATH = Path(os.environ.get("PROJECTION_OUTPUT_PATH", ARTICLE_ROOT / "projection.png"))

PANEL_LABELS = {
    "PL": "PL",
    "kp1": r"BT $k_p=1$",
    "kp10": r"BT $k_p=10$",
}
LABEL_FONTSIZE = 16
LABEL_EFFECTS = [pe.withStroke(linewidth=2.0, foreground="black", alpha=0.75)]
AXES_COUNT = 3
WSPACE = 0.06
AXIS_WIDTH = 1.0 / (AXES_COUNT + WSPACE * (AXES_COUNT - 1))
AXIS_GAP = WSPACE * AXIS_WIDTH
LABEL_X_AXES = 0.04
LABEL_Y_AXES = 0.045


def panel_origin(row: int, col: int) -> tuple[float, float]:
    x0 = col * (AXIS_WIDTH + AXIS_GAP)
    y0 = (AXES_COUNT - 1 - row) * (AXIS_WIDTH + AXIS_GAP)
    return x0, y0


def main() -> None:
    if not CLEAN_INPUT.exists():
        raise FileNotFoundError(f"Missing released projection mosaic: {CLEAN_INPUT}")
    if not METADATA_INPUT.exists():
        raise FileNotFoundError(f"Missing projection metadata: {METADATA_INPUT}")

    image = mpimg.imread(CLEAN_INPUT)
    metadata = json.loads(METADATA_INPUT.read_text(encoding="utf-8"))
    height, width = image.shape[:2]
    dpi = 300

    fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(image, origin="upper")
    ax.set_axis_off()

    for panel in metadata:
        x0, y0 = panel_origin(int(panel["row"]), int(panel["col"]))
        fig.text(
            x0 + LABEL_X_AXES * AXIS_WIDTH,
            y0 + LABEL_Y_AXES * AXIS_WIDTH,
            f"{PANEL_LABELS[panel['model']]}\nz={panel['redshift']}",
            fontsize=LABEL_FONTSIZE,
            color="white",
            weight="bold",
            ha="left",
            va="bottom",
            linespacing=0.95,
            path_effects=LABEL_EFFECTS,
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=dpi, pad_inches=0)
    plt.close(fig)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
