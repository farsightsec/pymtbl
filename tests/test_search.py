
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
                ('key1', 'val1'),
                ('key17', 'val17'),
                ('key2', 'val2'),
                ('key23', 'val23'),
                ('key3', 'val3'),
                ('key4', 'val4'),
            ],
        )

    def test_in(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        self.assertTrue('key23' in reader)
        self.assertEqual(['val23'], reader['key23'])

    def test_not_in(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        self.assertTrue('keyfoo' not in reader)

    def test_not_in_raises_keyerror(self):
        reader = mtbl.reader(self.filepath, verify_checksums=True)
        with self.assertRaises(KeyError):
            reader['keyfoo']
