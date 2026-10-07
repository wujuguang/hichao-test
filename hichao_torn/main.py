#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options
from hichao_torn.views import MainHandler

define("port", default=8888, help="run on the given port", type=int)


def main():
    application = tornado.web.Application([
        (r"/", MainHandler),
    ], **options.as_dict())

    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
