# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import tornado.web
from models.TestcaseResultDao import TestcaseResultDao

class TestcaseResultHtmlController(tornado.web.RequestHandler):
    def get(self):
        name=self.get_argument('name','')
        uuid=self.get_argument('uuid', '')
        if name:
            results = TestcaseResultDao().retrieveLastOne(name)
            self.render('result.html', name=name, uuid=uuid, parent_uuid=results[3])
        else:
            self.render('viewResult.html')