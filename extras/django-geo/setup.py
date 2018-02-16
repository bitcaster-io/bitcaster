#!/usr/bin/env python
import ast
import codecs
import os
import re
from setuptools import find_packages, setup

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, 'src', 'geo', '__init__.py')

_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    version = str(ast.literal_eval(_version_re.search(content).group(1)))
    name = str(ast.literal_eval(_name_re.search(content).group(1)))


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), "r").read()


tests_require = read('src/requirements/testing.pip')
install_requires = read('src/requirements/install.pip')
dev_require = read('src/requirements/develop.pip')

setup_requires = []

setup(
    name=name,
    version=version,
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    url='https://github.com/saxix/django-geo',
    long_description=read("README.rst"),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    extras_require={
        'tests': tests_require,
        'dev': dev_require + tests_require,
    },
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Intended Audience :: Developers'
    ]
)
