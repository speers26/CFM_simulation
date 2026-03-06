"""Script which gets maps of average yearly melt across AIC (or Larsen C), for RCM specified in config

Usage:
    - python melt_map.py

"""

from force.melt import MeltMar

if __name__ == "__main__":
    melt_mar = MeltMar()
    avg_yearly_melt_mar = melt_mar.get_melt_map()
