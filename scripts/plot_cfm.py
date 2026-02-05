"""Script to plot the results of the CFM simulations for different physical densification schemes. The script loads the CFM output data, creates plots for density profiles, DIP time series, and change in firn thickness over time, and saves the figures to the specified figure paths. The script can be run with command line arguments for borehole latitude, longitude, and physical densification schemes, or it can use the values specified in the config.yaml file if no command line arguments are provided.

Usage:
    python plot_cfm.py --lat 66.403 --lon 63.376 --physrhols GSFC2020 Crocus
"""

import argparse
import logging

import yaml

from plot.results import ResultsPlotter

logging.basicConfig(level=logging.INFO)

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run CFM plotting with optional command line arguments"
    )
    parser.add_argument("--lat", type=float, help="Borehole latitude")
    parser.add_argument("--lon", type=float, help="Borehole longitude")
    parser.add_argument(
        "--physrhols",
        nargs="+",
        type=str,
        help="List of physical densification schemes",
    )

    args = parser.parse_args()
    if args.lat is not None and args.lon is not None and args.physrhols is not None:
        logging.info(
            f"Using command line arguments: lat={args.lat}, lon={args.lon}, physrho={args.physrhols}"
        )
        lat = args.lat
        lon = args.lon
        phys_rho = args.physrhols
    else:
        lat = config["borehole_lat"]
        lon = config["borehole_lon"]
        phys_rho = list(config["cfm_config"]["physRho"])
        logging.info("Using borehole location and physrho from config.yaml")

    ResultsPlotter(lat, lon, phys_rho).plot()
