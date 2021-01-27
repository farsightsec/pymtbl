# -*- coding: utf-8 -*-
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
import sys

import mtbl

class StrFromBytesTestCase(unittest.TestCase):

    def test_from_bytes_with_byte_string(self):
        expected = 'foobar'
        actual = mtbl.from_bytes(expected.encode('utf-8'))
        self.assertEqual(actual, expected)
    
    @unittest.skipIf(sys.version_info[0] >= 3, 'py3 can handle unicode')
    def test_from_bytes_with_nonascii_byte_string(self):
        expected = '\xe4\xbd\xa0\xe5\xa5\xbd'
        actual = mtbl.from_bytes(u'你好'.encode('utf-8'))
        self.assertEqual(actual, expected)
    
    @unittest.skipIf(sys.version_info[0] == 2, 'py2 can\'t handle unicode')
    def test_from_bytes_with_nonascii_byte_string(self):
        expected = '你好'
        actual = mtbl.from_bytes(expected.encode('utf-8'))
        self.assertEqual(actual, expected)
    
    def test_from_bytes_with_non_string(self):
        expected = b'\x90N'
        actual = mtbl.from_bytes(expected)
        self.assertEqual(actual, expected)
    
    def test_from_bytes_with_non_string2(self):
        expected = b'\xc4\xb8\xd30\x00\x00\x00'
        actual = mtbl.from_bytes(expected)
        self.assertEqual(actual, expected)
    
    def test_from_bytes_with_deadbeef(self):
        expected = b'\xde\xad\xbe\xef'
        actual = mtbl.from_bytes(expected)
        self.assertEqual(actual, expected)

    def test_from_bytes_with_128(self):
        expected = b'\x80\x01' # b'\x80\x01' == mtbl.varint_encode(128)
        actual = mtbl.from_bytes(expected)
        self.assertEqual(actual, expected)
    
    def test_from_bytes_with_byte_string_as_bytes(self):
        expected = b'foobar'
        actual = mtbl.from_bytes(expected, True)
        self.assertEqual(actual, expected)
    
    def test_from_bytes_with_byte_string_as_bytes2(self):
        expected = b'\x01'
        actual = mtbl.from_bytes(expected, True)
        self.assertEqual(actual, expected)