#!usr/bin/env python
# coding: utf-8

"""根据tornado.testing 使用案例, 小试.
"""

from tornado.web import Application
from tornado.testing import gen_test, AsyncTestCase, AsyncHTTPTestCase, AsyncHTTPClient
from hichao_torn.views import MainHandler

local_host = "http://localhost:8888"


class MyTestCase(AsyncTestCase):
    """This test uses coroutine style.
    """

    @gen_test
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch(local_host)

        # Test contents of response
        self.assertIn("Hello, world", response.body)


class MyTestCase2(AsyncTestCase):
    """This test uses argument passing between self.stop and self.wait.
    """

    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch(local_host, self.stop)
        response = self.wait()

        # Test contents of response
        self.assertIn("Hello, world", response.body)


class MyTestCase3(AsyncTestCase):
    """This test uses an explicit callback-based style.
    """

    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch(local_host, self.handle_fetch)
        self.wait()

    def handle_fetch(self, response):
        """Test contents of response (failures and exceptions here
        will cause self.wait() to throw an exception and end the test).

        Exceptions thrown here are magically propagated to self.wait()
        in test_http_fetch() via stack_context.
        """

        self.assertIn("Hello, world", response.body)
        self.stop()


class MyHTTPTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application([('/', MainHandler)])

    def test_homepage(self):
        """The following two lines are equivalent to response = self.fetch('/')
        but are shown in full here to demonstrate explicit use of self.stop and self.wait.
        """

        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()

        # test contents of response
        self.assertIn("Hello, world", response.body)
