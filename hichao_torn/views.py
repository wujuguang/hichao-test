#!usr/bin/env python
# coding: utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from hichao_test import tornado_request


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    @tornado_request
    def post(self, *args, **kwargs):
        self.write("hello, world, world")
