import numpy as np
import xarray as xr
from typing import Tuple

class ProcessMAR:

    def __init__(self, daily_MAR: xr.Dataset, borehole_lat: float, borehole_lon: float) -> None:
        '''Initialize with daily MAR dataset and borehole coordinates.
        
        Args:
            daily_MAR (xr.Dataset): Daily xarray MAR dataset with 'LAT' and 'LON' variables. 
            borehole_lat (float): Latitude of the borehole.
            borehole_lon (float): Longitude of the borehole.
        
        '''

        self.daily_MAR: xr.Dataset = daily_MAR
        self.borehole_lat: float = borehole_lat
        self.borehole_lon: float = borehole_lon

        self.y_idx, self.x_idx = self._find_nearest_grid_point()
        self.borehole_data = self._extract_borehole_data()

    def _find_nearest_grid_point(self) -> Tuple[int, int]:
        '''
        Find the nearest grid point indices in the MAR dataset to the borehole location.
        This allows us to extract data specific to the borehole location, using the coordinate system of MAR data.

        Returns:
            Tuple[int, int]: Indices (y_idx, x_idx) of the nearest grid
        point to the borehole location.

        '''
        lat_diff = np.abs(self.daily_MAR['LAT'] - self.borehole_lat)
        lon_diff = np.abs(self.daily_MAR['LON'] - self.borehole_lon)

        y_idx = lat_diff.argmin().item()
        x_idx = lon_diff.argmin().item()

        return y_idx, x_idx

    def _extract_borehole_data(self) -> xr.Dataset:
        '''
        Extract the MAR data at the borehole location using the identified grid indices.

        Returns:
            xr.Dataset: MAR data at the borehole location.
        '''
        borehole_data = self.daily_MAR.isel(Y15_176=self.y_idx, X18_215=self.x_idx)
        return borehole_data    
