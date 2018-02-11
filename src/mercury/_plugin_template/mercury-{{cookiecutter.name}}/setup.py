#!/usr/bin/env python

from setuptools import setup

setup(
    name='mercury-{{cookiecutter.name}}',
    version='0.1',
    description='',
    long_description='',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_{{cookiecutter.name}}'],
    entry_points={'mercury': ['{{cookiecutter.name}} = mercury_{{cookiecutter.name}}.plugin:{{cookiecutter.classname}}']},
    license="MIT License",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ])
