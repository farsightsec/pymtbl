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
import locale
import random
import string
import sys
import time

import mtbl

report_interval = 10000000
megabyte = 1048576.0


def main(fname, num_keys):
    writer = mtbl.writer(fname, compression=mtbl.COMPRESSION_SNAPPY)

    a = time.time()
    last = a
    total_bytes = 0
    count = 0
    total = 0
    while count < num_keys:
        count += 1
        if random.random() >= 0.5:
            total += 1
            key = ('%010d' % count).encode()
            val = (random.choice(string.ascii_lowercase) * random.randint(1, 50)).encode()
            writer[key] = val
            total_bytes += len(key) + len(val)
        if (count % report_interval) == 0:
            b = time.time()
            last_secs = b - last
            last = b
            sys.stderr.write('wrote %s entries (%s MB) in %s seconds, %s entries/second\n' % (
                locale.format_string('%d', total, grouping=True),
                locale.format_string('%d', total_bytes / megabyte, grouping=True),
                locale.format_string('%f', last_secs, grouping=True),
                locale.format_string('%d', report_interval / last_secs, grouping=True)
                )
            )
    b = time.time()
    total_secs = b - a
    sys.stderr.write('wrote %s total entries (%s MB) in %s seconds, %s entries/second\n' % (
        locale.format_string('%d', total, grouping=True),
        locale.format_string('%d', total_bytes / megabyte, grouping=True),
        locale.format_string('%f', total_secs, grouping=True),
        locale.format_string('%d', total / total_secs, grouping=True)
        )
    )


def usage():
    sys.stderr.write('Usage: %s <MTBL FILENAME> <MAX NUMBER OF KEYS>\n' % sys.argv[0])
    sys.exit(1)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    if len(sys.argv) != 3:
        usage()
    try:
        fname = sys.argv[1]
        num_keys = int(sys.argv[2])
    except:
        usage()
    main(fname, num_keys)
