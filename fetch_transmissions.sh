#!/usr/bin/env bash
# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: fetches and parses all EQUiSat transmissions into json.
# must be run before some other scripts can execute (serves as an API cache)

# start date in ms since 1/1/1970
START_DATE=1546300800000

wget api.brownspace.org/equisat/transmissions?start_date=$START_DATE -O transmissions.json