import logging
import os
from typing import List

import numpy as np
import pandas as pd
import xarray as xr
import yaml
from abc import ABC, abstractmethod

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

logging.basicConfig(level=logging.INFO)


class ProcessBase(ABC):
    def __init__(self, borehole_lat: float, borehole_lon: float) -> None:
        """Base class for processing data at specified borehole coordinates. Subclasses should implement the process method to read in and process data, and save to the specified location.

        Args:
            borehole_lat (float): Latitude of borehole location.
            borehole_lon (float): Longitude of borehole location.
        """

        self._borehole_lat: float = borehole_lat
        self._borehole_lon: float = borehole_lon

        self._x_idx: int = 0
        self._y_idx: int = 0
        self._daily_xr: List[xr.Dataset] = None
        self._borehole_data: xr.Dataset = None

    def process(self, save_path: str) -> None:
        """
        Process the RCM dataset to extract data at the borehole location.

        Returns:
            xr.Dataset: MRCMAR data at the borehole location.
        """

        if os.path.exists(save_path):
            logging.info(
                f"Processed RCM data already exists at {save_path}. Skipping processing."
            )

        else:
            logging.info("Reading RCM data...")
            self._daily_xr = self._read_data()
            logging.info("...RCM data read successfully.")

            logging.info("Processing borehole data...")
            borehole_dataframes = [
                self._xr_to_input_dataframe(xr_data) for xr_data in self._daily_xr
            ]
            self._input_dataframe = pd.concat(borehole_dataframes)
            logging.info("...borehole data processed successfully.")

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self._input_dataframe.to_csv(save_path)
            logging.info(f"Borehole RCM data saved to {save_path}")

    @abstractmethod
    def _read_data(self) -> None:
        """Abstract method to read in data, to be implemented by subclasses."""
        pass

    @abstractmethod
    def _xr_to_input_dataframe(self, xr_data: xr.Dataset) -> pd.DataFrame:
        """Abstract method to convert xarray Dataset to pandas DataFrame, to be implemented by subclasses."""
        pass


class ProcessMAR(ProcessBase):
    def __init__(self, borehole_lat: float, borehole_lon: float) -> None:
        """Initialize with daily MAR dataset at specified borehole coordinates. Reads in .nc files from MAR data path specified in config.

        Args:
            borehole_lat (float): Latitude of borehole location.
            borehole_lon (float): Longitude of borehole location.
        """

        self._RCM_name: str = "MAR"
        self._save_path: str = config["force_data_save_path_pattern"].format(
            CFM_data_path=config["CFM_data_path"],
            rcm_name=self._RCM_name,
            borehole_lat=borehole_lat,
            borehole_lon=borehole_lon,
            start_year=config["start_year"],
            end_year=config["end_year"],
        )

        super().__init__(borehole_lat, borehole_lon)

    def process(self) -> None:
        """
        Process the MAR dataset to extract data at the borehole location.

        Returns:
            xr.Dataset: MAR data at the borehole location.
        """

        print(self._save_path)
        super().process(self._save_path)

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

        datasets = [xr.open_dataset(file, engine="h5netcdf") for file in year_files]

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

        # get indices of closest grid point to borehole
        lat_diff = np.abs(xr_data["LAT"] - self._borehole_lat)
        lon_diff = np.abs(xr_data["LON"] - self._borehole_lon)
        distance = np.sqrt(lat_diff**2 + lon_diff**2)
        y_idx, x_idx = np.unravel_index(distance.argmin(), distance.shape)

        # find coordinate names for X/Y (prefer MAR defaults, fallback to X/Y)
        x_coord_candidates = ["X18_215", "X"]
        y_coord_candidates = ["Y15_176", "Y"]
        x_coord = next(
            (name for name in x_coord_candidates if name in xr_data.coords), None
        )
        y_coord = next(
            (name for name in y_coord_candidates if name in xr_data.coords), None
        )
        if x_coord is None or y_coord is None:
            raise ValueError(
                f"Could not find appropriate X/Y coordinate names. Found coords: {list(xr_data.coords)}"
            )
        logging.info(
            "Using coordinates: %s for x and %s for y for year %s",
            x_coord,
            y_coord,
            xr_data["TIME"].dt.year.values[0],
        )

        # find data at borehole location
        borehole_data = xr_data.isel(**{y_coord: y_idx, x_coord: x_idx})

        # drop everything not in correct sector
        borehole_data = borehole_data.sel(SECTOR=config["sector"])

        # convert to dataframe, filtering for valid data variables only
        mapping = config["MAR_to_CFM_column_map"]
        vars_to_include = list(mapping.keys())

        # drop any variables not in vars_to_include
        borehole_data = borehole_data.drop_vars(
            [var for var in borehole_data.data_vars if var not in vars_to_include]
        )

        # convert to dataframe
        borehole_df = borehole_data.to_dataframe().reset_index()

        # drop everything apart from outlay 0.0 (surface layer)
        borehole_df = borehole_df[borehole_df["OUTLAY"] == 0.0]

        # rename columns to match CFM input column names
        borehole_df.rename(columns=mapping, inplace=True)
        borehole_df.set_index("TIME", inplace=True)

        # drop unneeded columns - should just be coordinates now
        borehole_df = borehole_df[list(mapping.values())]

        # convert temperature to Kelvin
        borehole_df["TSKIN"] = borehole_df["TSKIN"] + 273.15
        borehole_df["T2m"] = borehole_df["T2m"] + 273.15

        # remove duplicate times
        borehole_df = borehole_df[~borehole_df.index.duplicated(keep="first")]

        return borehole_df
