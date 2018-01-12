#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2018/1/11 8:15
#--RevisedDate:   
#------------------------------------

import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from main import app

if __name__ == "__main__":

    if len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        port = 5000

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()