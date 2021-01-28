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


class SearchTestCase(MtblTestCase):

    def setUp(self):
        super(SearchTestCase, self).setUp()
        # write our test mtbl
        self.filepath = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 'example.mtbl'))
        self.write_mtbl(
            self.filepath,
            [
                ('key1', 'val1'),
                ('key17', 'val17'),
                ('key2', 'val2'),
                ('key23', 'val23'),
                ('key3', 'val3'),
                ('key4', 'val4'),
            ],
        )

    def test_in(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        self.assertTrue(b'key23' in reader)
        self.assertEqual(['val23'], reader['key23'])

    def test_not_in(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        self.assertTrue(b'keyfoo' not in reader)
        self.assertTrue('keyfoo' not in reader)

    def test_not_in_raises_keyerror(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        with self.assertRaises(KeyError):
            reader[b'keyfoo']
        with self.assertRaises(KeyError):
            reader['keyfoo']
