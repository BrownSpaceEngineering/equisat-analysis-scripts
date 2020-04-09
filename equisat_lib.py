#!/usr/bin/env python

import requests
import datetime
import pytz
import ephem
import math

EPOCH = datetime.datetime(1970, 1, 1)
DEG_PER_RAD = 360./(2*math.pi)

# download using `fetch_historical_tles.sh`
TLEFILE = "tles.txt"

##### API Calls #####

def get_signals(signals, start_date=None, end_date=None):
    """ Downloads the desired signals from start date to end date. """
    url = "http://api.brownspace.org/equisat/signals?fields=%s&start_date=%d&end_date=%d" % \
        (",".join(signals), 1000*datetime_to_unix(start_date), 1000*datetime_to_unix(end_date))
    res = requests.get(url)
    if res.status_code < 200 or res.status_code >= 300:
        print("bad API status code: %d" % res.status_code)
        return None, res.status_code
    return res.json(), None

##### Helpers #####

def api_ts_to_datetime(sig_ts):
    return datetime.datetime.utcfromtimestamp(int(sig_ts/1000))

def datetime_to_unix(dt):
    """ Converts a datetime to seconds since 1/1/1970, the epoch. """
    return (dt - EPOCH).total_seconds()

def datetime_to_utc(dt):
    return dt.astimezone(pytz.utc)

##### Location Tracked Analysis #####

def read_tles(tlefile):
    tles = []
    with open(tlefile, "r") as f:
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
    # TODO: would be better to convert to UTC
    return ephem.localtime(tle._epoch)

def ephem_deg_to_deg(edeg):
    """ Converts an ephem degrees object to a float in degrees. """
    return float(edeg)*DEG_PER_RAD

def get_tles(tlefile=TLEFILE):
    """ Fetches and sorts ephem TLE objects from the given file. """
    def cmp_tles_by_date(t1, t2):
        return int(t1._epoch - t2._epoch)
    tles = read_tles(tlefile)
    tles = sorted(tles, cmp=cmp_tles_by_date)
    return tles

def get_tle_for_time(dt, tles):
    """ Returns the ephem TLE object to use to compute positions at the given local time,
    using the given SORTED tles from get_tles. """
    if len(tles) == 0:
        return None
    elif len(tles) == 1:
        # assume it's a recent TLE... (ephem will yell at people who use it anyways)
        if dt > tle_date_to_datetime(tles[0]):
            return tles[0]
        else:
            return None
    else:
        mid = int(len(tles)/2)-1
        mid_date = tle_date_to_datetime(tles[mid])
        mid_date_next = tle_date_to_datetime(tles[mid+1])
        if dt >= mid_date and dt < mid_date_next:
            return tles[mid]
        elif dt < mid_date:
            return get_tle_for_time(dt, tles[:mid+1])
        else:
            return get_tle_for_time(dt, tles[mid+1:])

def get_location_at(dt, tles):
    """ Returns an ephem tle object with information on the location of the satellite
    at the given local time. Ex fields: .sublat, .sublong, .elevation """
    tle = get_tle_for_time(dt, tles)
    if tle is None:
        return None
    tle.compute(ephem.Date(dt))
    return tle
