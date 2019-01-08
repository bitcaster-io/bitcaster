#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import codecs
import os
import re

from setuptools import find_packages, setup

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, 'src', 'bitcaster', '__init__.py')
BUILD_ASSETS = os.environ.get('BITCASTER_BUILD_ASSETS', '1') != '0'

rel = lambda *args: os.path.join(ROOT, 'src', 'requirements', *args)

_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    version = str(ast.literal_eval(_version_re.search(content).group(1)))
    name = str(ast.literal_eval(_name_re.search(content).group(1)))


def fread(fname):
    return open(rel(fname)).read()


def read(*files):
    content = []
    for f in files:
        content.extend(codecs.open(os.path.join(ROOT, 'src', 'requirements', f), 'r').readlines())
    return '\n'.join(filter(lambda l: not l.startswith('-'), content))


# install_requires = read('install.pip')
# test_requires = read('testing.pip')

readme = codecs.open('README.md').read()

setup(name=name,
      version=version,
      description="""A short description of the project.""",
      long_description=readme,
      author='Stefano Apostolico',
      author_email='s.apostolico@gmail.com',
      url='https://github.com/bitcaster-io/bitcaster',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'bitcaster = bitcaster.cli:main',
          ],
      },
      license='MIT',
      zip_safe=False,
      keywords='',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Framework :: Django',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6'
      ])
