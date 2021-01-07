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

from __future__ import print_function
import sys
import mtbl


def main(mtbl_fname):
    reader = mtbl.reader(mtbl_fname)
    for k, v in reader.items():
        word = k
        count = mtbl.varint_decode(v)
        print('%s\t%s' % (count, word))


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        sys.stderr.write('Usage: %s <MTBL FILE>\n' % sys.argv[0])
        sys.exit(1)
    main(sys.argv[1])
