#!/bin/bash

# Define arrays of latitude/longitude pairs (same index = same location)
LATITUDES=(-66.403 -66.588 -67.000 -67.444 -67.500)
LONGITUDES=(-63.376 -63.212 -61.486 -64.953 -63.336)
PHYSRHO_VALUES=("HLdynamic" "GSFC2020" "Crocus")

# Counters for tracking results
TOTAL_RUNS=0
SUCCESSFUL_RUNS=0
FAILED_RUNS=0

# for logging individual runs
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="/home/speersm/luna/CPOM/speersm/CFM_simulation/logs"
mkdir -p "$LOG_DIR"

# for summary logging
exec > >(tee "$LOG_DIR/run_cfm_summary_${TIMESTAMP}.log") 2>&1

# Function to run a single CFM simulation
run_cfm_job() {
    local lat=$1
    local lon=$2
    local physrho=$3

    local log_file="$LOG_DIR/cfm_lat${lat}_lon${lon}_${physrho}_${TIMESTAMP}.log"

    echo "Running CFM for lat=$lat, lon=$lon, physrho=$physrho (logging to $log_file)"
    
    if python /home/speersm/luna/CPOM/speersm/CFM_simulation/scripts/run_cfm.py \
        --lat "$lat" \
        --lon "$lon" \
        --physrho "$physrho" \
        > "$log_file" 2>&1; then
        echo "SUCCESS: lat=$lat, lon=$lon, physrho=$physrho"
        ((SUCCESSFUL_RUNS++))
    else
        echo "FAILED: lat=$lat, lon=$lon, physrho=$physrho"
        ((FAILED_RUNS++))
    fi
}

# loop over all latitude/longitude pairs and physrho values
for i in "${!LATITUDES[@]}"; do
    LAT=${LATITUDES[$i]}
    LON=${LONGITUDES[$i]}
    for PHYSRHO in "${PHYSRHO_VALUES[@]}"; do
        ((TOTAL_RUNS++))
        run_cfm_job "$LAT" "$LON" "$PHYSRHO" || true
    done
done

# Print summary
echo "=================================="
echo "Execution Summary:"
echo "Total runs: $TOTAL_RUNS"
echo "Successful: $SUCCESSFUL_RUNS"
echo "Failed: $FAILED_RUNS"
echo "=================================="
