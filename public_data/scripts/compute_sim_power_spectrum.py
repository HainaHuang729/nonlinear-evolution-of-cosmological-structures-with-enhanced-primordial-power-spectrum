#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Save simulation matter power spectra to .npz files."""

import argparse
import os
from pathlib import Path

import numpy as np
from swiftsimio import load
from swiftsimio.visualisation.power_spectrum import (
    deposition_to_power_spectrum,
    render_to_deposit,
)


# 宇宙学参数
h_val = 0.6736

DEFAULT_SNAPSHOT_LABELS = ["0056", "0048", "0040", "0032", "0024", "0016"]
DEFAULT_INPUT_TEMPLATE = (
    "/project/tkcastrosim/HNHuang/project_big_sim/data/PL/"
    "PL_128_1024/PL_128_1024_{label}.hdf5"
)
DEFAULT_OUTPUT_PREFIX = "PL_128_1024_snap"
DEFAULT_OUTPUT_DIR = "sim_power_data"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute SWIFT dark-matter power spectra and cache them as .npz."
    )
    parser.add_argument(
        "--path-template",
        default=DEFAULT_INPUT_TEMPLATE,
        help=(
            "Input snapshot template. Use either '{label}' or '{}' as the "
            "snapshot-label placeholder."
        ),
    )
    parser.add_argument(
        "--output-prefix",
        default=DEFAULT_OUTPUT_PREFIX,
        help="Prefix for output .npz files.",
    )
    parser.add_argument(
        "--snap-labels",
        nargs="+",
        default=DEFAULT_SNAPSHOT_LABELS,
        help="Snapshot labels to process.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for output .npz files.",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=1024,
        help="Mesh resolution for mass deposition.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=256,
        help="Worker count passed to deposition_to_power_spectrum.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip labels whose output .npz already exists.",
    )
    return parser.parse_args()


def format_input_path(path_template, label):
    if "{label}" in path_template:
        return path_template.format(label=label)
    return path_template.format(label)


def load_and_save(filepath, label, output_dir, output_prefix, resolution, workers):
    """Read one simulation snapshot, compute P(k), and save it as .npz."""
    print(f"处理快照 {label} ...")
    try:
        data = load(filepath)
    except Exception as exc:
        print(f"  无法加载文件 {filepath}: {exc}")
        return

    n_particles = data.dark_matter.coordinates.shape[0]
    boxsize = data.metadata.boxsize

    deposit = render_to_deposit(
        data.dark_matter,
        resolution=resolution,
        project="masses",
        parallel=True,
    )
    k_sim, ps_sim, _ = deposition_to_power_spectrum(
        deposit,
        boxsize,
        folding=0,
        cross_deposition=None,
        wavenumber_bins=None,
        workers=workers,
        shot_noise_norm=n_particles,
    )

    # 单位转换：k (1/Mpc) -> k (h/Mpc); P (Mpc^3) -> P ((Mpc/h)^3)
    k_h = (k_sim / h_val).value
    ps_h = (ps_sim * h_val**3).value
    z = data.metadata.redshift

    outfile = output_dir / f"{output_prefix}{label}.npz"
    np.savez(outfile, k=k_h, P=ps_h, z=z)
    print(f"  已保存: {outfile}")


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for label in args.snap_labels:
        outfile = output_dir / f"{args.output_prefix}{label}.npz"
        if args.skip_existing and outfile.exists():
            print(f"跳过快照 {label}; 已存在: {outfile}")
            continue
        load_and_save(
            format_input_path(args.path_template, label),
            label,
            output_dir,
            args.output_prefix,
            args.resolution,
            args.workers,
        )

    print("\n所有数据保存完毕。")


if __name__ == "__main__":
    main()
