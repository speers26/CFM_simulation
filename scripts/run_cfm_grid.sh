#!/bin/bash

#SBATCH -p serial
#SBATCH -J CFM_grid_simulation
#SBATCH --mem=20G
#SBATCH --array=1-5

set -euo pipefail

source /etc/profile
conda activate CFM

LATLON_FILE=${LATLON_FILE:-scripts/latlon_pairs.txt}
RCM=${RCM:-RACMO}
PHYSRHO=${PHYSRHO:-GSFC2020}
LIQUID=${LIQUID:-bucket}

line=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LATLON_FILE")
lat=$(echo "$line" | awk '{print $1}')
lon=$(echo "$line" | awk '{print $2}')

if [[ -z "${lat}" || -z "${lon}" ]]; then
	echo "No lat/lon found for task ${SLURM_ARRAY_TASK_ID} in ${LATLON_FILE}"
	exit 1
fi

echo "Starting CFM grid simulation for lat=${lat}, lon=${lon}"
python scripts/run_cfm.py --lat "$lat" --lon "$lon" --physrho "$PHYSRHO" --rcm "$RCM" --liquid "$LIQUID"

