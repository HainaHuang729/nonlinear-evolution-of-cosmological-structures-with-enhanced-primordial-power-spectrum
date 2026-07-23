#!/bin/bash

#SBATCH -J article_halo_catalog
#SBATCH -N 1
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 04:00:00
#SBATCH -o /project/tkcastrosim/HNHuang/project_big_sim/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs/%j_article_halo_catalog.out
#SBATCH -e /project/tkcastrosim/HNHuang/project_big_sim/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs/%j_article_halo_catalog.err

set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4
export PROJECT_BIG_SIM_ROOT=/project/tkcastrosim/HNHuang/project_big_sim

PYTHON=/project/tkcastrosim/HNHuang/envs/Miniconda3/envs/21cmfast/bin/python
SCRIPT=$PROJECT_BIG_SIM_ROOT/papers/article_nonlinear_evolution_pps/public_data/scripts/extract_article_halo_catalog.py
OUTPUT_DIR=$PROJECT_BIG_SIM_ROOT/analysis/_used_by_article_nonlinear_evolution_pps/public_catalog_release_2026-07-23
LOG_DIR=$PROJECT_BIG_SIM_ROOT/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

echo "Start: $(date --iso-8601=seconds)"
"$PYTHON" "$SCRIPT" --project-root "$PROJECT_BIG_SIM_ROOT" --output-dir "$OUTPUT_DIR"
echo "End: $(date --iso-8601=seconds)"
