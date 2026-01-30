import logging
import os
from typing import List

import numpy as np
import pandas as pd
import xarray as xr
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

logging.basicConfig(level=logging.INFO)

class ProcessMAR:
    def __init__(self, borehole_lat: float, borehole_lon: float) -> None:
        """Initialize with daily MAR dataset and borehole coordinates. Reads in .nc files from MAR data path specified in config.

        Args:
            borehole_lat (float): Latitude of the borehole.
            borehole_lon (float): Longitude of the borehole.
        """

        self.borehole_lat: float = borehole_lat
        self.borehole_lon: float = borehole_lon
        self._save_path: str = f"{config['processed_data_path']}/MAR_{self.borehole_lat}_{self.borehole_lon}_{config['start_year']}_{config['end_year']}.csv"

        self._daily_xr: List[xr.Dataset] = None
        self._x_idx: int = None
        self._y_idx: int = None
        self._borehold_data: xr.Dataset = None

    def process(self) -> xr.Dataset:
        """
        Process the MAR dataset to extract data at the borehole location.

        Returns:
            xr.Dataset: MAR data at the borehole location.
        """

        logging.info("Reading MAR data...")
        self._daily_xr = self._read_data()
        logging.info("...MAR data read successfully.")

        logging.info("Processing borehole data...")
        borehole_dataframes = [
            self._xr_to_input_dataframe(xr_data) for xr_data in self._daily_xr
        ]
        self._input_dataframe = pd.concat(borehole_dataframes)
        logging.info("...borehole data processed successfully.")

        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        self._input_dataframe.to_csv(self._save_path)
        logging.info(f"Borehole MAR data saved to {self._save_path}")

    def _read_data(self) -> List[xr.Dataset]:
        """
        Read in the MAR .nc files from the specified data path in config.

        Returns:
            List[xr.Dataset]: List of xarray Datasets for each year of MAR data.
        """
        mar_data_path = config["MAR_data_path"]
        year_files = [
            f"{mar_data_path}/MARv3.14.3-27.5km-daily-ERA5-{year}.nc"
            for year in range(config["start_year"], config["end_year"] + 1)
        ]

        datasets = [xr.open_dataset(file) for file in year_files]

        return datasets

    def _xr_to_input_dataframe(self, xr_data: xr.Dataset) -> pd.DataFrame:
        """
        Extract daily data for borehole location, then convert the borehole MAR data to the pandas DataFrame needed for CFM input. Also only takes the sector specified in config.

        Args:
            xr_data (xr.Dataset): MAR data at the borehole location.
        Returns:
            pd.DataFrame: DataFrame containing MAR data at the borehole location, with columns named as required by CFM.
        """
        logging.info(f"Processing XR data at year {xr_data['TIME'].dt.year.values[0]}")

        # extract data at borehole location
        lat_diff = np.abs(xr_data["LAT"] - self.borehole_lat)
        lon_diff = np.abs(xr_data["LON"] - self.borehole_lon)
        distance = np.sqrt(lat_diff**2 + lon_diff**2)
        y_idx, x_idx = np.unravel_index(distance.argmin(), distance.shape)
        borehole_data = xr_data.isel(
            Y15_176=y_idx,
            X18_215=x_idx,
        )

        # convert to dataframe
        borehole_df = (
            borehole_data.sel(SECTOR=config["sector"]).to_dataframe().reset_index()
        )

        # rename columms to match CFM input column names
        mapping = config["MAR_to_CFM_column_map"]
        borehole_df.rename(columns=mapping, inplace=True)
        borehole_df.set_index("TIME", inplace=True)

        # drop unneeded columns
        borehole_df = borehole_df[list(mapping.values())]

        return borehole_df
