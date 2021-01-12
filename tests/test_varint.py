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

import unittest
from mtbl import *


class TestVarint(unittest.TestCase):
    def test_0_ret_type(self):
        assert type(varint_encode(100)) == bytes

    def test_0_arg_type(self):
        x = varint_decode(b'\xc4\xb8\xd30\x00\x00\x00')
        x = varint_decode(bytearray(b'\xc4\xb8\xd30\x00\x00\x00'))

        # py2 will accept the following, but py3 will not
        # bc in py2 type 'bytes' is a synonym for type 'str'
        # note that you cant reliably use .encode() since these are
        # byte buffers and not guaranteed to be some sort of encoded string
        # so the following should be avoided in client scripts or you
        # risk portability
        # x = varint_decode('\xc4\xb8\xd30\x00\x00\x00')

    def test_inverse(self):
        assert 123 == varint_decode(varint_encode(123))

    def test_length(self):
        assert 1 == varint_length(1)
        assert 2 == varint_length(1000)
        assert 2 == varint_length_packed(varint_encode(1000))
        assert 4 == varint_length_packed(bytearray(b'\xc4\xb8\xd30\x00\x00\x00'))
        assert 4 == varint_length_packed(b'\xc4\xb8\xd30\x00\x00\x00')
        assert 1 == varint_length_packed('foo')

    def test_insitu_decode(self):
        assert 102030404 == varint_decode(bytearray(b'\xc4\xb8\xd30\x00\x00\x00'))


if __name__ == "__main__":
    unittest.main()
