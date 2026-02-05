#!/bin/bash

# Define arrays of latitude/longitude pairs (same index = same location)
LATITUDES=(-66.403 -66.588 -67.000 -67.444 -67.500)
LONGITUDES=(-63.376 -63.212 -61.486 -64.953 -63.336)
PHYSRHO_VALUES=("HLdynamic" "GSFC2020" "Crocus")

# Function to run a single CFM plotting script
run_cfm_plot() {
    local lat=$1
    local lon=$2
    shift 2
    local physrho_values=("$@")

    if python /home/speersm/luna/CPOM/speersm/CFM_simulation/scripts/plot_cfm.py \
        --lat "$lat" \
        --lon "$lon" \
        --physrhols "${physrho_values[@]}"; then
        echo "SUCCESS: lat=$lat, lon=$lon, physrho=${physrho_values[*]}"
    else
        echo "FAILED: lat=$lat, lon=$lon, physrho=${physrho_values[*]}"
    fi
}

# loop over all latitude/longitude pairs, using all physrho values for each location
for i in "${!LATITUDES[@]}"; do
    LAT=${LATITUDES[$i]}
    LON=${LONGITUDES[$i]}
    run_cfm_plot "$LAT" "$LON" "${PHYSRHO_VALUES[@]}"
done
