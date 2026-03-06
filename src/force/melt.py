"""Classes which find the average yearly total melt across the AIS, for specified RCM"""

import logging

import xarray as xr
import yaml

from .process import ProcessMAR

logging.basicConfig(level=logging.INFO)
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


class MeltMar(ProcessMAR):
    """Class to find the average yearly total melt across the AIS for MAR

    Inherits from ProcessMar so that it can use the _read_data method.
    """

    def __init__(self, borehole_lat: float = 0.0, borehole_lon: float = 0.0):
        """Initialise with generic borehole_lat and borehole_lon. This class calculates melt over entire AIS, so doesn't need borehole location.

        Args:
            borehole_lat (float, optional): borehole location latitude (not needed). Defaults to 0.0 as a placeholder.
            borehole_lon (float, optional): borehole location longitude (not needed). Defaults to 0.0 as a placeholder.
        """
        super().__init__(borehole_lat, borehole_lon)

        self._save_location: str = (
            f"{config['CFM_data_path']}/melt_maps/mar_avg_yearly_melt_map.nc"
        )

    def get_melt_map(self):
        """Get the average yearly total melt across the AIS for MAR. This method will load in the MAR data for the entire AIS, calculate the yearly sums of melt, and then average these yearly sums to get a single spatial map of how 'wet' firn is across the AIS.

        Returns:
            xr.DataArray: A spatial map of the average yearly total melt across the AIS.
        """

        logging.info(
            "Reading in MAR data for the entire AIS over the entire time period..."
        )
        # Load the MAR data for the entire AIS over the entire time period
        mar_ds = self._read_data()
        logging.info("MAR data loaded successfully.")

        logging.info("Calculating the average yearly total melt across the AIS...")
        # joint list of xrarray together
        mar_ds = xr.concat(mar_ds, dim="TIME")

        # Calculate the yearly sums of melt
        mar_ds["year"] = mar_ds["TIME"].dt.year
        yearly_melt = mar_ds.groupby("year").sum(dim="TIME")["ME"]

        # Average these yearly sums to get a single spatial map of how 'wet' firn is across the AIS
        avg_yearly_melt = yearly_melt.mean(dim="year")
        logging.info("Average yearly total melt calculated successfully.")

        # save the average yearly melt map to a netcdf file
        avg_yearly_melt.to_netcdf(self._save_location)
        logging.info(f"Average yearly total melt saved to {self._save_location}")

        return avg_yearly_melt
