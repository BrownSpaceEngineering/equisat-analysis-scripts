#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to generate stats on every received packet, including 
# RSSI, azimuth/elevation, and doppler information
# NOTE: you must download the history of EQUiSat tles.txt from 
# space-track.org (NORAD) using the URL below for this to work.
# Contact BSE if you can't get an account.

import requests
import json
import csv
import ephem
import datetime
import math

# config
# download from https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/43552/orderby/EPOCH%20ASC/format/3le
TLESFILE = "../tles.txt"
OUTFILE = "data/rx-az-el-rssi_ladd.csv"
EARLIEST_DATE = datetime.datetime(2018, 8, 1)
#ONLY_STATION = "Sapienza University of Rome"
ONLY_STATION = "Ladd Observatory"

# Ladd
STATION_LON = -71.398982 # deg E
STATION_LAT = 41.839157 # deg N
STATION_ALT = 66 # in meters
# Rome
# STATION_LON = 12.494183
# STATION_LAT = 41.892942
# STATION_ALT = 152

# constants
SAT_FREQ_HZ = 435550000
SPEED_OF_LIGHT_MPS = 299792000
DEG_PER_RAD = 360/(2*math.pi)
EPOCH = datetime.datetime(1970, 1, 1)

def read_tles():
    tles = []
    with open(TLESFILE, "r") as f:
        while True:
            # will error if file not formatted correctly
            l1 = f.readline()
            if l1 == "": break
            l2 = f.readline()
            if l2 == "": break
            l3 = f.readline()
            if l3 == "": break
            tles.append(ephem.readtle(l1, l2, l3))
    return tles

def tle_date_to_datetime(tle):
    return ephem.localtime(tle._epoch)
def trans_date_to_datetime(tx):
    return datetime.datetime.strptime(tx["added"], "%Y-%m-%dT%H:%M:%S.%fZ")
def get_doppler_shift(tle):
    return SAT_FREQ_HZ*(-tle.range_velocity / SPEED_OF_LIGHT_MPS)
def datetime_to_unix(dt):
    return (dt - EPOCH).total_seconds()


if __name__ == "__main__":
    obs = ephem.Observer()
    obs.lon = str(STATION_LON)
    obs.lat = str(STATION_LAT)
    obs.elevation = STATION_ALT

    # grab and sort
    def cmp_tles_by_date(t1, t2):
        return int(t1._epoch - t2._epoch)
    print("reading + sorting TLEs")
    tles = read_tles()
    tles = sorted(tles, cmp=cmp_tles_by_date)

    # grab and sort transmissions by date
    def cmp_trans_by_date(tx1, tx2):
        return int((trans_date_to_datetime(tx1) - trans_date_to_datetime(tx2)).total_seconds())
    print("requesting + sorting transmissions")
    res = requests.get("http://api.brownspace.org/equisat/transmissions/latest")
    trans = res.json()
    trans = sorted(trans, cmp=cmp_trans_by_date)
    tx_i = 0

    # collect sets of data from each tx recieve
    tx_data = []

    for i in range(len(tles)):
        # ignore first date and switch to next date once we get past the end
        tle_date = tle_date_to_datetime(tles[i])
        if tle_date < EARLIEST_DATE:
            continue
        if i+1 < len(tles):
            next_tle_date = tle_date_to_datetime(tles[i+1])
        else:
            next_tle_date = None

        if tx_i < len(trans):
            tx_date = trans_date_to_datetime(trans[tx_i])

        while tx_date is not None and next_tle_date is not None and tx_date < next_tle_date:
            if ONLY_STATION is None or trans[tx_i]["station_names"][0] == ONLY_STATION:
                obs.date = ephem.Date(tx_date)
                tles[i].compute(obs)
                
                stat_info = trans[tx_i]["station_info"][0]
                
                if stat_info.has_key("latest_packet_rssi"):
                    packet_rssi = stat_info["latest_packet_rssi"]
                    if packet_rssi == -140: # bad reading
                        packet_rssi = 0
                else:
                    packet_rssi = 0
                    
                if stat_info.has_key("latest_rssi"):
                    ambient_rssi = stat_info["latest_rssi"] 
                    if ambient_rssi == -140: # bad reading
                        ambient_rssi = 0
                else:
                    ambient_rssi = 0
                
                tx = {
                    "tle_epoch": tles[i]._epoch,
                    "tle_date": tle_date,
                    "added date": tx_date,
                    "tle_date_unix": datetime_to_unix(tle_date),
                    "added date_unix": datetime_to_unix(tx_date),
                    "station_name": trans[tx_i]["station_names"][0],
                    "azimuth": DEG_PER_RAD*tles[i].az,
                    "elevation": DEG_PER_RAD*tles[i].alt,
                    "doppler_shift": get_doppler_shift(tles[i]),
                    "packet_rssi": packet_rssi,
                    "ambient_rssi": ambient_rssi
                }
                tx_data.append(tx)

            tx_i += 1
            if tx_i < len(trans):
                tx_date = trans_date_to_datetime(trans[tx_i])
            else:
                tx_date = None

    # write series to TLE
    with open(OUTFILE, "w") as csvf:
        writer = csv.writer(csvf)
        headers = ["tle epoch", "tle date", "added date", "tle date (unix)", "added date (unix)", "station name", "azimuth (deg)", "elevation (deg)", "doppler shift (kHz)", "RSSI (last packet)", "RSSI (last ambient)"]
        writer.writerow(headers)

        i = 0
        for tx in tx_data:
            row = []
            row = [
                tx["tle_epoch"],
                tx["tle_date"],
                tx["added date"],
                tx["tle_date_unix"],
                tx["added date_unix"],
                tx["station_name"],
                tx["azimuth"],
                tx["elevation"],
                tx["doppler_shift"] / 1000,
                tx["packet_rssi"],
                tx["ambient_rssi"]
            ]
            writer.writerow(row)
            i += 1

        print("Wrote max %d data points" % i)
