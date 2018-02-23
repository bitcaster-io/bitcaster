#!/usr/bin/env python

from setuptools import setup

tests_require = ['vcrpy', 'pdbpp', 'pytest', 'pytest-cov',
                 'flake8', 'isort', 'check-manifest']

setup(
    name='mercury-slack-webhook',
    version='0.1',
    description='',
    long_description='',
    install_requires=['mercury', ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    py_modules=['slack_webhook'],
    entry_points={'mercury': ['slack-webhook = slack_webhook.plugin:SlackWebhook']},
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
