#!/usr/bin/env python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to analyze deteriorations in receptions of EQUiSat's transmissions,
# by plotting RSSI in ambient conditions vs. packet-receiving conditions.

import matplotlib.pyplot as plt
import numpy as np

rx_az_el_rssi_data_ladd = np.genfromtxt("data/rx-az-el-rssi_ladd.csv",
    delimiter=',')
rx_az_el_rssi_data_ladd = rx_az_el_rssi_data_ladd[1:,:]

l_added_unix = rx_az_el_rssi_data_ladd[:,4]
l_elevation = rx_az_el_rssi_data_ladd[:,7]
l_rssi_packet = rx_az_el_rssi_data_ladd[:,9]
l_rssi_ambient = rx_az_el_rssi_data_ladd[:,10]

cond_packet_ok = l_rssi_packet != 0
l_added_unix_packet_filt = l_added_unix[cond_packet_ok]
l_rssi_packet_filt = l_rssi_packet[cond_packet_ok]
plt.plot(l_added_unix_packet_filt, l_rssi_packet_filt)

cond_ambient_ok = l_rssi_ambient != 0
l_added_unix_ambient_filt = l_added_unix[cond_ambient_ok]
l_rssi_ambient_filt = l_rssi_ambient[cond_ambient_ok]
plt.plot(l_added_unix_ambient_filt, l_rssi_ambient_filt)

# plt.plot(l_added_unix, -l_elevation)
plt.legend(["Last packet RSSI", "Ambient RSSI (recorded during doppler correction)"])
plt.ylabel("RSSI (dBm)")
plt.xlabel("UNIX timestamp (s)")
plt.savefig('data/ladd_rssi_ambient_vs_packet.png')
plt.show()