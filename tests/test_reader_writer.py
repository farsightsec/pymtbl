# Copyright (c) 2015-2019 by Farsight Security, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import unittest

import mtbl


class WriterTestCase(unittest.TestCase):

    def test_misordered_write_raises_keyordererror(self):
        filepath = os.path.join(
            os.path.dirname(__file__), 'example.mtbl')
        writer = mtbl.writer(filepath, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, filepath)
        writer[b'key1'] = b'val1'
        writer[b'key17'] = b'val17'
        writer[b'key2'] = b'val2'
        writer[b'key23'] = b'val23'
        writer[b'key3'] = b'val3'
        writer[b'key4'] = b'val4'
        with self.assertRaises(mtbl.KeyOrderError):
            writer[b'key05'] = b'val05'


class ReaderTestCase(unittest.TestCase):

    def setUp(self):
        super(ReaderTestCase, self).setUp()
        # write our test mtbl
        self.filepath = os.path.join(
            os.path.dirname(__file__), 'example.mtbl')
        writer = mtbl.writer(self.filepath, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, self.filepath)
        writer[b'key1'] = b'val1'
        writer[b'key17'] = b'val17'
        writer[b'key2'] = b'val2'
        writer[b'key23'] = b'val23'
        writer[b'key3'] = b'val3'
        writer[b'key4'] = b'val4'
        writer.close()

    def test_get_range(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        result = list(reader.get_range(b'key19', b'key23'))
        self.assertEqual([(b'key2', b'val2'), (b'key23', b'val23')], result)

    def test_get_prefix(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        result = list(reader.get_prefix(b'key2'))
        self.assertEqual([(b'key2', b'val2'), (b'key23', b'val23')], result)

    def test_iteritems(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        result = list(reader.iteritems())
        self.assertEqual(
            [
                (b'key1', b'val1'),
                (b'key17', b'val17'),
                (b'key2', b'val2'),
                (b'key23', b'val23'),
                (b'key3', b'val3'),
                (b'key4', b'val4'),
            ],
            result,
        )
