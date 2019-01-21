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
        # write two mtbls to be merged
        self.mtbls_to_merge = []
        for filename, tuples in [
                ('left.mtbl',
                 [(b'key1', b'val1'), (b'key2', b'val2'), (b'key3', b'val3')]),
                ('right.mtbl',
                 [(b'key17', b'val17'), (b'key23', b'val23'), (b'key4', b'val4')]),
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
                (b'key1', b'val1'),
                (b'key17', b'val17'),
                (b'key2', b'val2'),
                (b'key23', b'val23'),
                (b'key3', b'val3'),
                (b'key4', b'val4'),
            ],
            result,
        )
