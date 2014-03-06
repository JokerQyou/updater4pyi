#!/usr/bin/env python

import os
import os.path
#from distutils.core import setup
from setuptools import setup

import updater4pyi.upd_version


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(name='updater4pyi',
      version=updater4pyi.upd_version.version_str,
      description='Lightweight library to add software auto-update functionality to pyinstaller-packaged applications',
      long_description=read('README.txt'),
      author='Philippe Faist',
      # obfuscate e-mail in source script, will be in clear in the package
      author_email=("".join([chr(ord(x)+1) for x in 'oghkhood-e`hrs?aktdvhm-bg'])),
      url='https://github.com/phfaist/updater4pyi/',
      license='BSD',
      packages=['updater4pyi'],
      py_modules=[],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Software Distribution',
          ],
      )
