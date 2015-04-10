#!usr/bin/env python
# coding: utf-8

"""该文件copy自源码: tornado.test.runtests.py, 但做了删减.
"""

from __future__ import absolute_import, division, print_function, with_statement
import gc
import locale  # system locale module, not tornado.locale
import logging
import operator
import textwrap
import sys
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.netutil import Resolver
from tornado.options import define, options, add_parse_callback
from tornado.test.util import unittest
import warnings
import tornado.testing
from tornado.platform.auto import monotonic_time

try:
    reduce  # py2
except NameError:
    from functools import reduce  # py3

TEST_MODULES = ['hichao_torn.test.test', ]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


class TornadoTextTestRunner(unittest.TextTestRunner):
    def run(self, test):
        result = super(TornadoTextTestRunner, self).run(test)
        if result.skipped:
            skip_reasons = set(reason for (test, reason) in result.skipped)
            self.stream.write(textwrap.fill("Some tests were skipped because: %s" % ", ".join(sorted(skip_reasons))))
            self.stream.write("\n")
        return result


class LogCounter(logging.Filter):
    def __init__(self, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.warning_count = self.error_count = 0

    def filter(self, record):
        if record.levelno >= logging.ERROR:
            self.error_count += 1
        elif record.levelno >= logging.WARNING:
            self.warning_count += 1
        return True


def main():
    warnings.filterwarnings("error")
    warnings.filterwarnings("ignore", category=ImportWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning, message="Please use assert.* instead")
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning, message="Please use assert.* instead")

    logging.getLogger("ky_hichao.access").setLevel(logging.CRITICAL)

    define('httpclient', type=str, default=None,
           callback=lambda s: AsyncHTTPClient.configure(s, defaults=dict(allow_ipv6=False)))

    define('ioloop', type=str, default=None)
    define('ioloop_time_monotonic', default=False)
    define('resolver', type=str, default=None, callback=Resolver.configure)
    define('debug_gc', type=str, multiple=True,
           help="A comma-separated list of gc module debug constants, "
                "e.g. DEBUG_STATS or DEBUG_COLLECTABLE,DEBUG_OBJECTS",
           callback=lambda values: gc.set_debug(reduce(operator.or_, (getattr(gc, v) for v in values))))

    define('locale', type=str, default=None, callback=lambda x: locale.setlocale(locale.LC_ALL, x))

    def configure_ioloop():
        kwargs = {}
        if options.ioloop_time_monotonic:
            if monotonic_time is None:
                raise RuntimeError("monotonic clock not found")
            kwargs['time_func'] = monotonic_time

        if options.ioloop or kwargs:
            IOLoop.configure(options.ioloop, **kwargs)

    add_parse_callback(configure_ioloop)
    log_counter = LogCounter()
    add_parse_callback(lambda: logging.getLogger().handlers[0].addFilter(log_counter))

    kwargs = {}
    if sys.version_info >= (3, 2):
        kwargs['warnings'] = False

    kwargs['testRunner'] = TornadoTextTestRunner
    try:
        tornado.testing.main(**kwargs)
    finally:
        if log_counter.warning_count > 0 or log_counter.error_count > 0:
            logging.error("logged %d warnings and %d errors", log_counter.warning_count, log_counter.error_count)
            sys.exit(1)


if __name__ == '__main__':
    main()
