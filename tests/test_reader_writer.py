# -*- coding: utf-8 -*-
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
        writer[b'key1'] = 'val1'
        writer['key17'] = b'val17'
        writer['key2'] = 'val2'
        writer['key23'] = 'val23'
        writer[b'key3'] = b'val3'
        writer[b'key4'] = b'val4'
        with self.assertRaises(mtbl.KeyOrderError):
            writer['key05'] = 'val05'
        with self.assertRaises(mtbl.KeyOrderError):
            writer[b'key05'] = b'val05'
        # this one should not raise mtbl.KeyOrderError
        writer['key5'] = 'key5'


class ReaderTestCase(unittest.TestCase):

    def setUp(self):
        # write our test mtbl
        self.filepath = os.path.join(
            os.path.dirname(__file__), 'example.mtbl')
        writer = mtbl.writer(self.filepath, compression=mtbl.COMPRESSION_NONE)
        self.addCleanup(os.remove, self.filepath)
        
        writer[b'\x00'] = b'\x01'
        writer[b'\x61'] = b'a'
        writer['key0'] = b'\xff'
        writer[b'key1'] = b'val1'
        writer[b'key17'] = b'val17'
        writer[b'key2'] = b'val2'
        writer[b'key23'] = b'val23'
        writer[b'key3'] = b'val3'
        writer[b'\x90N'] = b'\xaa'
        writer['你好，世界'] = 'hello world'
        writer.close()

        self.reader = mtbl.reader(self.filepath, verify_checksums=True)
    
    def test_has_key_true(self):
        self.assertTrue(self.reader.has_key('a'))
        self.assertTrue(self.reader.has_key(b'\x61'))
        self.assertTrue(self.reader.has_key('key17'))
        self.assertTrue(self.reader.has_key(b'key17'))
    
    def test_has_key_false(self):        
        self.assertFalse(self.reader.has_key('key42'))
        self.assertFalse(self.reader.has_key(b'key42'))
        self.assertFalse(self.reader.has_key('nope'))
    
    def test_get(self):        
        self.assertEqual(self.reader.get('你好，世界'), ['hello world'])
        self.assertEqual(self.reader.get('a'), ['a'])
        self.assertEqual(self.reader.get(b'\x61'), ['a'])   
        self.assertEqual(self.reader.get(b'\x90N'), [b'\xaa'])
    
    def test_get_as_bytes(self):
        self.reader = mtbl.reader(self.filepath, verify_checksums=True, return_bytes=True)
        self.assertEqual(self.reader.get(b'\xe4\xbd\xa0\xe5\xa5\xbd\xef\xbc\x8c\xe4\xb8\x96\xe7\x95\x8c'), [b'hello world'])
        self.assertEqual(self.reader.get(b'a'), [b'a'])
        self.assertEqual(self.reader.get(b'\x61'), [b'a'])   
        self.assertEqual(self.reader.get(b'\x90N'), [b'\xaa'])
    
    def test_get_keyerror_returns_none(self):
        self.assertEqual(self.reader.get('nope'), None)

    def test_get_default(self):
        expected = 'foobar'
        self.assertEqual(self.reader.get('nope', expected), expected)

    def test_get_range(self):
        result = list(self.reader.get_range('key19', 'key23'))
        self.assertEqual([('key2', 'val2'), ('key23', 'val23')], result)
    
    def test_get_range_as_bytes(self):
        self.reader = mtbl.reader(self.filepath, verify_checksums=True, return_bytes=True)
        result = list(self.reader.get_range('key19', 'key23'))
        self.assertEqual([(b'key2', b'val2'), (b'key23', b'val23')], result)

    def test_get_prefix(self):
        result = list(self.reader.get_prefix(b'key2'))
        self.assertEqual([('key2', 'val2'), ('key23', 'val23')], result)
    
    def test_get_prefix_string(self):
        result = list(self.reader.get_prefix('key'))
        self.assertEqual(
            [
                ('key0', b'\xff'),
                ('key1', 'val1'),
                ('key17', 'val17'),                
                ('key2', 'val2'),
                ('key23', 'val23'),
                ('key3', 'val3'),
            ], result)
    
    def test_get_prefix_string_as_bytes(self):
        self.reader = mtbl.reader(self.filepath, verify_checksums=True, return_bytes=True)
        result = list(self.reader.get_prefix('key'))
        self.assertEqual(
            [
                (b'key0', b'\xff'),
                (b'key1', b'val1'),
                (b'key17', b'val17'),                
                (b'key2', b'val2'),
                (b'key23', b'val23'),
                (b'key3', b'val3'),
            ], result)
    
    def test_iterkeys(self):
        result = list(self.reader.iterkeys())
        self.assertEqual(
            [
                '\x00',                
                'a',
                'key0',
                'key1',
                'key17',
                'key2',
                'key23',
                'key3',
                b'\x90N',
                '你好，世界',
            ],
            result,
        )
    
    def test_iterkeys_as_bytes(self):
        self.reader = mtbl.reader(self.filepath, verify_checksums=True, return_bytes=True)
        result = list(self.reader.iterkeys())
        self.assertEqual(
            [
                b'\x00',                
                b'a',
                b'key0',
                b'key1',
                b'key17',
                b'key2',
                b'key23',
                b'key3',
                b'\x90N',
                b'\xe4\xbd\xa0\xe5\xa5\xbd\xef\xbc\x8c\xe4\xb8\x96\xe7\x95\x8c',
            ],
            result,
        )
    
    def test_itervalues(self):
        result = list(self.reader.itervalues())
        self.assertEqual(
            [
                '\x01',                
                'a',
                b'\xff',
                'val1',
                'val17',
                'val2',
                'val23',
                'val3',
                b'\xaa',
                'hello world',
            ],
            result,
        )
    
    def test_itervalues_as_bytes(self):
        self.reader = mtbl.reader(self.filepath, verify_checksums=True, return_bytes=True)
        result = list(self.reader.itervalues())
        self.assertEqual(
            [
                b'\x01',                
                b'a',
                b'\xff',
                b'val1',
                b'val17',
                b'val2',
                b'val23',
                b'val3',
                b'\xaa',
                b'hello world',
            ],
            result,
        )

    def test_iteritems(self):
        result = list(self.reader.iteritems())
        self.assertEqual(
            [
                ('\x00', '\x01'),                
                ('a', 'a'),
                ('key0', b'\xff'),
                ('key1', 'val1'),
                ('key17', 'val17'),
                ('key2', 'val2'),
                ('key23', 'val23'),
                ('key3', 'val3'),
                (b'\x90N', b'\xaa'),
                ('你好，世界', 'hello world'),
            ],
            result,
        )
    
    def test_iteritems_as_bytes(self):
        self.reader = mtbl.reader(self.filepath, verify_checksums=True, return_bytes=True)
        result = list(self.reader.iteritems())
        self.assertEqual(
            [
                (b'\x00', b'\x01'),                
                (b'a', b'a'),
                (b'key0', b'\xff'),
                (b'key1', b'val1'),
                (b'key17', b'val17'),
                (b'key2', b'val2'),
                (b'key23', b'val23'),
                (b'key3', b'val3'),
                (b'\x90N', b'\xaa'),
                (b'\xe4\xbd\xa0\xe5\xa5\xbd\xef\xbc\x8c\xe4\xb8\x96\xe7\x95\x8c', b'hello world'),
            ],
            result,
        )
