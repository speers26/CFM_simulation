"""This script loads in either MAR or RACMO forcing data for the entire AIS, over the entire time period 1979-2024. We take the yearly sums of melt, and average these yearly sums to get a single
spatial map of how 'wet' firn is across the AIS. We then plot this spatial map of 'wetness' for the entire AIS, and overlay the locations of the boreholes to see how wet the firn is at each borehole location.

Usage:
    python plot_firn_moisture.py

"""

# TODO script needs changing to read in melt maps that have already been calculated by the MeltMAR and MeltRACMO classes,
# rather than re-calculating the melt maps from the raw RCM data.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import yaml
from typing import Dict, Tuple
import logging
import os

logging.basicConfig(level=logging.INFO)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":
    borehole_sites: Dict[str, Tuple[float, float]] = config["borehole_sites"]
    rcm_name: str = config["rcm_name"]

    # Load the RCM data for the entire AIS over the entire time period
    # to save memory, we will load in the data for each time chunk, calculate the yearly sums of melt, and then add to a running total of the yearly sums of melt for the entire time period

    melt_ds: xr.Dataset = None
    rcm_file_pattern: Dict[str, str] = {
        "MAR": "MARv3.14.3-27.5km-daily-ERA5-",
        "RACMO": "mltgl_ANT-12_ERA5_evaluation_r1i1p1f1_UU-IMAU_RACMO24P-NN_v1-r1_day_",
    }
    melt_name: Dict[str, str] = {
        "MAR": "ME",
        "RACMO": "mltgl",
    }  # variable name for melt in the RCM data
    time_name: Dict[str, str] = {
        "MAR": "TIME",
        "RACMO": "time",
    }  # variable name for time in the RCM data
    lat_name: Dict[str, str] = {
        "MAR": "LAT",
        "RACMO": "lat",
    }  # variable name for latitude in the RCM data
    lon_name: Dict[str, str] = {
        "MAR": "LON",
        "RACMO": "lon",
    }  # variable name for longitude in the RCM data

    for year in range(config["start_year"], config["end_year"] + 1):
        # find files in directory matching the pattern for this year
        rcm_files = [
            f
            for f in os.listdir(config[f"{rcm_name}_data_path"])
            if f.startswith(f"{rcm_file_pattern[rcm_name]}{year}")
        ]
        if len(rcm_files) > 1:
            logging.warning(
                f"Multiple files found for year {year} in {rcm_name} data directory. Check file reading pattern for rcm: {rcm_name}"
            )

        rcm_data = xr.open_dataset(f"{config[f'{rcm_name}_data_path']}/{rcm_files[0]}")
        if rcm_name == "MAR":
            rcm_data = rcm_data.sel(SECTOR=config["sector"])

        # restrict rcm_data to larsen C - find index ranges for faster slicing
        lat_mask = (rcm_data[lat_name[rcm_name]] >= config["larsenC_box"]["lat_min"]) & (
            rcm_data[lat_name[rcm_name]] <= config["larsenC_box"]["lat_max"]
        )
        lon_mask = (rcm_data[lon_name[rcm_name]] >= config["larsenC_box"]["lon_min"]) & (
            rcm_data[lon_name[rcm_name]] <= config["larsenC_box"]["lon_max"]
        )
        combined_mask = lat_mask & lon_mask

        # Find the grid dimension names
        y_dim = [d for d in rcm_data.dims if d.startswith("Y")][0]
        x_dim = [d for d in rcm_data.dims if d.startswith("X")][0]

        # Get the index ranges where the mask is True
        y_indices = combined_mask.any(dim=x_dim).values.nonzero()[0]
        x_indices = combined_mask.any(dim=y_dim).values.nonzero()[0]

        if len(y_indices) > 0 and len(x_indices) > 0:
            rcm_data = rcm_data.isel(
                {
                    y_dim: slice(y_indices.min(), y_indices.max() + 1),
                    x_dim: slice(x_indices.min(), x_indices.max() + 1),
                }
            )

        # Aggregate daily melt to a single annual total per grid cell.
        rcm_data[time_name[rcm_name]] = pd.to_datetime(rcm_data[time_name[rcm_name]].values)
        melt_yearly_sum = rcm_data[melt_name[rcm_name]].resample({time_name[rcm_name]: "1YE"}).sum()
        melt_yearly_sum = melt_yearly_sum.sum(dim=time_name[rcm_name])
        if time_name[rcm_name] in melt_yearly_sum.coords:
            melt_yearly_sum = melt_yearly_sum.drop_vars(time_name[rcm_name])

        if melt_ds is None:
            melt_ds = xr.Dataset({"melt_sum": melt_yearly_sum})
        else:
            melt_ds["melt_sum"] = melt_ds["melt_sum"] + melt_yearly_sum

        melt_ds["melt_avg"] = melt_ds["melt_sum"] / (config["end_year"] - config["start_year"] + 1)

        logging.info(f"Loaded and processed RCM data for year {year}")

    # Get coordinates of site locations in the RCM grid and plot melt map with site locations overlaid
    lat_mask = (rcm_data[lat_name[rcm_name]] >= config["larsenC_box"]["lat_min"]) & (
        rcm_data[lat_name[rcm_name]] <= config["larsenC_box"]["lat_max"]
    )
    lon_mask = (rcm_data[lon_name[rcm_name]] >= config["larsenC_box"]["lon_min"]) & (
        rcm_data[lon_name[rcm_name]] <= config["larsenC_box"]["lon_max"]
    )
    combined_mask = lat_mask & lon_mask
    y_dim = [d for d in rcm_data.dims if d.startswith("Y")][0]
    x_dim = [d for d in rcm_data.dims if d.startswith("X")][0]
    y_indices = combined_mask.any(dim=x_dim).values.nonzero()[0]
    x_indices = combined_mask.any(dim=y_dim).values.nonzero()[0]
    if len(y_indices) > 0 and len(x_indices) > 0:
        rcm_data = rcm_data.isel(
            {
                y_dim: slice(y_indices.min(), y_indices.max() + 1),
                x_dim: slice(x_indices.min(), x_indices.max() + 1),
            }
        )

    melt_ds["melt_avg"].plot(cmap="Blues", cbar_kwargs={"label": "Average Yearly Melt (mm w.e.)"})
    # add points showing borehole locations
    for site, (lat, lon) in borehole_sites.items():
        # Find nearest grid point
        lat_diff = np.abs(rcm_data["LAT"] - lat)
        lon_diff = np.abs(rcm_data["LON"] - lon)
        distance = np.sqrt(lat_diff**2 + lon_diff**2)
        y_idx, x_idx = np.unravel_index(distance.argmin().values, distance.shape)

        # Get the grid coordinates (X18_215, Y15_176)
        x_coord = rcm_data[x_dim].values[x_idx]
        y_coord = rcm_data[y_dim].values[y_idx]

        plt.plot(x_coord, y_coord, marker="o", markersize=5, label=site)
    plt.legend()
    plt.title(f"Average Yearly Melt from {rcm_name} ({config['start_year']} - {config['end_year']})")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.savefig(
        f"{config['CFM_data_path']}/cfm_figures/melt_maps/melt_avg_{rcm_name}_{config['start_year']}_{config['end_year']}.png"
    )
