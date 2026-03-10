import pandas as pd

if __name__ == "__main__":
    site_names = ["J108", "J208", "J409"]
    path = "/home/speersm/luna/CPOM/speersm/in_situ"

    # load in from txt files
    for site in site_names:
        in_situ_path = f"{path}/{site}_density.txt"
        in_situ_data = pd.read_csv(
            in_situ_path, delim_whitespace=True, header=None, names=["Uncertainty", "Density", "Depth"]
        )
        in_situ_data = in_situ_data[["Depth", "Density"]]
        in_situ_data["Depth"] = in_situ_data["Depth"] * 0.01  # convert from mm to m
        in_situ_data["Density"] = in_situ_data["Density"] * 1000  # convert from g/cm^3 to kg/m^3
        in_situ_data.to_csv(f"{path}/{site}_depth-density.csv", index=False)
