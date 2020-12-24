#!/usr/bin/env python
# author: Mckenna Cisler <mckenna_cisler@alumni.brown.edu>
# purpose: to determine and graph EQUiSat's altitude over the course of it's mission
# NOTE: requires up-to-date historical tles (run ./fetch_historical_tles.sh)

import equisat_lib
import datetime
import ephem
import numpy as np
import matplotlib.pyplot as plt

START_DATE = datetime.datetime(2018, 7, 17)
END_DATE = datetime.datetime.now()
INCREMENT_MINS = 80
MINS_TO_AVG = 15*24*60
PTS_TO_AVG = int(MINS_TO_AVG/INCREMENT_MINS)

tles = equisat_lib.get_tles()

# get sat altitude points
cur_ts = START_DATE
ts_vals = []
alt_vals = []
while cur_ts <= END_DATE:
    ts_vals.append(cur_ts)

    loc = equisat_lib.get_location_at(cur_ts, tles)
    alt_vals.append(loc.elevation/1000.)

    cur_ts += datetime.timedelta(minutes=INCREMENT_MINS)

smooth_box = np.ones(PTS_TO_AVG)/PTS_TO_AVG
alt_vals_smoothed = np.convolve(alt_vals, smooth_box, mode='valid')
ts_vals_smoothed = ts_vals[int(PTS_TO_AVG/2):-int(PTS_TO_AVG/2)+1]

plt.plot(ts_vals, alt_vals)
plt.plot(ts_vals_smoothed, alt_vals_smoothed)
plt.plot()
plt.ylim(bottom=0)
plt.legend(["Altitude", "Altitude (smoothed)", "Edge of Atmosphere"])
plt.title("EQUiSat Orbital Altitude")
plt.ylabel("Orbital Altitude ASL (km)")
plt.xlabel("Date")
plt.show()
