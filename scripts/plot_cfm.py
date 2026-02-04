import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import yaml
import argparse
import logging

logging.basicConfig(level=logging.INFO)

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run CFM plotting with optional command line arguments"
    )
    parser.add_argument("--lat", type=float, help="Borehole latitude")
    parser.add_argument("--lon", type=float, help="Borehole longitude")
    parser.add_argument("--physrho", type=str, help="Physical densification scheme")

    args = parser.parse_args()
    if args.lat is not None and args.lon is not None and args.physrho is not None:
        logging.info(
            f"Using command line arguments: lat={args.lat}, lon={args.lon}, physrho={args.physrho}"
        )
        lat = args.lat
        lon = args.lon
        phys_rho = args.physrho
    else:
        lat = config["borehole_lat"]
        lon = config["borehole_lon"]
        phys_rho = config["cfm_config"]["physRho"]
        logging.info("Using borehole location and physrho from config.yaml")

    ### below needs to be put into plotting class later ###

    output_path = (
        f"{config['CFM_data_path']}/cfm_output/CFMoutput_{lat}_{lon}_{phys_rho}"
    )
    figure_path = (
        f"{config['CFM_data_path']}/cfm_figures/figures_{lat}_{lon}_{phys_rho}"
    )
    os.makedirs(figure_path, exist_ok=True)
    results_dict = {}

    with xr.open_dataset(f"{output_path}/CFMresults.hdf5", engine="h5netcdf", phony_dims="sort") as ds:
        results_dict["model_time_matrix"] = ds["density"][
            1:, 0
        ]  # the first column of the density data is the model time step for matrix outputs ('rho','Tz','LWC','age'), which will be different than others if "truncate_outputs" is true.
        results_dict["model_time_vector"] = ds["DIP"][
            1:, 0
        ]  # the first column of the DIP data is the model time step for vector outputs (all time steps).
        results_dict["depth"] = ds["depth"][1:]  # Put the depth data into a numpy array
        results_dict["density"] = ds["density"][
            1:, 1:
        ]  # Put the density data into an array
        results_dict["temperature"] = ds["temperature"][1:, 1:]
        results_dict["DIP"] = ds["DIP"][1:, 1:]
        ds.close()

    # Plot density profiles
    plt.figure(figsize=(6, 8))
    n_lines = results_dict["density"].shape[0]
    colors = plt.cm.Reds(np.linspace(0.3, 1.0, n_lines))
    for i in range(n_lines):
        plt.plot(
            results_dict["density"][i, :],
            results_dict["depth"],
            linewidth=0.5,
            alpha=0.7,
            color=colors[i],
        )
    plt.xlabel("Density (kg/m³)")
    plt.ylabel("Depth (m)")
    plt.grid()
    plt.gca().invert_yaxis()
    plt.savefig(f"{figure_path}/density_profile_{lat}_{lon}_{phys_rho}.png")

    # plot DIP with time
    plt.figure(figsize=(10, 6))
    plt.plot(results_dict['model_time_vector'].values, results_dict['DIP'][:, 0])
    plt.xlabel("Model Time (years)")
    plt.ylabel("DIP (m)")
    plt.grid()
    plt.savefig(f"{figure_path}/DIP_time_{lat}_{lon}_{phys_rho}.png")

    # plot change in firn thickness over time
    dz = results_dict['depth'][:-1]-results_dict['depth'][1:]
    dz = np.mean(dz)

    close_off_dens = 830.0
    firn_mask = results_dict['density'] <= close_off_dens
    firn_thickness = np.sum(firn_mask * dz, axis=1)
    firn_delta = firn_thickness[1:] - firn_thickness[:-1]

    plt.figure(figsize=(10, 6))
    plt.plot(results_dict['model_time_vector'].values[1:], firn_delta)
    plt.xlabel("Model Time (years)")
    plt.ylabel("Change in Firn Thickness (m)")
    plt.grid()
    plt.savefig(f"{figure_path}/firn_thickness_change_{lat}_{lon}_{phys_rho}.png")