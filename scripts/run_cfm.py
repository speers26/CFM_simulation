"""
Reads in and processes MAR forcing data at specified borehole location, then saves to
processed data directory as pandas dataframe. Borehole location, dataframe column names, and save location
are specified in config file.

Then runs the CFM model using the processed forcing data and configuration from config file. Saves CFM output in 
location specified in config file. Also saves the CFM configuration used for the run as a JSON file in the output directory.

Usage:
    python run_cfm.py

"""

from force.process import ProcessMAR
from sim.run import CFMRun
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":
    ProcessMAR().process()
    CFMRun().run()
