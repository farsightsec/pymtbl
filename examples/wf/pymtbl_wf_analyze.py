#!/usr/bin/env python
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

import string
import sys
import mtbl


def merge_func(key, val0, val1):
    i0 = mtbl.varint_decode(val0)
    i1 = mtbl.varint_decode(val1)
    return mtbl.varint_encode(i0 + i1)


def main(txt_fname, mtbl_fname):
    txt = open(txt_fname)
    sorter = mtbl.sorter(merge_func)
    writer = mtbl.writer(mtbl_fname, compression=mtbl.COMPRESSION_SNAPPY)

    # trim header
    while True:
        line = txt.readline()
        if line.startswith('*** START OF THIS PROJECT GUTENBERG EBOOK'):
            break
    for x in range(0, 5):
        txt.readline()

    for line in txt:
        if line.startswith('End of the Project Gutenberg EBook') or \
           line.startswith('*** END OF THIS PROJECT GUTENBERG EBOOK'):
            break
        for tok in line.strip().split():
            try:
                word = tok.strip(string.punctuation).lower().encode()
            except UnicodeDecodeError:
                # Don't need to encode() in py2 becase 'str' is a synonym for 'bytes' so we can already use it as a key
                word = tok.strip(string.punctuation).lower() #py2
            sorter[word] = mtbl.varint_encode(1)

    sorter.write(writer)


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        sys.stderr.write('Usage: %s <TXT FILE> <MTBL FILE>\n' % sys.argv[0])
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
