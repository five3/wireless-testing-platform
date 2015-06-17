# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen9
'''

import tornado.web


class IndexController(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')