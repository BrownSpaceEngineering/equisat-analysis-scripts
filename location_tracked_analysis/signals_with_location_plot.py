#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to plot the locations of signal data points 
# from signals_with_location.py on a basic map
# NOTE: you must run signals_with_location.py first

import csv
import matplotlib.pyplot as plt
import geopandas
import time

INFILE = "data/signal_loc_data.csv"
PLOT_DATA = False
JUST_NORTHWEST = False

CREATED_I = 4
LATS_I = 5
LONGS_I = 6
FIRST_DATA_PT_I = 8

sigdata = []
with open(INFILE, "r") as f:
    reader = csv.reader(f)
    headers = reader.next()
    for row in reader:
        sigdata.append(row)

lats = [float(sig[LATS_I]) for sig in sigdata]
longs = [float(sig[LONGS_I]) for sig in sigdata]

# plt.figure()
# plt.subplot(111, projection="mollweide")
# plt.grid(True)

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
world.plot(color="#5284ce", figsize=(16, 9))

plt.title("Locations of every received EQUiSat data point%s" % \
    (" (northwest)" if JUST_NORTHWEST else ""), family="Roboto", fontweight="regular")
plt.scatter(longs, lats, c="#f04230", s=2)
plt.axis("off")

if JUST_NORTHWEST:
    plt.xlim((-128, 37))
    plt.ylim((0, 56))

if PLOT_DATA:
    plt.figure()

    ts = [float(sig[CREATED_I]) for sig in sigdata]
    for i in range(FIRST_DATA_PT_I, len(sigdata[0])):
        data = [float(sig[i]) for sig in sigdata]
        plt.plot(ts, data)

    plt.legend(headers[FIRST_DATA_PT_I:], loc='best')
    plt.title("Data points")
    plt.xlabel("UNIX timestamp (secs since 1/1/1970)")

# plt.savefig('data/equisat_data_point_locations%s.png' % \
#     ("_northwest" if JUST_NORTHWEST else ""), dpi=300)
plt.show()