
import os
import unittest

import mtbl


def write_mtbl(filename, tuples):
    writer = mtbl.writer(filename, compression=mtbl.COMPRESSION_NONE)
    for k, v in tuples:
        writer[k] = v
    writer.close()


class MtblTestCase(unittest.TestCase):

    def write_mtbl(self, filename, tuples):
        # tempfiles would be better but mtbl is bossy about fds :/ (?)
        filepath = os.path.join(
            os.path.dirname(__file__), filename)
        write_mtbl(filepath, tuples)
        self.addCleanup(os.remove, filepath)
        return filepath
