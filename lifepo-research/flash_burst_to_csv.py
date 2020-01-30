#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: simply generates .csv for input into spreadsheet for FLASH BURST data

import requests
import json
import sys
import csv
import datetime
import dateutil.parser

def unixtime(dt=None, txt=None):
    if txt is not None:
        dt = dateutil.parser.parse(txt).replace(tzinfo=None)
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()

START_DATE = datetime.datetime(2018, 7, 12)
OUTFILE = "data/flash_bursts.csv"

def get_station_names(tx_cuid):
    res = requests.get("http://api.brownspace.org/equisat/transmissions/%s" % tx_cuid)
    tx = res.json()
    return ",".join(tx["station_names"])

def write_bursts(bursts, csvf, write_header=True, start_date=datetime.datetime(2018, 7, 12)):
    # avoid duplicates
    data_hashes = {}    

    writer = csv.writer(csvf)
    if write_header:
        writer.writerow(["num", "tx cuid", "created", "created (ISO)", "timestamp","ms","LED1TEMP","LED2TEMP","LED3TEMP","LED4TEMP","LF1_TEMP","LF3_TEMP","LFB1SNS","LFB1OSNS","LFB2SNS","LFB2OSNS","LF1REF","LF2REF","LF3REF","LF4REF","LED1SNS","LED2SNS","LED3SNS","LED4SNS","gyroscopeX","gyroscopeY","gyroscopeZ", "station names"])

    uniques = []
    for b in bursts:
        pay = b["payload"]
        if data_hashes.has_key(pay["data_hash"]):
            continue
        else:
            data_hashes[pay["data_hash"]] = True

        created = unixtime(txt=b["created"])
        if created < unixtime(start_date):
            continue

        uniques.append(b)

    count = 0
    for c in uniques:
        pay = c["payload"]
        station_names = get_station_names(c["transmission_cuid"])
        burst = pay["burst"]
        
        for i in range(7):
            row = burst[i]
            writer.writerow([
                len(uniques)-count, # because in reverse order
                c["transmission_cuid"],
                unixtime(txt=c["created"]),
                c["created"],
                pay["timestamp"],
                (i-1)*20,
                row["LED1TEMP"],
                row["LED2TEMP"],
                row["LED3TEMP"],
                row["LED4TEMP"],
                row["LF1_TEMP"],
                row["LF3_TEMP"],
                row["LFB1SNS"],
                row["LFB1OSNS"],
                row["LFB2SNS"],
                row["LFB2OSNS"],
                row["LF1REF"],
                row["LF2REF"],
                row["LF3REF"],
                row["LF4REF"],
                row["LED1SNS"],
                row["LED2SNS"],
                row["LED3SNS"],
                row["LED4SNS"],
                row["gyroscopeX"],
                row["gyroscopeY"],
                row["gyroscopeZ"],
                station_names
            ])
        count += 1
    return count

if __name__ == "__main__":
    res = requests.get("http://api.brownspace.org/equisat/data/flashburst/latest")
    cmps = res.json()

    with open(OUTFILE, "w") as csvf:
        count = write_bursts(cmps, csvf, start_date=START_DATE)
        print("%d written" % count)
