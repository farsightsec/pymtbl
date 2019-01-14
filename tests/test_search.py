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


class SearchTestCase(MtblTestCase):

    def setUp(self):
        super(SearchTestCase, self).setUp()
        # write our test mtbl
        self.filepath = os.path.join(
            os.path.dirname(__file__), 'example.mtbl')
        self.write_mtbl(
            self.filepath,
            [
                (b'key1', b'val1'),
                (b'key17', b'val17'),
                (b'key2', b'val2'),
                (b'key23', b'val23'),
                (b'key3', b'val3'),
                (b'key4', b'val4'),
            ],
        )

    def test_in(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        self.assertTrue(b'key23' in reader)
        self.assertEqual([b'val23'], reader[b'key23'])

    def test_not_in(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        self.assertTrue(b'keyfoo' not in reader)

    def test_not_in_raises_keyerror(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        with self.assertRaises(KeyError):
            reader[b'keyfoo']
