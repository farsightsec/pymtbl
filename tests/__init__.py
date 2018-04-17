
import os
import unittest

import mtbl


def write_mtbl(filename, tuples):
    writer = mtbl.writer(filename, compression=mtbl.COMPRESSION_NONE)
    for k, v in tuples:
        writer[k] = v
    writer.close()
