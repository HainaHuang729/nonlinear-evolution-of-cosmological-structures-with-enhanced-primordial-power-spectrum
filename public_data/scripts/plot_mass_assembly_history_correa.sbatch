#!/bin/bash
#SBATCH --job-name=plot_mah_correa
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/oss06/data/project/tkcastrosim/HNHuang/project_big_sim/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs/plot_mass_assembly_history_correa_%j.out
#SBATCH --error=/oss06/data/project/tkcastrosim/HNHuang/project_big_sim/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs/plot_mass_assembly_history_correa_%j.err

set -euo pipefail

ARTICLE_DIR=/oss06/data/project/tkcastrosim/HNHuang/project_big_sim/papers/article_nonlinear_evolution_pps
PYTHON=/oss06/data/project/tkcastrosim/HNHuang/envs/Miniconda3/envs/21cmfast/bin/python

cd "$ARTICLE_DIR"
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR=/tmp/matplotlib-${SLURM_JOB_ID}

"$PYTHON" public_data/scripts/plot_mass_assembly_history_correa.py \
    --output mass-assembly-history-correa-halfmass.png
