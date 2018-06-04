#!/usr/bin/env python

from setuptools import find_packages, setup

tests_require = ['bitcaster'
                 'pytest',
                 'pytest-django',
                 'pytest-coverage',
                 'pytest-echo',
                 'pytest-pythonpath']

setup(
    name='bitcaster-twilio',
    version='0.1',
    description='',
    long_description='',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    package_dir={'': '.'},
    packages=find_packages('.'),
    include_package_data=True,
    package_data={
        'bitcaster_twilio': ['*.png', ],
    },
    install_requires=['twilio', 'lxml'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={'bitcaster': ['twilio = bitcaster_twilio.plugin:Twilio']},
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
