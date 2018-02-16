#!/usr/bin/env python

from setuptools import setup

setup(
    name='mercury-xmpp',
    version='0.1',
    description='',
    long_description='',
    install_requires=['mercury',
                      'pyxmpp2',
                      'pyasn1-modules==0.1.5',
                      'sleekxmpp==1.3.3'
                      ],
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_xmpp'],
    entry_points={'mercury': ['xmpp = mercury_xmpp.plugin:Xmpp']},
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
