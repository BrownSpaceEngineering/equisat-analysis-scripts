#!/usr/bin/env bash
# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: fetches the entire history of EQUiSat tles from space-track.org.
# This file is used in various scripts which must track EQUiSat's position
# throughout history.

TLES_OUTPUT_FILE="tles.txt"

# URL to query to get full list of EQUiSat historical TLEs. 
# Note that instead of using this script you can alternatively 
# log in to space-track.org and download the file to $TLES_OUTPUT_FILE
# using this link.
EQUISAT_HISTORICAL_TLE_QUERY="https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/43552/orderby/EPOCH%20ASC/format/3le"

echo "NOTE: This script requires a www.space-track.org account."
echo "You can obtain one there, but if you're a BSE member"
echo "be sure to ask us for the BSE account."
echo "Otherwise, this repository should contain a fairly"
echo "recent set of TLEs to use."
echo "You can also contact BSE at bse@brown.edu to get a"
echo "newer copy."
echo
echo "So, please enter your space-track.org account info:"

read -p "Username (email): " username
read -sp "Password: " password
echo
echo

curl https://www.space-track.org/ajaxauth/login -d "identity=$username&password=$password&query=$EQUISAT_HISTORICAL_TLE_QUERY" -o $TLES_OUTPUT_FILE

echo
echo "Output to $TLES_OUTPUT_FILE"
echo "Note: if the file is empty, your username or password might be wrong"