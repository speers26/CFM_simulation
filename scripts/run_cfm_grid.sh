#!/bin/bash

#SBATCH -p serial
#SBATCH -J CFM_grid_simulation
#SBATCH --mem=20G
#SBATCH --array=1-396
#SBATCH -o logs/cfm_grid_%A_%a.out
#SBATCH -e logs/cfm_grid_%A_%a.err

source /etc/profile
set -euo pipefail

export HDF5_USE_FILE_LOCKING=FALSE

echo "Reading from latlon file"
LATLON_FILE=${LATLON_FILE:-scripts/latlon_pairs.txt}
RCM=${RCM:-RACMO}
PHYSRHO=${PHYSRHO:-GSFC2020}
LIQUID=${LIQUID:-bucket}
echo "done."

line=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$LATLON_FILE")
lat=$(echo "$line" | awk '{print $1}')
lon=$(echo "$line" | awk '{print $2}')

if [[ -z "${lat}" || -z "${lon}" ]]; then
	echo "No lat/lon found for task ${SLURM_ARRAY_TASK_ID} in ${LATLON_FILE}"
	exit 1
fi

echo "Starting CFM grid simulation for lat=${lat}, lon=${lon}"
/home/hpc/11/speersm/.conda/envs/CFM/bin/python /home/hpc/11/speersm/CFM_simulation/scripts/run_cfm.py --lat "$lat" --lon "$lon" --physrho "$PHYSRHO" --rcm "$RCM" --liquid "$LIQUID"

