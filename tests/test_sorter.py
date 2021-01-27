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
import unittest

import mtbl

def merge_func(key, val0, val1):
    return val0 + b' sorted ' + val1

def make_sort(return_bytes=False):
    # create the sorted mtbl
    sorter = mtbl.sorter(merge_func, return_bytes=return_bytes)
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
    return sorter

class SorterTestCase(unittest.TestCase):

    def test_sort_with_merging(self):
        sorter =  make_sort()

        # check our results
        result = list(sorter.iteritems())
        self.assertEqual(
            [
                ('key0', 'val0 sorted val01'),
                ('key1', 'val1'),
                ('key2', 'val2'),
                ('key3', 'val3 sorted val31')
            ],
            result,
        )

    def test_sort_iteritems_as_bytes(self):
        # create the sorted mtbl but this time read as bytes
        sorter =  make_sort(True)

        result = list(sorter.iteritems())

        self.assertEqual(
            [
                (b'key0', b'val0 sorted val01'),
                (b'key1', b'val1'),
                (b'key2', b'val2'),
                (b'key3', b'val3 sorted val31')
            ],
            result,
        )

    def test_sort_iterreturn_bytes(self):
        # create the sorted mtbl but this time read as bytes
        sorter =  make_sort(True)

        result = list(sorter.iterkeys())

        self.assertEqual(
            [
                (b'key0'),
                (b'key1'),
                (b'key2'),
                (b'key3')
            ],
            result,
        )

    def test_sort_itervalues_as_bytes(self):
        # create the sorted mtbl but this time read as bytes
        sorter =  make_sort(True)

        result = list(sorter.itervalues())

        self.assertEqual(
            [
                (b'val0 sorted val01'),
                (b'val1'),
                (b'val2'),
                (b'val3 sorted val31')
            ],
            result,
        )
