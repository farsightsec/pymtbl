#!/usr/bin/env python

NAME = 'pymtbl'
VERSION = '0.4.1'

from distutils.core import setup, Command
from distutils.extension import Extension
import unittest

def pkgconfig(*packages, **kw):
    import subprocess
    flag_map = {
            '-I': 'include_dirs',
            '-L': 'library_dirs',
            '-l': 'libraries'
    }
    pkg_config_cmd = 'pkg-config --cflags --libs "%s"' % ' '.join(packages)
    for token in subprocess.check_output(pkg_config_cmd, shell=True).split():
        flag = token[:2]
        arg = token[2:]
        if flag in flag_map:
            kw.setdefault(flag_map[flag], []).append(arg)
    return kw


class Test(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        unittest.TextTestRunner(verbosity=1).run(
            unittest.TestLoader().discover('.'))


try:
    from Cython.Distutils import build_ext
    setup(
        name = NAME,
        version = VERSION,
        ext_modules = [ Extension('mtbl', ['mtbl.pyx'], **pkgconfig('libmtbl >= 1.1.0')) ],
        cmdclass = {
            'build_ext': build_ext,
            'test': Test,
        },
    )
except ImportError:
    import os
    if os.path.isfile('mtbl.c'):
        setup(
            name = NAME,
            version = VERSION,
            ext_modules = [ Extension('mtbl', ['mtbl.c'], **pkgconfig('libmtbl >= 0.8.0')) ],
        )
    else:
        raise
