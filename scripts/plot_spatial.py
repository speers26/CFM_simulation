"""Script to plot spatial maps of variables from the RCM simulations, typically restricted to AIS peninsula.

Usage:
    - plot_spatial.py
"""

from plot import SpatialPlotter
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":

    mar_variables = config["MAR_to_CFM_column_map"].keys()
    racmo_variables = config["RACMO_to_CFM_column_map"].keys()

    SpatialPlotter(rcm_name="MAR", variables=mar_variables, plot_type="mean").plot()
    SpatialPlotter(rcm_name="RACMO", variables=racmo_variables, plot_type="mean").plot()
