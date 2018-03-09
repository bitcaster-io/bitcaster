#!/usr/bin/env python

from setuptools import setup

tests_require = ['bitcaster',
                 'pytest',
                 'tox',
                 'pytest-django',
                 'pytest-coverage',
                 'pytest-echo',
                 'pytest-pythonpath',
                 'vcrpy'
                 ]

setup(
    name='bitcaster-facebook',
    version='0.1',
    description='',
    long_description='',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['bitcaster_facebook'],
    install_requires=['fbchat', ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={'bitcaster': ['facebook = bitcaster_facebook.plugin:Facebook']},
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
