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

class ToBytesTestCase(unittest.TestCase):

    def test_string_to_bytes(self):
        expected = b'foobar'
        actual = mtbl.to_bytes('foobar')
        self.assertEqual(actual, expected)
    
    def test_byte_string_to_bytes(self):
        expected = b'foobar'
        actual = mtbl.to_bytes(expected)
        self.assertEqual(actual, expected)

    def test_bytes_varint_to_bytes(self):
        expected = b'\xc4\xb8\xd30\x00\x00\x00'
        actual = mtbl.to_bytes(b'\xc4\xb8\xd30\x00\x00\x00')
        self.assertEqual(actual, expected)

    def test_bytearray_to_bytes(self):
        expected = b'\xde\xad\xbe\xef'
        actual = mtbl.to_bytes(bytearray(b'\xde\xad\xbe\xef'))
        self.assertEqual(actual, expected)
    
    def test_to_bytes_raises_valueerror_with_list(self):
        self.assertRaises(ValueError, mtbl.to_bytes, ['a', 'b', 'c', 'd'])
    
    def test_to_bytes_raises_valueerror_with_int(self):
        self.assertRaises(ValueError, mtbl.to_bytes, 42)
    