#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: like signals_to_csv.py (entire history of satellite signals), 
# but including location information of the satellite at the time.
# NOTE: you must download the history of EQUiSat tles.txt from 
# space-track.org (NORAD) using the URL below for this to work.
# Contact BSE if you can't get an account.

import requests
import json
import csv
import ephem
import datetime
import math

## config ##
# NOTE: signals must have matching sets of timestamps, and the script
# will only compute up to the min number of signal readings.
# To get a list of possible signal names, see this document:
# https://docs.google.com/spreadsheets/u/1/d/e/2PACX-1vSCpr4KPwXkXyEMv6oPps-kVsNsd_Ell5whlvj-0T_5N9dIH5jvBTHCl6eZ_xVBugYEiL5CNR-p45G7/pubhtml?gid=589366724&single=true
SIGNALS = ["LED1TEMP", "LED2TEMP", "LED3TEMP", "LED4TEMP"]
# SIGNALS = ["timestamp"] # basically all packets
# SIGNALS = ["time_to_flash"] # all individual transmissions (downlinks)

# EARLIEST_DATE = datetime.datetime(2018, 8, 1)
# LATEST_DATE = datetime.datetime(2020, 2, 1)

## date ranges ##
# EARLIEST_DATE = datetime.datetime.utcfromtimestamp(1551610000)
# LATEST_DATE =   datetime.datetime.utcfromtimestamp(1551620000)
# EARLIEST_DATE = datetime.datetime.utcfromtimestamp(1545496000)
# LATEST_DATE =   datetime.datetime.utcfromtimestamp(1545510000)
# EARLIEST_DATE = datetime.datetime.utcfromtimestamp(1535170000)
# LATEST_DATE =   datetime.datetime.utcfromtimestamp(1535180000)
EARLIEST_DATE = datetime.datetime.utcfromtimestamp(1532560000)
LATEST_DATE =   datetime.datetime.utcfromtimestamp(1532570000)
# EARLIEST_DATE = datetime.datetime.utcfromtimestamp(1554450000)
# LATEST_DATE =   datetime.datetime.utcfromtimestamp(1554470000)
# EARLIEST_DATE = datetime.datetime.utcfromtimestamp(1550810000)
# LATEST_DATE =   datetime.datetime.utcfromtimestamp(1550830000)


OUTFILE = "data/signal_loc_data.csv"
# download from https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/43552/orderby/EPOCH%20ASC/format/3le
TLESFILE = "tles.txt"

# constants
DEG_PER_RAD = 360./(2*math.pi)
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
def datetime_to_unix(dt):
    return (dt - EPOCH).total_seconds()
def ephem_deg_to_deg(edeg):
    return float(edeg)*DEG_PER_RAD

def get_sig_datetime(sigvals, sig_i, min_sigvals_len):
    if sig_i < min_sigvals_len:
        sig_date_val = sigvals[SIGNALS[0]]["timestamps"][sig_i]
        # ensure all signals have same timestamp
        for j in range(1, len(SIGNALS)):
            if sigvals[SIGNALS[j]]["timestamps"][sig_i] != sig_date_val:
                print("signal index %d did not have same timestamp for all signals!" % sig_i)
                exit(1)
        return datetime.datetime.utcfromtimestamp(int(sig_date_val/1000))
    return None

if __name__ == "__main__":
    # grab and sort
    def cmp_tles_by_date(t1, t2):
        return int(t1._epoch - t2._epoch)
    print("reading + sorting TLEs")
    tles = read_tles()
    tles = sorted(tles, cmp=cmp_tles_by_date)

    # grab signals (sorted in ascending order of created field)
    assert len(SIGNALS) > 0
    print("requesting signals")
    url = "http://api.brownspace.org/equisat/signals?fields=%s&start_date=%d&end_date=%d" % \
        (",".join(SIGNALS), 1000*datetime_to_unix(EARLIEST_DATE), 1000*datetime_to_unix(LATEST_DATE))
    res = requests.get(url)
    if res.status_code < 200 or res.status_code >= 300:
        print("bad API status code: %d" % res.status_code)
        exit(1)

    sigvals = res.json()
    min_sigvals_len = min([len(sigvals[sig]["timestamps"]) for sig in SIGNALS])
    sig_i = 0

    # collect sets of data from each tx recieve
    sig_data = []

    print("iterating over %d signals" % min_sigvals_len)
    for i in range(len(tles)):
        tle_date = tle_date_to_datetime(tles[i])
        # switch to next date once we get past the end
        if i+1 < len(tles):
            next_tle_date = tle_date_to_datetime(tles[i+1])
        else:
            break

        sig_date = get_sig_datetime(sigvals, sig_i, min_sigvals_len)

        # keep trying signals until/while they fall in the validity period of this TLE
        while sig_date is not None and next_tle_date is not None \
            and sig_date < next_tle_date and sig_date <= LATEST_DATE:
            # if we're not on this TLE yet, or not at the earliest date,
            # loop till we are (should only apply for the first one)
            if sig_date >= tle_date and sig_date >= EARLIEST_DATE:
                tles[i].compute(ephem.Date(sig_date))

                # corresponds to headers below
                sig = [
                    tles[i]._epoch,
                    tle_date,
                    datetime_to_unix(tle_date),
                    sig_date,
                    datetime_to_unix(sig_date),
                    ephem_deg_to_deg(tles[i].sublat),
                    ephem_deg_to_deg(tles[i].sublong),
                    tles[i].elevation,
                ]
                for signame in SIGNALS:
                    sig.append(sigvals[signame]["values"][sig_i])

                sig_data.append(sig)

            sig_i += 1
            sig_date = get_sig_datetime(sigvals, sig_i, min_sigvals_len)

    # write series to TLE
    with open(OUTFILE, "w") as csvf:
        writer = csv.writer(csvf)
        headers = [
            "tle epoch",
            "tle date", 
            "tle date (unix)", 
            "created date",
            "created date (unix)",
            "latitude (+N)",
            "longitude (+E)",
            "elevation (m above sea level)"]
        headers += SIGNALS

        writer.writerow(headers)
        writer.writerows(sig_data)
        print("Wrote %d data points" % len(sig_data))
