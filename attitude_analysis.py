#!/usr/bin/env python
# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to analyze the effectiveness of EQUiSat's attitude determinination and control system

import equisat_lib
import datetime
import ephem
import numpy as np
import matplotlib.pyplot as plt

OBJ_SIGS = [
    "IR_FLASH_OBJ",
    "IR_SIDE1_OBJ",
    "IR_SIDE2_OBJ",
    "IR_RBF_OBJ",
    "IR_ACCESS_OBJ",
    "IR_TOP1_OBJ"
]

# START_DATE = datetime.datetime(2018, 7, 13)
START_DATE = datetime.datetime(2020, 1, 1)
END_DATE = datetime.datetime.now()

sigs, success = equisat_lib.get_signals(OBJ_SIGS, START_DATE, END_DATE)
if success is not None:
    exit(1)

# all timestamp sets should be the same
objs_ts = [equisat_lib.api_ts_to_datetime(ts) for ts in sigs[OBJ_SIGS[0]]["timestamps"]]

## get object sensor values
objs_arr = []
for sig in OBJ_SIGS:
    objs_arr.append(sigs[sig]["values"])
objs = np.array(objs_arr)

def get_sun_bearing(loc, ts):
    sat = ephem.Observer()
    # TODO: is this right?
    sat.date = ephem.Date(ts)
    sat.lon, sat.lat, sat.elevation = loc.sublat, loc.sublong, loc.elevation
    sun = ephem.Sun()
    sun.date = ephem.Date(ts)
    sun.compute(sat)
    return (sun.az, sun.alt)

tles = equisat_lib.get_tles()

# get satellite location for each reading
locs = []
sun_bearings = []
for ts in objs_ts:
    loc = equisat_lib.get_location_at(ts, tles)
    locs.append(loc)
    sun_bearings.append(get_sun_bearing(loc, ts))

for b in sun_bearings:
    print(b)

def analyze_norms():
    norms = np.linalg.norm(objs, axis=0)
    print(norms)
    plt.hist(norms, bins=len(norms))
    plt.show()

# analyze_norms()

# TODOs: 
# see if we can compute a sun angle somehow
# see what that looks like over time
# pull in position and earth rotation data and see if we can get a predicted sun angle