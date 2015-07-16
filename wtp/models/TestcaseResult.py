# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import uuid


class TestcaseResult:
    def __init__(self):
        self.deviceInfo = None
        self.parentUuid = ''
        self.uuid = str(uuid.uuid4())
        self.testcaseName = None
        self.result = u''
        self.isEnd = 0
        self.isSuccess = 0
        self.run_time = 0
        self.memo = u''
        
    def toDict(self):
        testcase_result_dict = {}
        testcase_result_dict['deviceInfo'] = self.deviceInfo
        testcase_result_dict['parentUuid'] = self.parentUuid
        testcase_result_dict['uuid'] = self.uuid
        testcase_result_dict['testcaseName'] = self.testcaseName
        testcase_result_dict['result'] = self.result
        testcase_result_dict['isEnd'] = self.isEnd
        testcase_result_dict['isSuccess'] = self.isSuccess
        testcase_result_dict['run_time'] = self.run_time
        testcase_result_dict['memo'] = self.memo
        return testcase_result_dict
