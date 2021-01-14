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
from . import MtblTestCase


def merge_func(key, val0, val1):
    return val0 + ' ' + val1


class MergerTestCase(MtblTestCase):

    def setUp(self):
        super(MergerTestCase, self).setUp()       

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
        # check that our results merged as expected
        reader = mtbl.reader(merged_filename, verify_checksums=True)
        result = list(reader.iteritems())
        self.assertEqual(
            [
                ('key1', 'val1 val12'),
                ('key2', 'val2 val22'),
                ('key3', 'val3 val32'),
            ],
            result,
        )
