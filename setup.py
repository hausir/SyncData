# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup, find_packages

VERSION = '0.0.9'

with open('README.md') as f:
    long_description = f.read()

setup(
    name='SyncData',
    version=VERSION,
    license='MIT',
    description='Sync client and server data',
    long_description=long_description,
    url='https://github.com/kuanger/SyncData',
    author='hausir',
    author_email='hausir@icloud.com',
    platforms='any',
    install_requires=[
        'SQLAlchemy>=1.1.4',
        'redis>=2.10.5',
    ],
    packages=find_packages()
)
