# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import json

import tornado.web

from models.TestcaseResult import TestcaseResult
from models.TestcaseResultDao import TestcaseResultDao


class TestcaseResultListController(tornado.web.RequestHandler):
    ''' 查看测试用例结果 '''
    def get(self):
        uuid = self.get_argument('uuid')
        
        if not uuid:
            raise Exception
        
        resultsets = TestcaseResultDao().retrieveAllInOneJob(uuid)
        if not resultsets:
            self.write({"successful": False, 'msg':'no result found'})
        else:
            testcaseResultListDict = {'testcase_result_list' : []}
            for resultset in resultsets:
                testcaseResult = TestcaseResult()
                testcaseResult.testcaseName = resultset[0]
                testcaseResult.memo = resultset[1]
                testcaseResult.deviceName = resultset[2]
                testcaseResult.isEnd = resultset[3]
                testcaseResult.isSuccess = resultset[4]
                testcaseResult.run_time = resultset[5]
                testcaseResult.result = '<br />'.join(resultset[6].splitlines())
                testcaseResult.deviceInfo = resultset[7]
                testcaseResult.parentUuid = resultset[8]
                testcaseResultListDict['testcase_result_list'].append(testcaseResult.toDict())

            self.write({"successful": True, 'testcaseResultArray': json.dumps(testcaseResultListDict,  indent=4)})        
