#!usr/bin/env python
# coding: utf-8

import sys

reload(sys)
sys.setdefaultencoding("utf8")

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options
from views import MainHandler

define("port", default=8888, help="run on the given port", type=int)


def main():
    application = tornado.web.Application([
        (r"/", MainHandler),
    ], **options.as_dict())

    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
