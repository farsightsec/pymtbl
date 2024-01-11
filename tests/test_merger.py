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

import mtbl
from tests import MtblTestCase


def merge_func_str(key, val0, val1):
    s = [val0, val1]
    s.sort()
    return s[0] + b' ' + s[1]

def merge_func_ints(_, val0, val1):
    i0 = mtbl.varint_decode(val0)
    i1 = mtbl.varint_decode(val1)
    return mtbl.varint_encode(i0 + i1)


class MergerTestCase(MtblTestCase):

    def setUp(self):
        super(MergerTestCase, self).setUp()

    def do_merge(self, merge_func):
        # create the merged mtbl
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
        # return a reader so we can check our results
        reader = mtbl.reader(merged_filename, verify_checksums=True)
        return list(reader.iteritems())

    def test_merge_and_iteritems_no_merge(self):
        # write two mtbls that don't have the same keys
        self.mtbls_to_merge = []
        for filename, tuples in [
                ('left.mtbl',
                 [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')]),
                ('right.mtbl',
                 [('key17', 'val17'), ('key23', 'val23'), ('key4', 'val4')]),
        ]:
            m = self.write_mtbl(filename, tuples)
            self.mtbls_to_merge.append(m)
        result = self.do_merge(merge_func_str)
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


    def test_merge_and_iteritems_with_merge(self):
        # write two mtbls with the same keys
        self.mtbls_to_merge = []
        for filename, tuples in [
                ('left.mtbl',
                 [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')]),
                ('right.mtbl',
                 [('key1', 'val12'), ('key2', 'val22'), ('key3', 'val32')]),
        ]:
            m = self.write_mtbl(filename, tuples)
            self.mtbls_to_merge.append(m)
        result = self.do_merge(merge_func_str)
        self.assertEqual(
            [
                ('key1', 'val1 val12'),
                ('key2', 'val2 val22'),
                ('key3', 'val3 val32'),
            ],
            result,
        )

    def test_merge_with_ints(self):
        # write two mtbls with the same keys
        self.mtbls_to_merge = []
        for filename, tuples in [
                ('left.mtbl',
                 [('key1', mtbl.varint_encode(1)), ('key2', mtbl.varint_encode(42)), ('key3', mtbl.varint_encode(12345))]),
                ('right.mtbl',
                 [('key1', mtbl.varint_encode(2)), ('key2', mtbl.varint_encode(1)), ('key3', mtbl.varint_encode(128))]),
        ]:
            m = self.write_mtbl(filename, tuples)
            self.mtbls_to_merge.append(m)
        result = self.do_merge(merge_func_ints)
        result = [(k, mtbl.varint_decode(v)) for k,v in result]
        self.assertEqual(
            [
                ('key1', 3),
                ('key2', 43),
                ('key3', 12345 + 128),
            ],
            result,
        )

    def test_merge_iteritems_as_bytes(self):
        self.mtbls_to_merge = []
        for filename, tuples in [
                ('left.mtbl',
                 [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')]),
                ('right.mtbl',
                 [('key1', 'val17'), ('key2', 'val23'), ('key4', 'val4')]),
        ]:
            m = self.write_mtbl(filename, tuples)
            self.mtbls_to_merge.append(m)
        merger = mtbl.merger(merge_func_str, return_bytes=True)
        for filename in self.mtbls_to_merge:
            merger.add_reader(mtbl.reader(filename))

        result = list(merger.iteritems())

        self.assertEqual([
            (b'key1', b'val1 val17'),
            (b'key2', b'val2 val23'),
            (b'key3', b'val3'),
            (b'key4', b'val4'),
        ],
        result)
