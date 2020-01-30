#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: simply generates .csv for input into spreadsheet for FLASH CMP data

import requests
import json
import sys
import csv
import datetime
import dateutil.parser

def unixtime(dt):
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()

START_DATE = datetime.datetime(2018, 7, 12)
OUTFILE = "data/flash_cmps.csv"

def get_station_names(tx_cuid):
    res = requests.get("http://api.brownspace.org/equisat/transmissions/%s" % tx_cuid)
    tx = res.json()
    return ",".join(tx["station_names"])

def write_cmps(cmps, csvf, write_header=True, start_date=datetime.datetime(2018, 7, 12)):
    # avoid duplicates
    data_hashes = {}
    
    writer = csv.writer(csvf)
    if write_header: 
        writer.writerow(["tx cuid", "created", "created (ISO)", "timestamp","LED1TEMP","LED2TEMP","LED3TEMP","LED4TEMP","LF1_TEMP","LF3_TEMP","LFB1SNS","LFB1OSNS","LFB2SNS","LFB2OSNS","LF1REF","LF2REF","LF3REF","LF4REF","LED1SNS","LED2SNS","LED3SNS","LED4SNS","magnetometer1X","magnetometer1Y","magnetometer1Z", "station names"])

    count = 0
    for c in cmps:
            pay = c["payload"]
            if data_hashes.has_key(pay["data_hash"]):
                continue
            else:
                data_hashes[pay["data_hash"]] = True

            created = dateutil.parser.parse(c["created"]).replace(tzinfo=None)
            if created < start_date:
                continue

            writer.writerow([
                c["transmission_cuid"],
                unixtime(created),
                c["created"],
                pay["timestamp"],
                pay["LED1TEMP"],
                pay["LED2TEMP"],
                pay["LED3TEMP"],
                pay["LED4TEMP"],
                pay["LF1_TEMP"],
                pay["LF3_TEMP"],
                pay["LFB1SNS"],
                pay["LFB1OSNS"],
                pay["LFB2SNS"],
                pay["LFB2OSNS"],
                pay["LF1REF"],
                pay["LF2REF"],
                pay["LF3REF"],
                pay["LF4REF"],
                pay["LED1SNS"],
                pay["LED2SNS"],
                pay["LED3SNS"],
                pay["LED4SNS"],
                pay["magnetometer1X"],
                pay["magnetometer1Y"],
                pay["magnetometer1Z"],
                get_station_names(c["transmission_cuid"])
            ])
            count += 1
    return count

if __name__ == "__main__":
    res = requests.get("http://api.brownspace.org/equisat/data/flashcomp/latest")
    cmps = res.json()

    with open(OUTFILE, "w") as csvf:
        count = write_cmps(cmps, csvf, start_date=START_DATE)
        print("%d written" % count)
        
