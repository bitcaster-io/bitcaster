#!/usr/bin/env python

from setuptools import setup

setup(
    name='mercury-facebook',
    version='0.1',
    description='',
    long_description='',
    install_requires=['mercury',],
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_facebook'],
    entry_points={'mercury': ['facebook = mercury_facebook.plugin:Facebook']},
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
