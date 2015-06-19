#!/usr/bin/env python
# coding=utf-8

import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'CHANGELOG.rst')).read()

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
zip_safe = not on_rtd

version = '0.2.2'

setup(
    name='hichao-test',
    version=version,
    description="hichao-test is a Tool that HTTP Test base on linux curl.",
    long_description=README + '\n\n' + NEWS,
    license='MIT License',
    author='kylinfish',
    author_email='kylinfish@126.com',
    keywords='hichao-test',
    url='https://github.com/wujuguang/hichao-test.git',
    packages=find_packages(),
    include_package_data=True,
    platforms=["any"],
    zip_safe=zip_safe,
    entry_points={
        'console_scripts': [
            'hichao_curl = hichao_test.curl_reader:main',
            'hichao_distinct = hichao_test.curl_builder:main'
        ]
    },
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License'
    ]
)