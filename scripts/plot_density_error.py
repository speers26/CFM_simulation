"""
Working script for plotting simulated density profiles against in situ density profiles
could be integrated into src/plot/results.py if we decide to keep these plots

Usage:
    python density_error.py

Requires specification of which sites to plot in borehole_sites dictionary, which physical densification schemes
to plot in physrho_values list, and the RCM and melt scheme to use for loading the correct simulation output.

The script will
- load in situ density data for each site
- load the corresponding CFM simulation output for each physical densification scheme
- interpolate the model density to the in situ depth grid
- calculate the mean model density across all time steps in the austral summers of 2014 and 2015
- and plot the difference between the model and in situ density profiles with depth.

The resulting plots will be saved to the specified figure path.

"""

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

    rcm_name = "RACMO"
    melt_scheme = "bucket"

    summer_2014 = [
        2014 + 11 / 12,
        2015 + 2 / 12,
    ]  # astrochronological summer of 2014 (December 2014 - February 2015)
    summer_2015 = [
        2015 + 11 / 12,
        2016 + 2 / 12,
    ]  # astrochronological summer of 2015 (December 2015 - February 2016)

    for site, (lat, lon) in borehole_sites.items():
        # load in in situ density data for this site
        in_situ_path = (
            f"/home/speersm/luna/CPOM/speersm/in_situ/{site}_depth-density.csv"
        )
        in_situ_data = pd.read_csv(in_situ_path)
        in_situ_data = in_situ_data.iloc[1:]

        # put in situ data on same depth grid as model output
        in_situ_depth = pd.to_numeric(in_situ_data["Depth"].values)
        in_situ_density = pd.to_numeric(in_situ_data["Density"].values)
        plt.figure(figsize=(6, 8))
        # plt.plot(in_situ_density, in_situ_depth, label="In situ", color="k", linewidth=1)
        for physrho in physrho_values:
            # load simulation
            output_path = f"{config['CFM_data_path']}/cfm_output/CFMoutput_{lat}_{lon}_{start}_{end}_{physrho}_{melt_scheme}_{rcm_name}/CFMresults.hdf5"
            with xr.open_dataset(
                output_path, engine="h5netcdf", phony_dims="sort"
            ) as ds:
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

            # only keep model data from depths where we have in situ data
            depth_mask = (results_dict["depth"] >= in_situ_depth.min()) & (
                results_dict["depth"] <= in_situ_depth.max()
            )

            # interpolate in model data to in situ depth grid
            density_summer_interp = np.empty(
                (density_summer.shape[0], len(in_situ_depth))
            )
            for i in range(density_summer.shape[0]):
                density_summer_interp[i, :] = np.interp(
                    in_situ_depth,
                    results_dict["depth"].values[depth_mask],
                    density_summer[i, depth_mask],
                )

            # get mean model density at each depth across all model time steps in astrochronological summers
            density_summer_mean = np.mean(density_summer_interp, axis=0)
            density_summer_lower = np.percentile(density_summer_interp, 25, axis=0)
            density_summer_upper = np.percentile(density_summer_interp, 75, axis=0)

            # plot rmse vs depth
            plt.plot(
                density_summer_mean - in_situ_density,
                in_situ_depth,
                label=f"{physrho}",
                linestyle="--",
            )
            plt.fill_betweenx(
                in_situ_depth,
                density_summer_lower - in_situ_density,
                density_summer_upper - in_situ_density,
                alpha=0.3,
                color=plt.gca().lines[-1].get_color(),
            )
        # also plot in situ density profile for reference
        # add vertical line at 0 to indicate perfect agreement between model and in situ
        plt.axvline(0, color="k", linestyle=":")
        plt.gca().invert_yaxis()
        plt.xlabel("Density (kg/m³)")
        plt.ylabel("Depth (m)")
        plt.title(f"Density vs Depth (model difference) for {site}")
        plt.legend()
        plt.grid()
        plt.savefig(
            f"/home/speersm/luna/CPOM/speersm/CFM_data/cfm_figures/errors/{site}_diff_{melt_scheme}_{rcm_name}.png"
        )
