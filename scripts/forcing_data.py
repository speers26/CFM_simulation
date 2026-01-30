from force.process import ProcessMAR
import yaml
import xarray as xr

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":

    borehole_lat = -66.403
    borehole_lon = -63.212

    year_file = f"{config['MAR_data_path']}/MARv3.14.3-27.5km-daily-ERA5-1999.nc"
    daily_MAR = xr.open_dataset(year_file)

    processor = ProcessMAR(daily_MAR, borehole_lat, borehole_lon)
    borehole_MAR_data = processor.process()

    print(borehole_MAR_data.head())