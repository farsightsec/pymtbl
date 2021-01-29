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


def write_mtbl(filename, tuples):
    writer = mtbl.writer(filename, compression=mtbl.COMPRESSION_NONE)
    for k, v in tuples:
        writer[k] = v
    writer.close()


class MtblTestCase(unittest.TestCase):

    def write_mtbl(self, filename, tuples):
        # tempfiles would be better but mtbl is bossy about fds :/ (?)
        filepath = os.path.join(
            os.path.dirname(__file__), filename)
        write_mtbl(filepath, tuples)
        self.addCleanup(os.remove, filepath)
        return filepath
