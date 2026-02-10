import matplotlib.pyplot as plt
from typing import Dict, Tuple
import xarray as xr
import pandas as pd
import numpy as np

import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":
    borehole_sites: Dict[str, Tuple[float, float]] = {
        "CI-0": (-66.403, -63.376),
        "CI-22": (-66.588, -63.212),
        "CI-120": (-67.000, -61.486),
        "WI-0": (-67.444, -64.953),
        "WI-70": (-67.500, -63.336),
    }

    physrho_values = [
        "GSFC2020",
        "HLdynamic",
        "Crocus",
        "Barnola1991",
        "Ligtenberg2011",
    ]
    start, end = 1979, 2024

    summer_2014 = [
        2014 + 11 / 12,
        2015 + 2 / 12,
    ]  # astrochronological summer of 2014 (December 2014 - February 2015)
    summer_2015 = [
        2015 + 11 / 12,
        2016 + 2 / 12,
    ]  # astrochronological summer of 2015 (December 2015 - February 2016)

    for site, (lat, lon) in borehole_sites.items():
        plt.figure(figsize=(6, 8))
        for physrho in physrho_values:
            # load simulation
            output_path = f"{config['CFM_data_path']}/cfm_output/CFMoutput_{lat}_{lon}_{start}_{end}_{physrho}/CFMresults.hdf5"
            with xr.open_dataset(output_path, engine="h5netcdf") as ds:
                results_dict = {
                    "model_time_matrix": ds["density"][1:, 0],
                    "model_time_vector": ds["DIP"][1:, 0],
                    "depth": ds["depth"][1:],
                    "density": ds["density"][1:, 1:],
                    "temperature": ds["temperature"][1:, 1:],
                    "DIP": ds["DIP"][1:, 1:],
                }

            # only keep data from astrochronological summers
            summer_2014_mask = (results_dict["model_time_vector"] >= summer_2014[0]) & (
                results_dict["model_time_vector"] <= summer_2014[1]
            )
            summer_2015_mask = (results_dict["model_time_vector"] >= summer_2015[0]) & (
                results_dict["model_time_vector"] <= summer_2015[1]
            )
            summer_mask = summer_2014_mask | summer_2015_mask

            # only keep density data from astrochronological summers
            density_summer = results_dict["density"][summer_mask, :]

            # load in in situ density data for this site
            in_situ_path = (
                f"/home/speersm/luna/CPOM/speersm/in_situ/{site}_depth-density.csv"
            )
            in_situ_data = pd.read_csv(in_situ_path)
            in_situ_data = in_situ_data.iloc[1:]

            # put in situ data on same depth grid as model output
            in_situ_depth = pd.to_numeric(in_situ_data["Depth"].values)
            in_situ_density = pd.to_numeric(in_situ_data["Density"].values)

            # interpolate in model data to in situ depth grid
            density_summer_interp = np.empty(
                (density_summer.shape[0], len(in_situ_depth))
            )
            for i in range(density_summer.shape[0]):
                density_summer_interp[i, :] = np.interp(
                    in_situ_depth, results_dict["depth"].values, density_summer[i, :]
                )

            # get rmse at each depth, averaging over time steps
            rmse = np.sqrt(
                np.mean((density_summer_interp - in_situ_density) ** 2, axis=0)
            )

            # get rmse as percentage of in situ density
            rmse_percent = rmse / in_situ_density * 100

            # plot rmse vs depth
            plt.plot(rmse_percent, in_situ_depth, label=f"{physrho}")
        plt.gca().invert_yaxis()
        plt.xlabel("RMSE (% of in situ density)")
        plt.ylabel("Depth (m)")
        plt.title(f"Density RMSE vs Depth for {site}")
        plt.legend()
        plt.grid()
        plt.xlim(0, 45)
        plt.savefig(
            f"/home/speersm/luna/CPOM/speersm/CFM_data/cfm_figures/errors/{site}_density_rmse.png"
        )
