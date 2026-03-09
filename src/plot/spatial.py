import logging
import os
from typing import List, Literal

import matplotlib.pyplot as plt
import xarray as xr
import yaml

from force import ProcessMAR, ProcessRACMO

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


class SpatialPlotter:
    """Class to plot spatial maps of the average yearly melt across AIS peninsula for MAR and RACMO"""

    def __init__(self, rcm_name: Literal["MAR", "RACMO"], variables: List[str], plot_type: str) -> None:
        """Initializes the PlotSpatial class.

        Args:
            rcm_name (Literal["MAR", "RACMO"]): name of the RCM to plot melt for - either 'MAR' or 'RACMO'
            variables (List[str]): list of variable names to plot
            plot_type (str): type of plot to create (e.g., "mean", "max", "min", or a time point)
        """

        self.rcm_name = rcm_name
        self.variables = variables

        self.processor = {"MAR": ProcessMAR, "RACMO": ProcessRACMO}[rcm_name]
        self.time_name: str = {"MAR": "TIME", "RACMO": "time"}[rcm_name]
        self.lat_name: str = {"MAR": "LAT", "RACMO": "lat"}[rcm_name]
        self.lon_name: str = {"MAR": "LON", "RACMO": "lon"}[rcm_name]
        self.plot_type: str = plot_type

        self.save_dir: str = f"{config['CFM_data_path']}/cfm_figures/spatial_maps"
        os.makedirs(self.save_dir, exist_ok=True)

    def plot(self) -> None:
        """Plots the spatial map of the specified variable(s) for the specified RCM and plot type. This method will
        read in the data, aggregate it according to the specified plot type, and then plot the spatial map.
        The resulting plot will be saved to the specified directory.
        """

        logging.info("Reading in data...")
        self._read_data()
        logging.info("...Data read.")

        logging.info("Aggregating data...")
        self._aggregate_data()
        logging.info("...Data aggregated.")

        logging.info("Plotting spatial map...")
        self._plot_spatial_map()
        logging.info("...Spatial map plotted.")

    def _read_data(self) -> None:
        """Reads in the data for the specified RCM and variables, and concatenates it into a single xarray Dataset."""

        # initialise the processor class to read in the data
        # can use generic borehole location, as this class is just for plotting spatial maps of melt across the AIS
        # peninsula, so doesn't need specific borehole location
        processor = self.processor(borehole_lat=0.0, borehole_lon=0.0)

        # use the processer to read in data
        if self.rcm_name == "RACMO":
            processor._var_to_read = self.variables  # do this to speed up reading for racmo data
        # use the processor to read in data
        ds = processor._read_data()
        ds = xr.concat(ds, dim=self.time_name)

        # only keep the variables we want to plot
        self.ds = ds[self.variables]
        self.ds.compute()

    def _aggregate_data(self) -> None:
        """Aggregates the data according to the specified plot type (e.g., "mean", "max", "min", or a time point)."""

        if self.plot_type == "mean":
            self.ds = self.ds.mean(dim=self.time_name)
        elif self.plot_type == "max":
            self.ds = self.ds.max(dim=self.time_name)
        elif self.plot_type == "min":
            self.ds = self.ds.min(dim=self.time_name)
        else:
            # assume plot_type is a time point, so select the data for that time point
            self.ds = self.ds.sel({self.time_name: self.plot_type})

    def _plot_spatial_map(self) -> None:
        """Plots the spatial map of the specified variable(s) for the specified RCM and plot type."""

        for var in self.variables:
            plt.figure(figsize=(10, 8))
            self.ds[var].plot()
            plt.title(f"{self.rcm_name} {var} ({self.plot_type})")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.savefig(f"{self.save_dir}/{self.rcm_name}_{var}_{self.plot_type}.png")
            plt.close()
