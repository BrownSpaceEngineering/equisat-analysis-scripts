#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: this script was meant to analyze a single EQUiSat flash period
# and summarize the data from that period, particularly as it related
# to the period's timing.

import requests
import datetime
import sys

if len(sys.argv) != 3:
    print("usage: %s <flash cmp url> <flash burst url>" % sys.argv[0])
    exit(1)

complete_flash_cmp_url = sys.argv[1]
latest_flash_burst_url = sys.argv[2]

def parse_dt(dt):
    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%fZ")

flash_cmp = requests.get(complete_flash_cmp_url).json()
flash_burst = requests.get(latest_flash_burst_url).json()

cmp_ts = flash_cmp["preamble"]["timestamp"]
burst_ts = flash_burst["preamble"]["timestamp"]
cmp_added = parse_dt(flash_cmp["added"])
burst_added = parse_dt(flash_burst["added"])

cmps = flash_cmp["data"]
earliest_ts = min([cmps[i]["payload"]["timestamp"] for i in range(len(cmps))])
latest_ts = flash_burst["data"][0]["payload"]["timestamp"]

earliest = cmp_added - datetime.timedelta(seconds=(cmp_ts - earliest_ts))
latest = burst_added - datetime.timedelta(seconds=(burst_ts - latest_ts))

print("earliest : %s / %s" % (earliest, earliest_ts))
print("latest   : %s / %s" % (latest, latest_ts))
print("duration : %s" % (datetime.timedelta(seconds=latest_ts - earliest_ts)))
