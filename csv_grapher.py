#!/usr/bin/python

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: basic generalized script to generate a graph from any .csv file

import csv
import sys
import matplotlib.pyplot as plt

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: %s <csv filename> <x column> <y column>" % sys.argv[0])
        exit(1)

    infile = sys.argv[1]
    x_col = int(sys.argv[2])
    y_col = int(sys.argv[3])

    x = []
    y = []
    with open(infile, "r") as csvf:
        reader = csv.reader(csvf)

        for row in reader:
            try:
                num_x = float(row[x_col])
                num_y = float(row[y_col])
                # so we only append if both work
                x.append(num_x)
                y.append(num_y)
            except ValueError:
                continue

    plt.scatter(x, y)
    plt.show()
