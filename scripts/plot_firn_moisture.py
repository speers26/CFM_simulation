""" This script loads in either MAR or RACMO forcing data for the entire AIS, over the entire time period 1979-2024. We take the yearly sums of melt, and average these yearly sums to get a single 
spatial map of how 'wet' firn is across the AIS. We then plot this spatial map of 'wetness' for the entire AIS, and overlay the locations of the boreholes to see how wet the firn is at each borehole location.

Usage:
    python plot_firn_moisture.py

"""

import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import yaml
from typing import Dict, Tuple
import logging 

logging.basicConfig(level=logging.INFO)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":

    borehole_sites: Dict[str, Tuple[float, float]] = config["borehole_sites"]
    rcm_name: str = "MAR" # config["rcm_name"]

    # Load the RCM data for the entire AIS over the entire time period
    # to save memory, we will load in the data for each time chunk, calculate the yearly sums of melt, and then add to a running total of the yearly sums of melt for the entire time period

    melt_ds: xr.Dataset = None
    rcm_file_pattern: Dict[str, str] = {"MAR": "MARv3.14.3-27.5km-daily-ERA5-{year}.nc"}
    melt_name: Dict[str, str] = {"MAR": "ME"}  # variable name for melt in the RCM data
    time_name: Dict[str, str] = {"MAR": "TIME"}

    for year in range(config["start_year"], config["end_year"] + 1):
        rcm_file = rcm_file_pattern[rcm_name].format(year=year)
        rcm_data = xr.open_dataset(f"{config['MAR_data_path']}/{rcm_file}")
        rcm_data = rcm_data.sel(SECTOR=config["sector"])

        # Aggregate daily melt to a single annual total per grid cell.
        rcm_data[time_name[rcm_name]] = pd.to_datetime(rcm_data[time_name[rcm_name]].values)
        melt_yearly_sum = rcm_data[melt_name[rcm_name]].resample({time_name[rcm_name]: '1YE'}).sum()
        melt_yearly_sum = melt_yearly_sum.sum(dim=time_name[rcm_name])
        if time_name[rcm_name] in melt_yearly_sum.coords:
            melt_yearly_sum = melt_yearly_sum.drop_vars(time_name[rcm_name])

        if melt_ds is None:
            melt_ds = xr.Dataset({'melt_sum': melt_yearly_sum})
        else:
            melt_ds['melt_sum'] = melt_ds['melt_sum'] + melt_yearly_sum

        melt_ds['melt_avg'] = melt_ds['melt_sum'] / (config["end_year"] - config["start_year"] + 1)

        logging.info(f"Loaded and processed RCM data for year {year}")

    melt_ds["melt_avg"].plot()
    plt.savefig(f"{config['CFM_data_path']}/cfm_figures/melt_maps/melt_avg_{rcm_name}_{config['start_year']}_{config['end_year']}.png")