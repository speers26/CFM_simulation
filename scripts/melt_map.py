"""Script which gets maps of average yearly melt across AIC (or Larsen C), for RCM specified in config

Usage:
    - python melt_map.py

"""

from force.melt import MeltMAR, MeltRACMO
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":
    if config["rcm_name"] == "MAR":
        melt = MeltMAR()
    elif config["rcm_name"] == "RACMO":
        melt = MeltRACMO()
    else:
        raise ValueError(f"Invalid RCM name in config: {config['rcm_name']}. Must be 'MAR' or 'RACMO'.")

    melt.get_melt_map()
