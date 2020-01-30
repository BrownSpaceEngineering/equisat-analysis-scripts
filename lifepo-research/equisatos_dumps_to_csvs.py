#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: simply generates .csv for input into spreadsheet for FLASH BURST and FLASH CMP data,
# but using pre-launch EQUiSat log dump files

import requests
import json
import sys
import csv
import datetime
import binascii
import dateutil.parser
from packetparse import packetparse

import flash_burst_to_csv
import flash_cmp_to_csv

APPEND = False # whether to append to .csvs
OUTFILE_BURST = "data/ground_flash_bursts.csv"
OUTFILE_CMP = "data/ground_flash_cmps.csv"
START_DATE = datetime.datetime(1970, 1, 1) # these dumps are before launch

def read_dump_file(dfile):
    pkts = []
    for line in dfile:
        cl = line.replace("Pet watchdog", "")
        cl = cl.replace(" ", "")
        cl = cl.replace("\t", "")
        cl = cl.replace("\r", "")
        
        if cl[0:6] == "WL9XZE":
            pkt_raw = cl[0:255]
            pkt = binascii.hexlify(pkt_raw)
            parsed, errs = packetparse.parse_packet(pkt)
            if len(errs) == 0:
                pkts.append(parsed)
            else:
                print("errors decoding packet: %s (len: %d)" % (errs, len(pkt_raw)))
    return pkts


def read_cmps_bursts(pkts, start_dt):
    cmps = []
    bursts = []
    for pkt in pkts:
        msg_type = pkt["preamble"]["message_type"]
        if msg_type == "FLASH BURST":
            ts = pkt["data"]["timestamp"]
            bursts.append({
                "created": (start_dt + datetime.timedelta(seconds=ts)).isoformat(),
                "payload": pkt["data"],
                "transmission_cuid": ""      
            })
            
        elif msg_type == "FLASH CMP":
            for c in pkt["data"]:
                ts = c["timestamp"]
                cmps.append({
                    "created": (start_dt + datetime.timedelta(seconds=ts)).isoformat(),
                    "payload": c,
                    "transmission_cuid": ""
                })
    return cmps, bursts


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage: %s <dump file 1> <dump file 1 start date> <dump file 2> ..." % (sys.argv[0]))
        exit(1)
        
    files = sys.argv[1::2]
    start_dates = sys.argv[2::2]
    assert(len(files) == len(start_dates))
    
    first_f = True
    mode = "a" if APPEND else "w"
    with open(OUTFILE_BURST, mode) as csvf_burst:
        with open(OUTFILE_CMP, mode) as csvf_cmp:    
            for i in range(len(files)):
                fname = files[i]
                start_date = dateutil.parser.parse(start_dates[i])
                with open(fname, "r") as f:
                    cmps, bursts = read_cmps_bursts(read_dump_file(f), start_date)

                    num_b = flash_burst_to_csv.write_bursts(bursts, csvf_burst, \
                        write_header=first_f, start_date=START_DATE)
                    print("%s: %d bursts written" % (fname, num_b))
                    
                    num_c = flash_cmp_to_csv.write_cmps(cmps, csvf_cmp, \
                        write_header=first_f, start_date=START_DATE)
                    print("%s: %d cmps written" % (fname, num_c))
                    
                first_f = False
