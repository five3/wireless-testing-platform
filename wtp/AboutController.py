# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen9
'''

import json

import lazyxml
import tornado.web

from DeviceManager import DeviceManager


class AboutController(tornado.web.RequestHandler):
    def get(self):
        self.render('about.html')