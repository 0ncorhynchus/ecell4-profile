#! /usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from os.path import basename, splitext

def fname2label(fname):
    return splitext(basename(fname))[0]

def draw(fname):
    x = []
    ave = []
    std = []
    with open(fname, 'r') as f:
        lines = f.readlines()
    for l in lines:
        data = map(float, l.split())
        ys = data[1:]
        x.append(data[0])
        ave.append(np.average(ys))
        std.append(np.std(ys))
    plt.errorbar(x, ave, std, linestyle='None', marker='^', label=fname2label(fname))

def main(argv):
    plt.xscale('log')
    plt.yscale('log')
    for fname in argv[1:]:
        draw(fname)
    plt.legend(loc='upper left', prop={'size':6})
    plt.subplots_adjust(right=0.8)
    plt.savefig('tmp.eps')

if __name__ == '__main__':
    import sys
    main(sys.argv)
