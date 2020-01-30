#!/usr/bin/env python
# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: this script helps us analyze the drifting (and random jumping ahead) of 
# EQUiSat's onboard clock, so that this could be compensated for in the API.
# The analysis to correct the API was performed in this sheet:
# https://docs.google.com/spreadsheets/d/13SVh82FDTeVK_eZtC0jzgTHDbhu1vs8-Ng0xXUJIyNE/edit#gid=1407150828
# The corrections are applied here on the API server:
# https://github.com/BrownSpaceEngineering/bse-api/blob/master/server/routes/sat-timing.js

import requests
import json
import sys
import csv
import datetime
import dateutil.parser

OUTFILE = "data/packet_timestamps.csv"

def unixtime(iso):
    return (dateutil.parser.parse(iso).replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()

if __name__ == "__main__":
    res = requests.get("http://api.brownspace.org/equisat/transmissions")
    txs = res.json()

    with open(OUTFILE, "w") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["url", "added", "added (ISO)", "created", "created (ISO)", "rx_time", "rx_time (ISO)", "timestamp"])


        count = 0
        for tx in txs:
            if "timestamp" in tx["current_info"]:
                writer.writerow([
                    "http://api.brownspace.org/equisat/transmissions/%s" % tx["cuid"],
                    unixtime(tx["added"]),
                    tx["added"],
                    unixtime(tx["created"]),
                    tx["created"],
                    unixtime(tx["station_info"][0]["request_time"]),
                    tx["station_info"][0]["request_time"],
                    tx["current_info"]["timestamp"],
                ])
                count += 1

    print("%d/%d txs written" % (count, len(txs)))
