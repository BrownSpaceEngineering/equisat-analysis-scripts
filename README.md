# equisat-analysis-scripts
This repository is a collection of various scripts for downloading, maintaining, and analyzing data 
from the EQUiSat database and API. They are mainly intended for internal BSE use, but are often
designed to be easily usable and customizable. 
`signals_to_csv.py` in particular may be most generally useful.

In general, these scripts are designed to be run standalone, with a few exceptions:
- Those in folders are part of a larger pipeline (within those folders).
- Some scripts use transmissions.json as a local cache of the API database. 
  You may need to upload this "cache" by running `fetch_transmissions.sh`

If you have questions about using these scripts, feel free to email [bse@brown.edu](mailto:bse@brown.edu).

## Dependencies
Various Python scripts require various dependencies, but here is a complete list:
- [`requests`](https://2.python-requests.org/en/master/)
- [`matplotlib`](https://matplotlib.org/)
- [`ephem`/`pyephem`](https://pypi.org/project/ephem/)