from plot import plot_larsen_c_melt
from typing import Dict, Tuple
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":
    borehole_sites: Dict[str, Tuple[float, float]] = config["borehole_sites"]

    plot_larsen_c_melt(
        rcm_name="mar",
        lat_name="LAT",
        lon_name="LON",
        borehole_sites=borehole_sites,
    )

    plot_larsen_c_melt(
        rcm_name="racmo",
        lat_name="lat",
        lon_name="lon",
        borehole_sites=borehole_sites,
    )
