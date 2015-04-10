#!usr/bin/env python
# coding: utf-8

"""该文件copy自源码: tornado.test.util.
"""

from __future__ import absolute_import, division, print_function, with_statement

import os
import socket
import sys

from tornado.testing import bind_unused_port

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    from tornado.testing import unittest

skipIfNonUnix = unittest.skipIf(os.name != 'posix' or sys.platform == 'cygwin', "non-unix platform")
skipOnTravis = unittest.skipIf('TRAVIS' in os.environ, 'timing tests unreliable on travis')
skipIfNoNetwork = unittest.skipIf('NO_NETWORK' in os.environ, 'network access disabled')
skipIfNoIPv6 = unittest.skipIf(not socket.has_ipv6, 'ipv6 support not present')


def refusing_port():
    server_socket, port = bind_unused_port()
    server_socket.setblocking(1)
    client_socket = socket.socket()
    client_socket.connect(("127.0.0.1", port))
    conn, client_addr = server_socket.accept()
    conn.close()
    server_socket.close()
    return client_socket.close, client_addr[1]
