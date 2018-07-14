#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import codecs
import os
import re
import subprocess
import sys
from distutils.errors import DistutilsError
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.sdist import sdist

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
    return "\n".join(filter(lambda l: not l.startswith('-'), content))


def check(cmd, filename):
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    f = os.path.join('src', 'requirements', filename)
    reqs = codecs.open(os.path.join(ROOT, f), 'r').readlines()
    existing = {name[:-1] for name in reqs if name and not name.startswith('-')}
    declared = {name for name in out.stdout.decode('utf8').split("\n") if name and not name.startswith('-')}
    if existing - declared:
        error = f"Unknown libraries: {existing-declared}"
    else:
        error = f"Missing libraries: {declared-existing}"

    if existing != declared:
        msg = f"""Requirements file not updated.

{error}

To fix run:

{' '.join(cmd)} > {f}

"""
        raise DistutilsError(msg)


class SDistCommand(sdist):

    def run(self):
        checks = {'install.pip': ['pipenv', 'lock', '--requirements'],
                  'testing.pip': ['pipenv', 'lock', '-d', '--requirements']}

        for filename, cmd in checks.items():
            check(cmd, filename)
        if not Path(__file__).parent / 'src' / 'bitcaster' / 'static' / 'dist':
            env = dict(os.environ)
            env['NODE_ENV'] = 'production'
            subprocess.check_output(['node_modules/.bin/webpack', '--bail'],
                                    cwd=os.path.abspath(os.path.dirname(sys.modules['__main__'].__file__)),
                                    env=env)
        super().run()


install_requires = read('install.pip')
test_requires = read('testing.pip')

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
      install_requires=install_requires,
      tests_require=test_requires,
      extras_require={
          'dev': test_requires,
          'test': test_requires,
      },
      cmdclass={
          'sdist': SDistCommand,
      },
      entry_points={
          'console_scripts': [
              'bitcaster = bitcaster.cli:main',
          ],
      },
      license="MIT",
      zip_safe=False,
      keywords='',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Framework :: Django',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6'
      ])
