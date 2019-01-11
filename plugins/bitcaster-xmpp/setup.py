#!/usr/bin/env python

from setuptools import find_packages, setup

tests_require = ['bitcaster',
                 'pytest',
                 'pytest-django',
                 'pytest-coverage',
                 'pytest-echo',
                 'pytest-pythonpath']
reqs = ['pyxmpp2']
setup(
    name='bitcaster-xmpp',
    version='0.1',
    description='',
    long_description='',
    install_requires=[],
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    package_dir={'': '.'},
    packages=find_packages('.'),
    include_package_data=True,
    package_data={
        'bitcaster_xmpp': ['*.png', ],
    },
    entry_points={'bitcaster': ['xmpp = bitcaster_xmpp.plugin:Xmpp']},
    license='MIT License',
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
