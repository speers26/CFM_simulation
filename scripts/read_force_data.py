"""
Reads in and processes MAR forcing data at specified borehole location, then saves to
processed data directory as pandas dataframe. Borehole location, dataframe column names, and save location
are specified in config file.

Usage: 
    python read_force_data.py

"""

from force.process import ProcessMAR
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":
    processor = ProcessMAR(config['borehole_lat'], config['borehole_lon'])
    borehole_MAR_data = processor.process()
