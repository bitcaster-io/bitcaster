#!/usr/bin/env python

from setuptools import setup

setup(
    name='mercury-gmail',
    version='0.1',
    description='',
    long_description='',
    install_requires=['mercury'],
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_gmail'],
    entry_points={'mercury': ['gmail = mercury_gmail.plugin:Gmail']},
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
