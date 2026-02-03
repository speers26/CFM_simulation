import time
import yaml
import pandas as pd
import numpy as np
import os
import json
import shutil
import sys

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

sys.path.append(config["CFM_repo_path"])
import RCMpkl_to_spin as RCM  # noqa: F401 # type: ignore
from firn_density_nospin import FirnDensityNoSpin  # noqa: F401 # type: ignore

lat_int = config["borehole_lat"]
lon_int = config["borehole_lon"]
lat_val = config["borehole_lat"]
lon_val = config["borehole_lon"]

df_daily = pd.read_csv(
    f"{config['CFM_data_path']}/cfm_input/MAR_{lat_val}_{lon_val}_{config['start_year']}_{config['end_year']}.csv",
    index_col=0,
    parse_dates=True,
)

### This function contains all of the CFM configuration options. You can change them, and the configuration gets stored as a .json file.
### The values here are more or less the defaults.


def makejson():
    false = False
    true = True
    c = {
        "InputFileFolder": "CFMinput",
        "InputFileNameTemp": "example_tskin.csv",
        "InputFileNamebdot": "example_smb.csv",
        "InputFileNameIso": "example_isotope.csv",
        "InputFileNamerho": "example_rhos.csv",
        "InputFileNamemelt": "example_melt.csv",
        "resultsFolder": "CFMoutput_example",
        "initfirnFile": "example_firndata.csv",
        "initprofile": false,
        "input_type": "dataframe",
        "input_type_options": ["csv", "dataframe"],
        "DFresample": "1D",
        "DFfile": "MERRA2_CLIM_df_72.5_-38.75.pkl",
        "physRho": "GSFC2020",
        "physRho_options": [
            "HLdynamic",
            "HLSigfus",
            "Li2004",
            "Li2011",
            "Helsen2008",
            "Arthern2010S",
            "Arthern2010T",
            "Li2015",
            "Goujon2003",
            "Barnola1991",
            "Morris2014",
            "KuipersMunneke2015",
            "Crocus",
            "Ligtenberg2011",
        ],
        "MELT": true,
        "ReehCorrectedT": false,
        "FirnAir": false,
        "AirConfigName": "AirConfig.json",
        "TWriteInt": 1,
        "TWriteStart": 1980.0,
        "int_type": "nearest",
        "int_type_options": ["nearest", "linear"],
        "SeasonalTcycle": false,
        "SeasonalThemi": "north",
        "coreless": true,
        "TAmp": 10.0,
        "physGrain": true,
        "calcGrainSize": false,
        "GrGrowPhysics": "Arthern",
        "GrGrowPhysics_options": ["Arthern", "Katsushima"],
        "heatDiff": true,
        "conductivity": "Calonne2019",
        "conductivity_options": [
            "Schwander",
            "Yen_fixed",
            "Yen_var",
            "Anderson",
            "Yen_b",
            "Sturm",
            "VanDusen",
            "Schwerdtfeger",
            "Riche",
            "Jiawen",
            "mix",
            "Calonne2011",
            "Calonne2019",
        ],
        "variable_srho": false,
        "srho_type": "userinput",
        "srho_type_options": ["userinput", "param", "noise"],
        "rhos0": 350.0,
        "r2s0": 1.0e-8,
        "AutoSpinUpTime": false,
        "yearSpin": 20,
        "H": 3000,
        "HbaseSpin": 2880.0,
        "stpsPerYear": 12.0,
        "D_surf": 1.0,
        "bdot_type": "mean",
        "bdot_type_options": ["instant", "mean", "stress"],
        "grid_outputs": true,
        "grid_output_res": 0.25,
        "isoDiff": false,
        "iso": "D",
        "isoOptions": ["18", "D", "NoDiffusion"],
        "spacewriteint": 1,
        "strain": false,
        "du_dx": 1e-5,
        "outputs": [
            "density",
            "depth",
            "temperature",
            "age",
            "DIP",
            "meltoutputs",
            "grainsize",
        ],
        "outputs_options": [
            "density",
            "depth",
            "temperature",
            "age",
            "Dcon",
            "bdot_mean",
            "climate",
            "compaction",
            "grainsize",
            "temp_Hx",
            "isotopes",
            "BCO",
            "DIPc",
            "DIP",
            "LWC",
            "gasses",
            "PLWC_mem",
            "viscosity",
            "runoff",
            "refrozen",
        ],
        "resultsFileName": "CFMresults.hdf5",
        "spinFileName": "CFMspin.hdf5",
        "doublegrid": true,
        "nodestocombine": 30,
        "multnodestocombine": 12,
        "Dnodestocombine": 30,
        "Dmultnodestocombine": 12,
        "grid1bottom": 5.0,
        "grid2bottom": 10.0,
        "spinup_climate_type": "mean",
        "spinup_climate_type_options": ["mean", "initial"],
        "manual_climate": false,
        "deepT": 255.88,
        "bdot_long": 0.49073,
        "manual_iceout": false,
        "iceout": 0.23,
        "QMorris": 110.0e3,
        "timesetup": "exact",
        "timesetup_options": ["exact", "interp", "retmip"],
        "liquid": "bucket",
        "liquid_options": [
            "percolation_bucket",
            "bucketVV",
            "resingledomain",
            "prefsnowpack",
        ],
        "merging": false,
        "merge_min": 1e-4,
        "LWCcorrect": false,
        "manualT": false,
        "no_densification": false,
        "rad_pen": false,
        "site_pressure": 1013.25,
        "output_bits": "float32",
        "spinUpdate": true,
        "spinUpdateDate": 1980.0,
        "DIPhorizon": 100.0,
        "NewSpin": true,
        "ColeouLesaffre": false,
        "IrrVal": 0.02,
        "RhoImp": 830.0,
        "DownToIce": false,
        "ThickImp": 0.1,
        "Ponding": false,
        "DirectRunoff": 0.0,
        "RunoffZuoOerlemans": false,
        "Slope": 0.1,
        "SUBLIM": True,
        "keep_firnthickness": true,
        "SEB_TL_thick": 0.05,
        "albedo_factor": 1,
        "bdm_sublim": true,
        "iceblock": false,
        "iceblock_rho": 917.0,
        "truncate_outputs": false,
        "stage_zero": false,
        "snow_model": "Yamazaki1993",
        "s_zero_rho": 200,
    }

    return c


tnow = time.time()
runid = config["runid"]

### The CFM takes inputs as vectors of temperature, accumulation, etc., and decimal time.
### The following line calls a script that takes the df_daily and creates a python dictionary (called Cd, for climate dictionary)
### containing the vectors that the CFM needs to run.
### the function also returns some other variables that will be used to configure the CFM run.

#######
### Prepare config .json (which is a dictionary called c within this python script) ###
### edit as you wish here (the makejson function above just has defaults, you can change there as well)
### the edited json will be saved and used for the run.
c = makejson()

timeres = "2d"  # time resolution for the run, 5 days here (1 day is usually what I run, but slower)
sds = config["start_year"]  # spin date start
sde = config["end_year"]  # spin date end
runid = config["runid"]  # arbitrary, but you can use this to keep track of runs

# "physRho_options":["HLdynamic","HLSigfus","Li2004","Li2011","Helsen2008","Arthern2010S","Arthern2010T","Li2015","Goujon2003","Barnola1991","Morris2014","KuipersMunneke2015","Crocus","Ligtenberg2011"],

c["physRho"] = config["physRho"]  # firn densification equation
c["runID"] = runid
c["DFresample"] = timeres  # resolution of the model run, e.g. '1d' is 1 day.

c["SEB"] = True  # surface energy balalnce module
c["MELT"] = True  # whether to run melt module or not.
c["rain"] = True

c["lat_int"] = float(lat_int)
c["lon_int"] = float(lon_int)
c["lat_val"] = float(lat_val)
c["lon_val"] = float(lon_val)

"""
CFM regrids (merges) deeper nodes to save computation. There are 2 mergings
nodestocombine and multnodestocombine should be adjusted based on the time resolution of the run
e.g. if DFresample is '1d', nodestocombine = 30 will combine 30 layers at an intermediate depth, 
and multnodestocombine = 12 will combine 12 of those layers at a greater depth (which in this case 
will give 3 sections of firn - near the surface very thin layers, representing a day's accumulation,
middle, which is a month's accumulation, and deep, that should be a year's accumulation. 
e.g. if I am doing DFresample = '5d', I would set nodestocombine to 6 to still get layers that are a
month's worth of accumulation. (there is no 'best' way to do this - it is a bit of an art)
"""
c["doublegrid"] = config["doublegrid"]
c["nodestocombine"] = config["nodestocombine"]
c["multnodestocombine"] = config["multnodestocombine"]

### surface density (fixed or variable)
variable_srho = False
if variable_srho:
    c["variable_srho"] = config[
        "variable_srho"
    ]  # whether to use variable surface density
    c["srho_type"] = config["srho_type"]
else:
    c["rhos0"] = config["rhos0"]  # e.g here you could change the surface density
    rhotype = f"rho{c['rhos0']}"
#######

rf_pre = f'{config["CFM_data_path"]}/cfm_output'
rf_po = f'/CFMresults_{lat_val}_{lon_val}_{c["physRho"]}_notebook'

c["resultsFolder"] = (
    rf_pre + rf_po
)  # path (within CFM_main that the results will be stored in)

### format the CFM forcing data (including creating the spin up)
### climateTS is a dictionary with the various climate fields needed, in the correct units.
climateTS, StpsPerYr, depth_S1, depth_S2, grid_bottom, SEBfluxes = RCM.makeSpinFiles(
    df_daily,
    timeres=c["DFresample"],
    Tinterp="mean",
    spin_date_st=sds,
    spin_date_end=sde,
    melt=c["MELT"],
    desired_depth=None,
    SEB=c["SEB"],
    rho_bottom=config["rho_bottom"],
)

climateTS["SUBLIM"] = (
    -1 * climateTS["SUBLIM"]
)  # ADDED THIS FOR MERRA2 TO GET THE SIGN CORRECT.
climateTS["forcing_data_start"] = sds

c["stpsPerYear"] = float("%.2f" % (StpsPerYr))
c["stpsPerYearSpin"] = float("%.2f" % (StpsPerYr))
c["grid1bottom"] = float("%.1f" % (depth_S1))
c["grid2bottom"] = float("%.1f" % (depth_S2))
c["HbaseSpin"] = float("%.1f" % (3000 - grid_bottom))

c["DIPhorizon"] = np.floor(
    0.8 * grid_bottom
)  # firn air content, depth integrated porosity

c["keep_firnthickness"] = True
c["grid_outputs"] = True
c["grid_output_res"] = config["grid_output_res"]

configName = "CFMconfig_{}_{}_{}.json".format(lat_val, lon_val, c["physRho"])
if os.path.exists(os.path.join(c["resultsFolder"], configName)):
    CFMconfig = os.path.join(c["resultsFolder"], configName)
    shutil.move(CFMconfig, os.getcwd())
else:
    CFMconfig = configName

with open(CFMconfig, "w") as fp:
    fp.write(json.dumps(c, sort_keys=True, indent=4, separators=(",", ": ")))

NewSpin = config["NewSpin"]  # rerun the spin up each time if true

### Create CFM instance by passing config file and forcing data, then run the model
firn = FirnDensityNoSpin(
    CFMconfig, climateTS=climateTS, NewSpin=NewSpin, SEBfluxes=SEBfluxes
)
firn.time_evolve()
###
telap = (time.time() - tnow) / 60
print("main done, {} minutes".format(telap))

shutil.move(configName, os.path.join(c["resultsFolder"], configName))
