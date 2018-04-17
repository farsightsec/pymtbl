
import os
import unittest

import mtbl
from . import write_mtbl


def merge_func(key, val0, val1):
    return val0 + ' ' + val1


class MergerTestCase(unittest.TestCase):

    def write_mtbl(self, filename, tuples):
        # tempfiles would be better but mtbl is bossy about fds :/ (?)
        filepath = os.path.join(
            os.path.dirname(__file__), filename)
        write_mtbl(filepath, tuples)
        self.addCleanup(os.remove, filepath)
        return filepath

    def setUp(self):
        super(MergerTestCase, self).setUp()
        # write two mtbls to be merged
        self.mtbls_to_merge = []
        for filename, tuples in [
                ('left.mtbl',
                 [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')]),
                ('right.mtbl',
                 [('key17', 'val17'), ('key23', 'val23'), ('key4', 'val4')]),
        ]:
            mtbl = self.write_mtbl(filename, tuples)
            self.mtbls_to_merge.append(mtbl)

    def test_merge_and_iteritems(self):
        merger = mtbl.merger(merge_func)
        merged_filename = os.path.join(
            os.path.dirname(__file__), 'merged.mtbl')
        writer = mtbl.writer(
            merged_filename, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, merged_filename)
        # write a merged mtbl
        for filename in self.mtbls_to_merge:
            merger.add_reader(mtbl.reader(filename))
        for k, v in merger.iteritems():
            writer[k] = v
        writer.close()
        # check our results
        reader = mtbl.reader(merged_filename, verify_checksums=True)
        result = list(reader.iteritems())
        self.assertEqual(
            [
                ('key1', 'val1'),
                ('key17', 'val17'),
                ('key2', 'val2'),
                ('key23', 'val23'),
                ('key3', 'val3'),
                ('key4', 'val4'),
            ],
            result,
        )
