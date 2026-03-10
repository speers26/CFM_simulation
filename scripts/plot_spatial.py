"""Script to plot spatial maps of variables from the RCM simulations, typically restricted to AIS peninsula.

Usage:
    - plot_spatial.py
"""

from plot import SpatialPlotter
import yaml
import logging

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    mar_variables = config["MAR_to_CFM_column_map"].keys()
    racmo_variables = config["RACMO_to_CFM_column_map"].keys()

    # faster to plot each variable separately, as this avoids having to load in all the data for all variables at once (which can be very large and cause memory issues)
    for var in racmo_variables:
        logging.info(f"Plotting RACMO variable: {var}")
        SpatialPlotter(rcm_name="RACMO", variables=[var], plot_type="mean").plot()
    for var in mar_variables:
        logging.info(f"Plotting MAR variable: {var}")
        SpatialPlotter(rcm_name="MAR", variables=[var], plot_type="mean").plot()
