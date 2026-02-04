import os
import matplotlib.pyplot as plt
import xarray as xr
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":

    phys_rho = "Crocus"
    lat, lon = -66.403, -63.376
    output_path = f"{config['CFM_data_path']}/cfm_output/CFMoutput_{lat}_{lon}_{phys_rho}"
    figure_path = f"{config['CFM_data_path']}/cfm_figures/CFMoutput_{lat}_{lon}_{phys_rho}"
    os.makedirs(figure_path, exist_ok=True)
    results_dict = {}

    with xr.open_dataset(f"{output_path}/CFMresults.hdf5", engine="h5netcdf") as ds:
        results_dict['model_time_matrix'] = ds['density'][1:,0] # the first column of the density data is the model time step for matrix outputs ('rho','Tz','LWC','age'), which will be different than others if "truncate_outputs" is true.
        results_dict['model_time_vector'] = ds['DIP'][1:,0] # the first column of the DIP data is the model time step for vector outputs (all time steps).
        results_dict['depth'] = ds['depth'][1:] # Put the depth data into a numpy array
        results_dict['density'] = ds['density'][1:,1:] # Put the density data into an array
        results_dict['temperature'] = ds['temperature'][1:,1:]
        results_dict['DIP'] = ds['DIP'][1:,1:]
        ds.close()

    plt.figure(figsize=(6, 8))
    plt.plot(results_dict['density'][0, :], results_dict['depth'])
    plt.xlabel('Density (kg/m³)')
    plt.ylabel('Depth (m)')
    plt.grid()
    plt.gca().invert_yaxis()
    plt.savefig(f"{figure_path}/density_profile_{lat}_{lon}_{phys_rho}.png")