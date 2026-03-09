"""Script to plot spatial maps of variables from the RCM simulations, typically restricted to AIS peninsula.

Usage:
    - plot_spatial.py
"""

from plot import SpatialPlotter

if __name__ == "__main__":
    rcm_name = "RACMO"  # or "MAR"
    variables = ["mltgl"]  # list of variable names to plot, e.g. "mltgl" for melt in MAR and RACMO

    spatial_plotter = SpatialPlotter(rcm_name=rcm_name, variables=variables, plot_type="mean")
    spatial_plotter.plot()
