#!/usr/bin/env python

from setuptools import setup

setup(
    name='mercury-whatsapp',
    version='0.1',
    description='',
    long_description='',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['mercury_whatsapp'],
    entry_points={'mercury': ['whatsapp = mercury_whatsapp.plugin:WhatsApp']},
    install_requires=['pywhatsapp'],
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
