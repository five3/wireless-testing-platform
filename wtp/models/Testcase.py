# -*- coding: utf-8 -*-
'''
Created on May 25, 2015

@author: chenchen
'''
from models.Condition import Condition
from models.TestcaseResult import TestcaseResult


class Testcase:
    ''' test case model '''
    def __init__(self, name, apkpath, description, testcasepath, package, condition=Condition()):
        self.name = name
        self.commands = []
        self.apkpath = apkpath
        self.prepares = []
        self.description = description
        self.testcasepath = testcasepath
        self.package = package
        self.condition = condition
        self.testcaseResult = TestcaseResult()
        self.init = []
        self.version = 0
    
