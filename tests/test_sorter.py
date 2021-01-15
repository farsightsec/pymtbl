# Copyright (c) 2015-2021 by Farsight Security, Inc.
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
    return val0 + ' sorted ' + val1

class SorterTestCase(MtblTestCase):
    def setUp(self):
        super(SorterTestCase, self).setUp()
    
    def test_sort_with_merging(self):
        # create the sorted mtbl
        sorter = mtbl.sorter(merge_func)
        sorted_filename = os.path.join(os.path.dirname(__file__), 'sorted.mtbl')
        writer = mtbl.writer(
            sorted_filename, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, sorted_filename)

        test_data = [
            ('key0', 'val0'),
            ('key0', 'val01'),
            ('key1', 'val1'),
            ('key2', 'val2'),
            ('key3', 'val3'),
            ('key3', 'val31')
        ]
        for d in test_data:
            sorter[d[0]] = d[1]

        # write the mtbl
        sorter.write(writer)
        writer.close()

        # check our results
        reader = mtbl.reader(sorted_filename, verify_checksums=True)
        result = list(reader.iteritems())
        self.assertEqual(
            [
                ('key0', 'val0 sorted val01'),
                ('key1', 'val1'),
                ('key2', 'val2'),
                ('key3', 'val3 sorted val31')
            ],
            result,
        )
