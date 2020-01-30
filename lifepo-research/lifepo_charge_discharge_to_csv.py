#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: simply generates .csv for input into LiFePO4 charge/discharge spreadsheet

import requests
import json
import sys
import csv
import datetime
import dateutil.parser

def unixtime(dt):
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()

OUTFILE = "data/lifepo_charge_discharge_analysis.csv"

# avoid duplicate flash_cmps
data_hashes = {}

if __name__ == "__main__":
    print("fetching all transmissions")
    res = requests.get("http://api.brownspace.org/equisat/transmissions")
    txs = res.json()

    with open(OUTFILE, "w") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["tx cuid", "created", "created (ISO)", "timestamp","LF1REF","LF2REF","LF3REF","LF4REF","LF_B1_CHGN","LF_B2_CHGN","L1_TEMP","L2_TEMP","LF1_TEMP","LF3_TEMP"])

        count = 0
        for tx in txs:
                msg_type = tx["preamble"]["message_type"]
                curinfo = tx["current_info"]
                created = dateutil.parser.parse(tx["created"]).replace(tzinfo=None)
                
                # current info
                writer.writerow([
                    tx["cuid"],
                    unixtime(created),
                    tx["created"],
                    tx["preamble"]["timestamp"],
                    
                    curinfo["LF1REF"],
                    curinfo["LF2REF"],
                    curinfo["LF3REF"],
                    curinfo["LF4REF"],
                    1 if curinfo["LF_B1_CHGN"] else 0,
                    1 if curinfo["LF_B2_CHGN"] else 0,
                    curinfo["L1_TEMP"],
                    curinfo["L2_TEMP"],
                    
                    "",
                    ""
                ])
                count += 1
                
                # flash cmp if we have it
                if msg_type == "FLASH CMP":
                    data = tx["data"]
                    
                    for datum in data:
                        pay = datum["payload"]
                        if data_hashes.has_key(pay["data_hash"]):
                            continue
                        else:
                            data_hashes[pay["data_hash"]] = True
                        
                        created = dateutil.parser.parse(datum["created"]).replace(tzinfo=None)
                        
                        writer.writerow([
                            tx["cuid"],
                            unixtime(created),
                            datum["created"],
                            pay["timestamp"],
                            
                            pay["LF1REF"],
                            pay["LF2REF"],
                            pay["LF3REF"],
                            pay["LF4REF"],
                            
                            "",
                            "",
                            "",
                            "",
                            
                            pay["LF1_TEMP"],
                            pay["LF3_TEMP"],
                        ])
                        count += 1
                
        print("%d written" % count)
