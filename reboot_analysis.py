#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: this script performs some analysis on the reboot periods of the satellites,
# to help determine the pattern of reboots and what may cause them
# NOTE: run fetch_transmissions.sh before running this!

import json
import datetime
import matplotlib.pyplot as plt
import dateutil.parser

def unixtime(dt=None, txt=None):
    if txt is not None:
        dt = dateutil.parser.parse(txt).replace(tzinfo=None)
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()

with open("transmissions.json", "r") as f:
    txs = json.load(f)
    

# sort with oldest first
txs.sort(key=lambda tx: tx["created"])

MAX_BOOT_DEV = 12
createds = []
reboot_cnts = []
pre_reboot_elocs = []
pre_reboot_ecodes = []
pre_reboot_states = []
boot_durations = []

cur_reboot = 1
last_reboot_time = unixtime(txt=txs[0]["created"])

for i in range(len(txs)):
    tx = txs[i]
    boot_cnt = tx["current_info"]["boot_count"]
    if abs(boot_cnt - cur_reboot) <= MAX_BOOT_DEV:
        reboot_cnts.append(boot_cnt)
        
        created = unixtime(txt=tx["created"])
        createds.append(created)
        
        if boot_cnt != cur_reboot:
            cur_reboot = boot_cnt

            dur = created - last_reboot_time    
            boot_durations.append(dur)
            last_reboot_time = created
            print("%d -> %d: %s" % (cur_reboot, boot_cnt, datetime.timedelta(seconds=dur)))
            
            if i > 0:
                prev_tx = txs[i-1]
                pre_reboot_states.append(prev_tx["preamble"]["satellite_state"])
                
                for j in range(len(prev_tx["error_codes"])):
                    pre_reboot_elocs.append(prev_tx["error_codes"][j]["error_location_name"])
                    pre_reboot_ecodes.append(prev_tx["error_codes"][j]["error_code_name"])

avg_dur = sum(boot_durations)/len(boot_durations)
print("average boot duration: %s (%ds)" % (datetime.timedelta(seconds=avg_dur), avg_dur/1000))

#plt.scatter(createds, reboot_cnts)
hist_met = pre_reboot_elocs # pre_reboot_ecodes pre_reboot_elocs pre_reboot_states
plt.hist(hist_met, bins=len(hist_met))
plt.show()




