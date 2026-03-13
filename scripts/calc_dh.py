import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt


def read_output_data(file_path):
    """
    Reads the output data from a NetCDF file and returns it as an xarray Dataset.

    Parameters:
    file_path (str): The path to the NetCDF file containing the output data.

    Returns:
    dict: A dictionary containing the model time matrix, model time vector, depth, density, temperature, and DIP.
    """

    with xr.open_dataset(file_path, engine="h5netcdf", phony_dims="sort") as ds:
        results_dict = {
            "model_time_matrix": ds["density"][1:, 0],
            "model_time_vector": ds["DIP"][1:, 0],
            "depth": ds["depth"][1:],
            "density": ds["density"][1:, 1:],
            "temperature": ds["temperature"][1:, 1:],
            "DIP": ds["DIP"][1:, 1:],
            # "compaction": ds["compaction"][1:, 1:],
            # dHOut from CFM update_dH: column index 2 in full DIP array,
            # units are meters of surface-height change per model step.
            "dH_step": ds["DIP"][1:, 2],
        }

    return results_dict


if __name__ == "__main__":
    lat_lon_pairs = [
        ("-66.403", "-63.376"),
        ("-66.588", "-63.212"),
        ("-67.000", "-61.486"),
        ("-67.444", "-64.953"),
        ("-67.500", "-63.336"),
    ]

    for lat, lon in lat_lon_pairs:
        input_path = f"/home/speersm/luna/CPOM/speersm/CFM_data/cfm_input/MAR_{float(lat)}_{float(lon)}_1979_2024.csv"
        output_path = f"/home/speersm/luna/CPOM/speersm/CFM_data/cfm_output/CFMoutput_{lat}_{lon}_1979_2024_GSFC2020_bucket_MAR/CFMresults.hdf5"

        input_df = pd.read_csv(input_path, parse_dates=["TIME"])
        results_dict = read_output_data(output_path)

        # only keep input from 1980 onwards
        input_df = input_df[input_df["TIME"] >= pd.Timestamp("1980-01-01")]

        # Align lengths so time and DIP-derived series are paired safely.
        dH_step = results_dict["dH_step"].values

        # plot
        plt.figure(figsize=(10, 6))
        plt.plot(input_df["TIME"], dH_step, label="dh/dt")
        plt.xlabel("Time")
        plt.ylabel("dh/dt (m/day)")
        plt.title("Rate of change of ice thickness (dh/dt) over time")
        plt.legend()
        plt.grid()
        plt.savefig(f"dh_dt_time_series_{lat}_{lon}.png", dpi=300)

        # save time series data to CSV
        output_df = pd.DataFrame({"TIME": input_df["TIME"], "dh_dt": dH_step})
        output_df.to_csv(f"dh_dt_time_series_{lat}_{lon}.csv", index=False)
