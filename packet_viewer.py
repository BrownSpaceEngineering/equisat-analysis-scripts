#!/usr/bin/env python
# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: This script is simply used to check if parts of the telemetry have ever
# changed over the lifetime of the satellite. It was used to detect bugs in telemetry
# reporting.

import requests

res = requests.get("http://api.brownspace.org/equisat/transmissions/latest")
data = res.json()

packets = []
for d in data:
    packets.append(d["raws"][0])

for packet in packets:
    print(packet[46:50])
