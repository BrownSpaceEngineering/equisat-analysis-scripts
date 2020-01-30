#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to analyze the duration of EQUiSat flash periods
# NOTE: run ../fetch_transmissions.sh before running this!

import json
import datetime
import matplotlib.pyplot as plt
import dateutil.parser
import csv

def unixtime(dt=None, txt=None):
    if txt is not None:
        dt = dateutil.parser.parse(txt).replace(tzinfo=None)
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()

# download with wget api.brownspace.org/equisat/transmissions -O transmissions.json
with open("../transmissions.json", "r") as f:
    txs = json.load(f)
print("%d transmissions" % len(txs))

# sort with oldest first
txs.sort(key=lambda tx: tx["created"])

# collect all flash-related timestamps
MIN_CREATED = datetime.datetime(2018, 7, 12)
MIN_TS = 1
MAX_TS = 60000000 # TODO: MAKE SURE TO ADJUST!
tss = []
data_hashes = {}
num_flash_cmps = 0
num_flash_bursts = 0

for i in range(len(txs)):
    tx = txs[i]
    
    msg = tx["preamble"]["message_type"]
    if msg == "FLASH CMP":
        for i in range(len(tx["data"])):
            flash = tx["data"][i]
            created = dateutil.parser.parse(flash["created"]).replace(tzinfo=None)
            
            dh = flash["payload"]["data_hash"]
            if dh in data_hashes:
                continue
            data_hashes[dh] = True
            
            ts = flash["payload"]["timestamp"]
            if ts < MIN_TS or ts > MAX_TS or created < MIN_CREATED:
                continue
                
            num_flash_cmps += 1
                
            tss.append({
                "cuid": tx["cuid"],
                "created": unixtime(dt=created),
                "ts": ts,
                "packet_index": i,
                "type": msg
            })
            
    elif msg == "FLASH BURST":
        created = dateutil.parser.parse(tx["data"][0]["created"]).replace(tzinfo=None)
        
        dh = tx["data"][0]["payload"]["data_hash"]
        if dh in data_hashes:
            continue
        data_hashes[dh] = True
        
        ts = tx["data"][0]["payload"]["timestamp"]
        if ts < MIN_TS or ts > MAX_TS or created < MIN_CREATED:
            continue
            
        num_flash_bursts += 1
            
        tss.append({
            "cuid": tx["cuid"],
            "created": unixtime(dt=created),
            "ts": ts,
            "type": msg
        })
        
tss.sort(key=lambda ts: ts["ts"])
#print([t["ts"] for t in tss])

# segment out flashes based on timestamp
MAX_FLASH_DUR = 100*60 # s
flashes = []

start = tss[0]
start_i = 0

i = 0
while i < len(tss):
    while i < len(tss) and tss[i]["ts"] - start["ts"] <= MAX_FLASH_DUR:
        i += 1
        
    flashes.append({
        "start": start,
        "end": tss[i-1],
        "quantity": i - start_i
    })

    if i < len(tss):
        start = tss[i]
        start_i = i


print("%d distinct flash seqs" % len(flashes))
print("%d flash bursts" % num_flash_cmps)
print("%d flash cmps" % num_flash_bursts)
total_q = sum([f["quantity"] for f in flashes])
print("%d total flash components" % total_q)
assert(total_q == num_flash_bursts + num_flash_cmps)

avg_dur = sum([(f["end"]["ts"] - f["start"]["ts"]) for f in flashes])/len(flashes)
dur_str = datetime.timedelta(seconds=avg_dur)
print("average duration: %s (%3.0f minutes)" % (dur_str, avg_dur/60.0))

for f in flashes:
    dur_m = (f["end"]["ts"] - f["start"]["ts"]) / 60.0
    dur_str = datetime.timedelta(minutes=dur_m)
    print("%.2f: %10d -> %10d = %s (%3.0f minutes) : %s -> %s : q=%d" % \
        (f["start"]["created"], f["start"]["ts"], f["end"]["ts"], dur_str, dur_m, f["start"]["type"], f["end"]["type"], f["quantity"]))
        
        
with open("data/flash_durations.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["num", "quantity of txs", "start cuid", "end cuid", "start created", "end created", "start ts", "end ts", "duration (s)"])
    for i in range(len(flashes)):
        fl = flashes[i]
        start = fl["start"]
        end = fl["end"]
        writer.writerow([i, fl["quantity"], start["cuid"], end["cuid"], start["created"], end["created"], start["ts"], end["ts"], end["ts"] - start["ts"]])
        

print("""\nPlot: 
green => tx was start of flash period
red-orange => tx was end of flash period
yellow => tx was between start and end of flash period
""")
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.scatter([ts["created"] for ts in tss], [ts["ts"] for ts in tss], c='y', marker="s", s=160)
for end in ["start", "end"]:
    ax1.scatter([f[end]["created"] for f in flashes], [f[end]["ts"] for f in flashes],
        c=('g' if end == "start" else 'r'), marker="o", s=120)
plt.show()




