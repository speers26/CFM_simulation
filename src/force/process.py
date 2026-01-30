import numpy as np
import xarray as xr
from typing import Tuple
import pandas as pd
import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

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

        self._x_idx: int = None
        self._y_idx: int = None
        self._borehold_data: xr.Dataset = None

    def process(self) -> xr.Dataset:
        '''
        Process the MAR dataset to extract data at the borehole location.

        Returns:
            xr.Dataset: MAR data at the borehole location.
        '''
        self._y_idx, self._x_idx = self._find_nearest_grid_point()
        self._borehole_data = self._extract_borehole_data()
        self._input_dataframe = self._input_to_dataframe()

        return self._input_dataframe

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
        distance = np.sqrt(lat_diff**2 + lon_diff**2)

        y_idx, x_idx = np.unravel_index(distance.argmin(), distance.shape)
    
        return y_idx, x_idx

    def _extract_borehole_data(self) -> xr.Dataset:
        '''
        Extract the MAR data at the borehole location using the identified grid indices.

        Returns:
            xr.Dataset: MAR data at the borehole location.
        '''
        borehole_data = self.daily_MAR.isel(Y15_176=self._y_idx, X18_215=self._x_idx, )

        return borehole_data    

    def _input_to_dataframe(self) -> pd.DataFrame:
        '''
        Convert the borehole MAR data to a the pandas DataFrame needed for CFM input. Also only takes the sector specified in config.

        Returns:
            pd.DataFrame: DataFrame containing MAR data at the borehole location, with columns named as required by CFM.
        '''
        df = self._borehole_data.sel(SECTOR=config['sector']).to_dataframe().reset_index()

        # rename columms to match CFM input column names
        mapping = config['MAR_to_CFM_column_map']
        df.rename(columns=mapping, inplace=True)
        df.set_index('TIME', inplace=True)

        # drop unneeded columns
        df = df[list(mapping.values())]

        return df