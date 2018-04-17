
import os
import unittest

import mtbl


class WriterTestCase(unittest.TestCase):

    def test_misordered_write_raises_keyordererror(self):
        filepath = os.path.join(
            os.path.dirname(__file__), 'example.mtbl')
        writer = mtbl.writer(filepath, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, filepath)
        writer['key1'] = 'val1'
        writer['key17'] = 'val17'
        writer['key2'] = 'val2'
        writer['key23'] = 'val23'
        writer['key3'] = 'val3'
        writer['key4'] = 'val4'
        with self.assertRaises(mtbl.KeyOrderError):
            writer['key05'] = 'val05'


class ReaderTestCase(unittest.TestCase):

    def setUp(self):
        super(ReaderTestCase, self).setUp()
        # write our test mtbl
        self.filepath = os.path.join(
            os.path.dirname(__file__), 'example.mtbl')
        writer = mtbl.writer(self.filepath, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, self.filepath)
        writer['key1'] = 'val1'
        writer['key17'] = 'val17'
        writer['key2'] = 'val2'
        writer['key23'] = 'val23'
        writer['key3'] = 'val3'
        writer['key4'] = 'val4'
        writer.close()

    def test_get_range(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        result = list(reader.get_range('key19', 'key23'))
        self.assertEqual([('key2', 'val2'), ('key23', 'val23')], result)

    def test_get_prefix(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        result = list(reader.get_prefix('key2'))
        self.assertEqual([('key2', 'val2'), ('key23', 'val23')], result)

    def test_iteritems(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
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
