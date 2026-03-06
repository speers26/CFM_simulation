"""Script which gets maps of average yearly melt across AIS (or Larsen C), for both MAR and RACMO.

Usage:
    - python melt_map.py

"""

from force.melt import MeltMAR, MeltRACMO

if __name__ == "__main__":
    MeltMAR().get_melt_map()
    MeltRACMO().get_melt_map()
