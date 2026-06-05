#!/bin/bash

#SBATCH -J halo_radial_n100_ludlow177
#SBATCH -N 1 -c 8
#SBATCH -o /project/tkcastrosim/HNHuang/project_big_sim/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs/%j_halo_radial_n100_ludlow177.out
#SBATCH -e /project/tkcastrosim/HNHuang/project_big_sim/analysis/_used_by_article_nonlinear_evolution_pps/paperplot/logs/%j_halo_radial_n100_ludlow177.err
#SBATCH --mem=120GB

set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8

export PROJECT_BIG_SIM_ROOT=/project/tkcastrosim/HNHuang/project_big_sim
export PAPERPLOT_ROOT=$PROJECT_BIG_SIM_ROOT/analysis/_used_by_article_nonlinear_evolution_pps/paperplot
export MPLCONFIGDIR=$PAPERPLOT_ROOT/cache/mplconfig
export RADIAL_PROFILE_CACHE_DIR=$PAPERPLOT_ROOT/cache/halo_density_radial_n100_ludlow177
export RADIAL_MAX_HALOS_PER_BIN=100
export RADIAL_BOOTSTRAPS=160
export RADIAL_PARTICLE_CHUNK=250000
export POWER_KAPPA_THRESHOLD=0.177
export POWER_CRITERION_LABEL="Ludlow19 stack"
export RADIAL_OUTPUT_BASENAME=halo-density-radial-n100-ludlow177.png

PYTHON=/project/tkcastrosim/HNHuang/envs/Miniconda3/envs/21cmfast/bin/python3.10
SCRIPT=/project/tkcastrosim/HNHuang/project_21cmFast/paper/scripts/bluetilted/bt_plot_halo_density_radial_trial_png.py
LOCAL_FIGURES=/project/tkcastrosim/HNHuang/project_21cmFast/paper/figures

mkdir -p "$PAPERPLOT_ROOT/logs" "$MPLCONFIGDIR" "$RADIAL_PROFILE_CACHE_DIR" "$LOCAL_FIGURES"

cd /project/tkcastrosim/HNHuang/project_21cmFast
echo "Start at $(date)"

for label in "PL" "BT(soft)" "BT(deep)"; do
  for mass in 1e8 1e9 1e10 1e11; do
    echo "Computing cache: label=${label} mass=${mass}"
    RADIAL_ONLY_LABELS="$label" RADIAL_ONLY_MASSES="$mass" "$PYTHON" "$SCRIPT"
  done
done

echo "Drawing final cached figure"
unset RADIAL_ONLY_LABELS
unset RADIAL_ONLY_MASSES
"$PYTHON" "$SCRIPT"

cp -a "$PAPERPLOT_ROOT/figures/$RADIAL_OUTPUT_BASENAME" "$LOCAL_FIGURES/$RADIAL_OUTPUT_BASENAME"

echo "Figure: $PAPERPLOT_ROOT/figures/$RADIAL_OUTPUT_BASENAME"
echo "Local figure: $LOCAL_FIGURES/$RADIAL_OUTPUT_BASENAME"
echo "End at $(date)"
