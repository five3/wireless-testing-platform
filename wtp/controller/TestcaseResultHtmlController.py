# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import tornado.web


class TestcaseResultHtmlController(tornado.web.RequestHandler):
    def get(self):
        name=self.get_argument('name','')
        uuid=self.get_argument('uuid', '')
        if name:
            self.render('result.html', name=name, uuid=uuid)
        else:
            self.render('viewResult.html')