#!/usr/bin/env python

from setuptools import find_packages, setup

tests_require = ['bitcaster',
                 'pytest',
                 'pytest-django',
                 'pytest-coverage',
                 'pytest-echo',
                 'pytest-pythonpath']

setup(
    name='bitcaster-gmail-oauth',
    version='0.1',
    description='',
    long_description='',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    package_dir={'': '.'},
    packages=find_packages('.'),
    include_package_data=True,
    package_data={
        'bitcaster_gmail_oauth': ['*.png', ],
    },
    install_requires=['requests-oauthlib',
                      'google-api-python-client',
                      ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={'bitcaster': ['gmail = bitcaster_gmail_oauth.plugin:GmailOAuth']},
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
