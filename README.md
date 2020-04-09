# equisat-analysis-scripts
This repository is a collection of various scripts for downloading, maintaining, and analyzing data 
from the EQUiSat database and API. They are mainly intended for internal BSE use, but are often
designed to be easily usable and customizable.

`signals_to_csv.py` in particular may be the most generally useful.
`equisat_lib.py` is the core library that interfaces with the BSE databases API, which is behind most of these scripts (or is being made to be).

In general, these scripts are designed to be run standalone, with a few exceptions:
- Many require `equisat_lib.py`.
- Those in folders are generally part of a larger pipeline (within those folders).
- Some scripts use `transmissions.json` as a local cache of the API database. 
  You will need to update this "cache" by running `fetch_transmissions.sh`
- Some scripts use `tles.txt`, a list of all historical TLEs (three line elements) from EQUiSat. You may want to update this list with the script `fetch_historical_tles.sh`, though we try to provide a recent copy with this repo, because you need account credentials to run this script.

If you have questions about using these scripts, feel free to email [bse@brown.edu](mailto:bse@brown.edu).

## Dependencies
Various Python scripts require various dependencies, but here is a complete list:
- [`requests`](https://2.python-requests.org/en/master/)
- [`numpy`](https://pypi.org/project/numpy/)
- [`matplotlib`](https://matplotlib.org/)
- [`ephem`/`pyephem`](https://pypi.org/project/ephem/)