# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import json

import tornado.web

from TestcaseResult import TestcaseResult
from TestcaseResultDao import TestcaseResultDao


class TestcaseResultListController(tornado.web.RequestHandler):
    ''' 查看测试用例结果 '''
    def get(self):
        uuid = self.get_argument('uuid')
        
        if not uuid:
            raise Exception
        
        resultsets = TestcaseResultDao().retrieveAllInOneJob(uuid)
        if not resultsets:
            self.write({"successful": False})
        else:
            testcaseResultListDict = {'testcase_result_list' : []}
            for resultset in resultsets:
                testcaseResult = TestcaseResult()
                testcaseResult.uuid = resultset[0]
                testcaseResult.testcaseName = resultset[1]
                testcaseResult.isEnd = resultset[2]
                testcaseResult.isSuccess = resultset[3]
                testcaseResult.run_time = resultset[4]
                testcaseResult.result = '<br />'.join(resultset[5].splitlines())
                testcaseResult.deviceInfo = resultset[6]
                testcaseResult.parentUuid = resultset[7]
                testcaseResultListDict['testcase_result_list'].append(testcaseResult.toDict())

            self.write({"successful": True, 'testcaseResultArray': json.dumps(testcaseResultListDict,  indent=4)})        
