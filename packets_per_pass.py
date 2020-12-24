#!/usr/bin/env python
# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: This script is for determining how any packets a ground station received per pass,
# including general statistics and a histogram

import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
import sys

## config ##
#ONLY_STATION = "Sapienza University of Rome"
ONLY_STATION = "Ladd Observatory"
MAX_PASS_DUR_S = 15*60 # s

with open("transmissions.json", "r") as f:
    txs = json.load(f)

# for tx in txs:
#     if len(tx["station_info"]) > 0:
#         stat = tx["station_info"][0]
#         if stat["name"] == ONLY_STATION:
#             num_stations += 1
#             pass_data = stat["pass_data"]
#             if pass_data is not None:
#                 num_passes += 1
#                 rise_time = pass_data["rise_time"]
#                 if rise_time in pass_cts:
#                     pass_cts[rise_time] += 1
#                 else:
#                     pass_cts[rise_time] = 1

# get all txs from this station
station_txs = []
for tx in txs:
    for stat in tx["station_info"]:
        if stat["name"] == ONLY_STATION:
            tx["station_info"][0] = stat # make sure it's the first
            station_txs.append(tx)

# sort txs by request time
def trans_date_to_datetime(tx):
    return datetime.datetime.strptime(tx["added"], "%Y-%m-%dT%H:%M:%S.%fZ")
if sys.version_info[0] == 2:
    def cmp_trans_by_date(tx1, tx2):
        return int((trans_date_to_datetime(tx1) - trans_date_to_datetime(tx2)).total_seconds())
    station_txs_sort = sorted(station_txs, cmp=cmp_trans_by_date)
else:
    station_txs_sort = sorted(station_txs, key=lambda tx: trans_date_to_datetime(tx))

# sort into 10-minute chunks (assumed to be passes)
pass_cts = {}
addeds = {}
pass_i = 0

pass_start = station_txs_sort[0]
pass_cts[0] = 0
addeds[0] = station_txs_sort[0]["added"]

for tx in station_txs_sort:
    if (trans_date_to_datetime(tx) - trans_date_to_datetime(pass_start)).total_seconds() > MAX_PASS_DUR_S:
        pass_i += 1
        pass_start = tx
        pass_cts[pass_i] = 1
        addeds[pass_i] = tx["added"]
    else:
        pass_cts[pass_i] += 1

# manual removing of outliers
del pass_cts[len(pass_cts)-1]
del pass_cts[0]

cts = list(pass_cts.values())

for i, ct in pass_cts.items():
    print("%d: %d (started: %s)" % (i, ct, addeds[i]))

print("%d station txs, %d passes" % (len(station_txs_sort), len(pass_cts)))
print("min: %d, max: %d, mean: %f, median: %f" % (
    np.min(cts), np.max(cts), np.mean(cts), np.median(cts)
))
plt.hist(cts, bins=np.max(cts))
plt.show()
