#!/usr/bin/env python

from setuptools import setup

tests_require = ['pytest',
                 'pytest-django',
                 'pytest-coverage',
                 'pytest-echo',
                 'pytest-pythonpath']

setup(
    name='mercury-gmail-oauth',
    version='0.1',
    description='',
    long_description='',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_gmail_oauth'],
    install_requires=['mercury',
                      'requests-oauth'
                      ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={'mercury': ['gmail = mercury_gmail_oauth.plugin:GmailOAuth']},
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
