#!/usr/bin/env python
import requests
import json
import matplotlib.pyplot as plt

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: simply shows a graph of boot count vs. time to see trends
# (to help bet on when the 8-bit counter will wrap around ;) )
# NOTE: run fetch_transmissions.sh before running this!

with open("transmissions.json", "r") as f:
    txs = json.load(f)
print("%d transmissions" % len(txs))

ts = []
reboot_nums = []
for t in txs:
    ts.append(t["current_info"]["timestamp"])
    reboot_nums.append(t["current_info"]["boot_count"])

plt.scatter(ts, reboot_nums)
plt.show()