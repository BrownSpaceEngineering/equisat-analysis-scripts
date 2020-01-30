#!/usr/bin/env python
import requests
import json
import sys
import csv
import time

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: generates .csv files of satellite signals across the entire history of mission.
# See below for command line usage (this script can either by used with default signals or via CLI args).
# To get a list of possible signal names, see this document:
# https://docs.google.com/spreadsheets/u/1/d/e/2PACX-1vSCpr4KPwXkXyEMv6oPps-kVsNsd_Ell5whlvj-0T_5N9dIH5jvBTHCl6eZ_xVBugYEiL5CNR-p45G7/pubhtml?gid=589366724&single=true

# config
#DEF_SIGNALS = ["L1_TEMP", "RAD_TEMP"]
#DEF_SIGNALS = ["gyroscopeX", "gyroscopeY", "gyroscopeZ"]
#DEF_SIGNALS = ["L1_DISG", "L2_DISG", "L1_CHGN", "L2_CHGN", "L1_RUN_CHG", "L2_RUN_CHG", "LF_B2_CHGN", "LF_B1_CHGN", "L1_ST", "L2_ST"]
DEF_SIGNALS = ["LF1REF", "LF2REF", "LF3REF", "LF4REF", "LF_B1_CHGN", "LF_B2_CHGN", "L1_REF", "L2_REF", "L1_SNS", "L2_SNS", "L1_TEMP", "L2_TEMP", "L1_ST", "L2_ST", "L1_CHGN", "L2_CHGN"]
DEF_OUTFILE = "data/signal_data_temps.csv"

def sigs_to_csv(sigs, outfile):
    print("fetching signals %s" % signals)
    res = requests.get("http://api.brownspace.org/equisat/signals?fields=%s" % ",".join(signals))
    sigvals = res.json()

    with open(outfile, "w") as csvf:
        writer = csv.writer(csvf)
        headers = []
        for signal in signals:
            headers.append(signal + " timestamps")
            headers.append(signal + " values")
        writer.writerow(headers)

        # write each column until all are done
        done = False
        i = 0
        while not done:
            done = True
            row = []
            for signal in signals:
                sigdata = sigvals[signal]
                if len(sigdata["timestamps"]) > i and len(sigdata["values"]) > i:
                    row.append(sigdata["timestamps"][i])
                    row.append(sigdata["values"][i])
                    done = False
                else:
                    row.append("")
                    row.append("")
            writer.writerow(row)
            i += 1

        print("Wrote max of %d data points" % i)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("cli usage: ./signals_to_csv.py <output file> <signal name 1> <signal name 2> ...")
        print("using constants instead in 10s...")
        time.sleep(10)
        signals = DEF_SIGNALS
        outfile = DEF_OUTFILE
    else:
        outfile = sys.argv[1]
        signals = sys.argv[2:]
    
    sigs_to_csv(signals, outfile)

    
