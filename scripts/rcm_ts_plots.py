"""
Script to generate plots of time series for MAR and RACMO forcing data at specified borehole sites. The script will:
- Load the MAR and RACMO forcing data for each borehole site from the processed csv
- Generate time series plots of the forcing variables (e.g., temperature, accumulation) for each site and each RCM. The plots will show the temporal variability in the forcing data at the borehole locations.
- Overlay the time series for MAR and RACMO on the same plot for each variable to compare the two RCMs at each site.
The resulting plots will be saved to the specified figure path.

"""

import os

import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Tuple

import logging
import yaml

logging.basicConfig(level=logging.INFO)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":
    borehole_sites: Dict[str, Tuple[float, float]] = {
        "CI-0": (-66.403, -63.376),
        "CI-22": (-66.588, -63.212),
        "CI-120": (-67.000, -61.486),
        "WI-0": (-67.444, -64.953),
        "WI-70": (-67.500, -63.336),
    }

    mar_data_dict: Dict[str, pd.DataFrame] = {}
    racmo_data_dict: Dict[str, pd.DataFrame] = {}

    for site, (lat, lon) in borehole_sites.items():
        # Load MAR data for this site
        mar_data_path = f"{config['CFM_data_path']}/cfm_input/MAR_{lat}_{lon}_{config['start_year']}_{config['end_year']}.csv"
        mar_data_dict[site] = pd.read_csv(mar_data_path)

        # Load RACMO data for this site
        racmo_data_path = f"{config['CFM_data_path']}/cfm_input/RACMO_{lat}_{lon}_{config['start_year']}_{config['end_year']}.csv"
        racmo_data_dict[site] = pd.read_csv(racmo_data_path)

    save_dir = f"{config['CFM_data_path']}/cfm_figures/rcm_comp"
    os.makedirs(save_dir, exist_ok=True)

    # Generate time series plots for each site and variable
    for site in borehole_sites.keys():
        mar_data = mar_data_dict[site]
        racmo_data = racmo_data_dict[site]

        # Example variables to plot (these should match the columns in your data)
        variables_to_plot = mar_data.columns.difference(
            ["TIME"]
        )  # Assuming 'TIME' is the time column

        for var in variables_to_plot:
            plt.figure(figsize=(10, 6))
            plt.plot(
                mar_data[var], label="MAR", color="blue", linestyle="--", alpha=0.5
            )
            plt.plot(
                # only plot first half of racmo data
                racmo_data[var],
                label="RACMO",
                color="orange",
                linestyle="--",
                alpha=0.5,
            )
            plt.title(f"{var.capitalize()} Time Series at {site}")
            plt.xlabel("Time")
            plt.ylabel(var.capitalize())
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.savefig(f"{save_dir}/{site}_{var}_timeseries.png")
            plt.close()

            logging.info(
                f"Saved time series plot for {var} at {site} to {save_dir}/{site}_{var}_timeseries.png"
            )

        # also plot variables against each other and get correlation coefficient
        for var in variables_to_plot:
            correlation = mar_data[var].corr(racmo_data[var])

            plt.figure(figsize=(10, 6))
            plt.scatter(
                mar_data[var],
                racmo_data[var],
                label="MAR vs RACMO",
                color="purple",
                alpha=0.5,
            )
            plt.title(
                f"{var.capitalize()} Scatter Plot at {site} (Correlation: {correlation:.2f})"
            )
            plt.xlabel("MAR " + var.capitalize())
            plt.ylabel("RACMO " + var.capitalize())
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.savefig(f"{save_dir}/{site}_{var}_scatter.png")
            plt.close()

            logging.info(
                f"Saved scatter plot for {var} at {site} to {save_dir}/{site}_{var}_scatter.png with correlation coefficient: {correlation:.2f}"
            )
