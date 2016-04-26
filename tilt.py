#!/usr/bin/python

import math

def readlines(fname):
    with open(fname, 'r') as f:
        return f.readlines()

def get_tilt(p0, p1):
    return (p1[1]-p0[1])/(p1[0]-p0[0])

def line2nums(line):
    return map(lambda x: float(x), line.split())

def log10(nums):
    return map(lambda x: math.log10(x), nums)

if __name__ == '__main__':
    import sys
    for fname in sys.argv[1:]:
        lines = readlines(fname)
        center_line = lines[len(lines)/2]
        last_line = lines[-1]
        center_point = log10(line2nums(center_line))
        last_point = log10(line2nums(last_line))
        print("%s :\t%f" % (fname, get_tilt(center_point, last_point)))
