# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import tornado.web
from models.TestcaseResultDao import TestcaseResultDao
from models.TestcaseResultDao import TestcaseNumDao

class TestcaseResultListHtmlController(tornado.web.RequestHandler):
    def get(self):
        uuid=self.get_argument('uuid', '')
        if not uuid:
            raise Exception

        results = TestcaseResultDao().retrieveAllInOneJob(uuid)

        if not results:
            self.render('msg.html', msg={"successful": False, 'msg':'no result'})
        else:
            r = TestcaseNumDao().get_num(uuid)
            if r:
                total = r[0]
            else:
                total = 0
            self.render('resultList.html', results=results, num=len(results), total=total)
        