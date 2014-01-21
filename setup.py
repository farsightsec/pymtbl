#!/usr/bin/env python

NAME = 'pymtbl'
VERSION = '0.2'

from distutils.core import setup
from distutils.extension import Extension
import os

try:
    from Cython.Distutils import build_ext
    setup(
        name = NAME,
        version = VERSION,
        ext_modules = [ Extension('mtbl', ['mtbl.pyx'], libraries = ['mtbl']) ],
        cmdclass = {'build_ext': build_ext},
    )
except ImportError:
    if os.path.isfile('mtbl.c'):
        setup(
            name = NAME,
            version = VERSION,
            ext_modules = [ Extension('mtbl', ['mtbl.c'], libraries = ['mtbl']) ],
        )
    else:
        raise
