#!/usr/bin/env python

import sys

import mtbl
import os

def main(fname):
    reader = mtbl.reader(fname)
    md = reader.metadata()
    for data in md:
        print("{}: {}".format(data, md[data]))
    reader.close()

def usage():
    sys.stderr.write('Usage: %s <MTBL FILENAME>\n' % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    fname = sys.argv[1]
    main(fname)
