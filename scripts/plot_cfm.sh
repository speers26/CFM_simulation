#!/bin/bash

# Define arrays of latitude/longitude pairs (same index = same location)
LATITUDES=(-66.403 -66.588 -67.000 -67.444 -67.500)
LONGITUDES=(-63.376 -63.212 -61.486 -64.953 -63.336)
PHYSRHO_VALUES=("HLdynamic" "GSFC2020" "Crocus")

# Function to run a single CFM plotting script
run_cfm_plot() {
    local lat=$1
    local lon=$2
    local physrho=$3

    if python /home/speersm/luna/CPOM/speersm/CFM_simulation/scripts/plot_cfm.py \
        --lat "$lat" \
        --lon "$lon" \
        --physrho "$physrho"; then
        echo "SUCCESS: lat=$lat, lon=$lon, physrho=$physrho"
    else
        echo "FAILED: lat=$lat, lon=$lon, physrho=$physrho"
    fi
}

# loop over all latitude/longitude pairs and physrho values
for i in "${!LATITUDES[@]}"; do
    LAT=${LATITUDES[$i]}
    LON=${LONGITUDES[$i]}
    for PHYSRHO in "${PHYSRHO_VALUES[@]}"; do
        ((TOTAL_RUNS++))
        run_cfm_plot "$LAT" "$LON" "$PHYSRHO" || true
    done
done
