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

import sys
import mtbl


def merge_func(key, val0, val1):
    i0 = mtbl.varint_decode(val0)
    i1 = mtbl.varint_decode(val1)
    return mtbl.varint_encode(i0 + i1)


def main(input_fnames, output_fname):
    merger = mtbl.merger(merge_func)
    writer = mtbl.writer(output_fname, compression=mtbl.COMPRESSION_SNAPPY)
    for fname in input_fnames:
        reader = mtbl.reader(fname)
        merger.add_reader(reader)
    merger.write(writer)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write('Usage: %s <MTBL INPUT FILE> [<MTBL INPUT FILE>...] <MTBL OUTPUT FILE>\n' % sys.argv[0])
        sys.exit(1)
    main(sys.argv[1:-1], sys.argv[-1])
