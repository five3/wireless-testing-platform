# -*- coding: utf-8 -*-
'''
Created on May 27, 2015

@author: chenchen
'''
import os
import uuid

import lazyxml

from models.Configuration import Configuration
from models.Testcase import Testcase
from models.TestcaseResultDao import TestcaseNumDao

class TestcaseReader:
    def __init__(self, apkpath, projectname):
        self.apkpath = apkpath
        self.projectname = projectname
        self.uuid = str(uuid.uuid4())
        self.testcaseList = []
        
        self._load()

        
    ''' 确定测试用例文件路径 '''
    def _getTestcasePath(self):
        testcasePath = "%s/%s/testcase.xml" % (Configuration().dicts['testcase']['testcaseServer'], self.projectname)
        # print testcasePath
        if os.path.isfile(testcasePath):
            return testcasePath
        else:
            raise Exception('testcase file not exist!')
    
    def _load(self):
        xml = open(self._getTestcasePath()).read()
        dicts = lazyxml.loads(xml, strip=False)
        
        if not dicts or not dicts['testcases'] or not dicts['testcases']['testcase']:
            raise Exception("no testcase found")
        
        package = dicts['package']
        self.version = dicts['version'].replace('.', '')
        self.init = self.splitCommandLine(dicts['init'])		
        self.setup = self.splitCommandLine(dicts['setup']) if 'setup' in dicts else []		
		
        if type(dicts['testcases']['testcase']) is dict:
            self.testcaseList.append(self._readTestcase(dicts['testcases']['testcase'], package))
        else:
            for testcaseDict in dicts['testcases']['testcase']:
                self.testcaseList.append(self._readTestcase(testcaseDict, package))

        TestcaseNumDao().insert(self.uuid, len(self.testcaseList))
                
    def _readTestcase(self, testcaseDict, package):
        if (not testcaseDict.has_key('name')) and (not testcaseDict.has_key('description')):
            raise Exception
        
        name = None
        if testcaseDict.has_key('name'):
            name = testcaseDict['name']
        else:
            name = testcaseDict['description']

        testcase = Testcase(name, self.apkpath.strip(), testcaseDict['description'].strip() if testcaseDict.has_key('description') else None, self._getTestcasePath().strip(), package.strip())
            
        testcase.testcaseResult.testcaseName = testcase.name
        testcase.testcaseResult.parentUuid = self.uuid
        testcase.testcaseResult.memo = testcase.description
        testcase.version = self.version
        testcase.init = self.init
        testcase.parent_uuid = self.uuid
        testcase.uuid = testcase.testcaseResult.uuid
            
        if type(testcaseDict['commands']['command']) is list:
            for command in testcaseDict['commands']['command']:
                testcase.commands.extend(self.splitCommandLine(command))
        else:
            testcase.commands.extend(self.splitCommandLine(testcaseDict['commands']['command']))
            
        if testcaseDict.has_key('condition') and testcaseDict['condition'].has_key('sim'):
            testcase.condition.sim = True if testcaseDict['condition']['sim'].lower() != 'false' else False

        testcase.prepares.extend(self.setup)
        if 'prepares' in testcaseDict:
			if type(testcaseDict['prepares']['prepare']) is list:
				for prepare in testcaseDict['prepares']['prepare']:
					testcase.prepares.extend(self.splitCommandLine(prepare))
			else:
				testcase.prepares.extend(self.splitCommandLine(testcaseDict['prepares']['prepare']))
        
        return testcase
    
    def splitCommandLine(self, command):
        command = command.strip()
        if command.find("\n") == -1:
            return [command.strip()]
        else: 
            return [x.strip() for x in command.split("\n")]
