# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen
'''
import os

import tornado.web

from models.Configuration import Configuration
from manager.TestcaseManager import TestcaseManager
from utils.TestcaseReader import TestcaseReader


class ProcessController(tornado.web.RequestHandler):
    ''' 执行测试用例 '''
    def get(self):
        ''' 1. 确定交付包位置 '''
        apkpath = "%s/%s" % (Configuration().dicts['testcase']['packageServer'], self.get_argument('apkpath'))
        # print apkpath
        exist = os.path.isfile(apkpath)
        if not exist:
            raise Exception('apkpath incorrect: %s' % apkpath)
        
        ''' 3. 解析xml，反序列化 '''
        testcaseReader = TestcaseReader(apkpath, self.get_argument('projectname').strip('/'));
            
        ''' 4. 循环读取命令，在线程池中运行 '''
        for testcase in testcaseReader.testcaseList:
            TestcaseManager().process(testcase)

        if not self.get_argument('rel', None):
            self.render('process.html', uuid=testcaseReader.uuid)
        else:
            self.write({'success': True, 'uuid': testcaseReader.uuid})
