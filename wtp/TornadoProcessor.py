# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen
'''

import os

import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import tornado.options
import tornado.web

from controller import *
from models.Configuration import Configuration
from manager.DeviceManager import DeviceManager
from manager.ThreadPoolManager import ThreadPoolManager

class TornadoProcessor:
    def __init__(self):
        Configuration()
        DeviceManager()
        ThreadPoolManager()

        define('port', 80, None, int)
        define("debug", default=True, help="Debug Mode", type=bool)

    def run(self):
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        static_path = os.path.join(os.path.dirname(__file__), "static")
        settings = {'static_path': static_path,
                    'template_path' : template_path,
                    }
        tornado.options.parse_command_line()
        application = tornado.web.Application(handlers=[(r'/', IndexController),
                                                        (r'/devices', DeviceInfoController),
                                                        (r'/process', ProcessController),
                                                        (r'/result', TestcaseResultController),
                                                        (r'/resultList', TestcaseResultListController),
                                                        (r'/resultHtml', TestcaseResultHtmlController),
                                                        (r'/resultListHtml', TestcaseResultListHtmlController),
                                                        (r'/about', AboutController)
                                                        ], **settings)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
