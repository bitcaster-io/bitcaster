#!/usr/bin/env python

from setuptools import setup

tests_requires = ['pytest',
                  'pytest-django',
                  'pytest-coverage',
                  'pytest-pythonpath']

setup(
    name='mercury-skype',
    version='0.1',
    description='',
    long_description='',
    install_requires=['mercury', 'skpy'],
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_skype'],
    entry_points={'mercury': ['skype = mercury_skype.plugin:Skype']},
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
