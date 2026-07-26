#!/usr/bin/env python3
"""Summarize released concentration accuracy and scatter measurements."""

from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "figure_data" / "concentration"
RATIO_INPUT = DATA_DIR / "concentration_qc_theory_ratios.csv"
SCATTER_INPUT = DATA_DIR / "concentration_qc_scatter.csv"
ACCURACY_OUTPUT = DATA_DIR / "concentration_qc_accuracy_summary.csv"
SCATTER_OUTPUT = DATA_DIR / "concentration_qc_scatter_mass_ranges.csv"

PARTICLE_MASS_MSUN = 1.89e6
STRICT_PARTICLE_COUNT = 1000
STRICT_LOG10_MASS = math.log10(PARTICLE_MASS_MSUN * STRICT_PARTICLE_COUNT)
BIN_HALF_WIDTH_DEX = 0.125
MIN_HALOS_PER_BIN = 20

ACCURACY_SELECTIONS = {
    "strict_1000_particle_full_bins": lambda mass: (
        mass - BIN_HALF_WIDTH_DEX >= STRICT_LOG10_MASS
    ),
    "quoted_1e9_to_1e9p5_centers": lambda mass: 9.0 <= mass < 9.5,
}

SCATTER_SELECTIONS = {
    "quoted_1e9_to_1e9p5_centers": lambda mass: 9.0 <= mass < 9.5,
    "resolved_low_1e9p5_to_1e10": lambda mass: 9.5 <= mass < 10.0,
    "resolved_high_1e10p5_to_1e11p5": lambda mass: 10.5 <= mass < 11.5,
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows generated for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_accuracy(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                row["model"],
                row["snapshot"],
                row["redshift"],
                row["theory_model"],
            )
        ].append(row)

    output = []
    for (model, snapshot, redshift, theory_model), group in sorted(grouped.items()):
        for selection_name, include_mass in ACCURACY_SELECTIONS.items():
            selected = [
                row
                for row in group
                if include_mass(float(row["log10_M200c_center_Msun"]))
                and int(row["n_halos_bin"]) >= MIN_HALOS_PER_BIN
            ]
            if not selected:
                continue
            masses = [float(row["log10_M200c_center_Msun"]) for row in selected]
            ratios = [float(row["sim_over_theory"]) for row in selected]
            absolute = [abs(value - 1.0) for value in ratios]
            output.append(
                {
                    "model": model,
                    "snapshot": snapshot,
                    "redshift": f"{float(redshift):.10e}",
                    "theory_model": theory_model,
                    "selection": selection_name,
                    "n_bins": len(selected),
                    "log10_mass_center_min_msun": f"{min(masses):.6f}",
                    "log10_mass_center_max_msun": f"{max(masses):.6f}",
                    "median_sim_over_theory": f"{statistics.median(ratios):.10e}",
                    "median_abs_fraction": f"{statistics.median(absolute):.10e}",
                    "max_abs_fraction": f"{max(absolute):.10e}",
                }
            )
    return output


def summarize_scatter(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: defaultdict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["snapshot"], row["redshift"])].append(row)

    output = []
    for (model, snapshot, redshift), group in sorted(grouped.items()):
        for selection_name, include_mass in SCATTER_SELECTIONS.items():
            selected = [
                row
                for row in group
                if include_mass(float(row["log10_M200c_center_Msun"]))
                and int(row["n_halos_bin"]) >= MIN_HALOS_PER_BIN
            ]
            if not selected:
                continue
            masses = [float(row["log10_M200c_center_Msun"]) for row in selected]
            scatter_log10 = [
                float(row["sigma_68_log10_c"])
                for row in selected
            ]
            median_log10 = statistics.median(scatter_log10)
            output.append(
                {
                    "model": model,
                    "snapshot": snapshot,
                    "redshift": f"{float(redshift):.10e}",
                    "selection": selection_name,
                    "n_bins": len(selected),
                    "log10_mass_center_min_msun": f"{min(masses):.6f}",
                    "log10_mass_center_max_msun": f"{max(masses):.6f}",
                    "median_sigma68_log10_c": f"{median_log10:.10e}",
                    "median_sigma68_ln_c": f"{median_log10 * math.log(10.0):.10e}",
                    "min_sigma68_log10_c": f"{min(scatter_log10):.10e}",
                    "max_sigma68_log10_c": f"{max(scatter_log10):.10e}",
                }
            )
    return output


def main() -> None:
    accuracy = summarize_accuracy(read_rows(RATIO_INPUT))
    scatter = summarize_scatter(read_rows(SCATTER_INPUT))
    write_rows(ACCURACY_OUTPUT, accuracy)
    write_rows(SCATTER_OUTPUT, scatter)
    print(ACCURACY_OUTPUT)
    print(SCATTER_OUTPUT)
    print(f"Strict full-bin threshold: log10(M/Msun) >= {STRICT_LOG10_MASS:.6f}")


if __name__ == "__main__":
    main()
