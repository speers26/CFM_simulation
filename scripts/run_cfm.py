"""
Reads in and processes MAR forcing data at specified borehole location, then saves to
processed data directory as pandas dataframe. Borehole location, dataframe column names, and save location
are specified in config file.

Then runs the CFM model using the processed forcing data and configuration from config file. Saves CFM output in
location specified in config file. Also saves the CFM configuration used for the run as a JSON file in the output directory.

Usage:
    python run_cfm.py
    python run_cfm.py --lat <latitude> --lon <longitude> --physrho <physrho_value>

"""

from force.process import ProcessMAR
from sim.run import CFMRun
import yaml
import argparse
import logging

logging.basicConfig(level=logging.INFO)

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run CFM simulation with optional command line arguments"
    )
    parser.add_argument("--lat", type=float, help="Borehole latitude")
    parser.add_argument("--lon", type=float, help="Borehole longitude")
    parser.add_argument("--physrho", type=str, help="Physical densification scheme")

    args = parser.parse_args()

    if args.lat is not None and args.lon is not None and args.physrho is not None:
        config["borehole_lat"] = args.lat
        config["borehole_lon"] = args.lon
        config["physrho"] = args.physrho
        logging.info(
            f"Using command line arguments: lat={config['borehole_lat']}, lon={config['borehole_lon']}, physrho={config['physrho']}"
        )
    else:
        logging.info("Using borehole location and physrho from config.yaml")

    ProcessMAR().process()
    CFMRun().run()
