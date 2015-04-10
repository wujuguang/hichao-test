#!usr/bin/env python
# coding: utf-8

"""
该文件copy自源码: tornado.test.__main__.py

Shim to allow python -m tornado.test.
This only works in python 2.7+.

允许运行 python -m tornado.test 的垫片.
它仅仅在python 2.7+ 工作.
"""

from __future__ import absolute_import, division, print_function, with_statement

from hichao_torn.test.runtests import all, main

# tornado.testing.main autodiscovery relies on 'all' being present in
# the main module, so import it here even though it is not used directly.
# The following line prevents a pyflakes warning.

all = all
main()
