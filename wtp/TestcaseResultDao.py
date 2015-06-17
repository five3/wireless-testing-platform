# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import MySQLdb
import sys
from Singleton import singleton

class BaseDao:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = MySQLdb.connect(
                # host='172.16.95.14', root:root
                host='127.0.0.1',
                user='root',
                passwd='changeit!',
                db='jenkins',
                port=3306,
                charset='utf8'
                )

    def getCursor(self):
        try:
            self.conn.ping()
        except Exception,e:
            try:
                self.connect()
            except Exception,e:
                sys.stderr.write('Error in [%s]: %s' % (self.__class__, e))
        return self.conn.cursor()

@singleton
class TestcaseResultDao(BaseDao):
    def __init__(self):
        BaseDao.__init__(self)

    def insert(self, testcaseResult):
        cursor = self.getCursor()
        try:
            sql = "INSERT INTO testcase_result(testcase_name, uuid, parent_uuid, device_info) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (testcaseResult.testcaseName, testcaseResult.uuid, testcaseResult.parentUuid, testcaseResult.deviceInfo))
        except Exception, e:
            sys.stderr.write(str(e))
            self.conn.rollback()
        
    def update(self, testcaseResult, resultList=[]):
        for result in resultList:
            testcaseResult.result += result
        
        cursor = self.getCursor()
        try:
            sql = "UPDATE testcase_result SET result = %s, isEnd = %s, isSuccess = %s, run_time=%s WHERE testcase_name = %s AND uuid = %s"
            cursor.execute(sql, (testcaseResult.result, testcaseResult.isEnd, testcaseResult.isSuccess, testcaseResult.run_time, testcaseResult.testcaseName, testcaseResult.uuid))
        except Exception, e:
            sys.stderr.write(str(e))
            self.conn.rollback()

    def retrieveAllInOneJob(self, parentUuid):
        cursor = self.getCursor()
        sql = "SELECT uuid, testcase_name, isEnd, isSuccess, run_time, result, device_info, parent_uuid FROM testcase_result WHERE parent_uuid = %s"
        cursor.execute(sql, (parentUuid,))
        return cursor.fetchall()
		
    def retrieveLastOne(self, testcaseName):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess FROM testcase_result WHERE testcase_name = %s ORDER BY ID DESC LIMIT 1"
        cursor.execute(sql, (testcaseName,))
        return cursor.fetchone()

    def retrieve(self, testcaseName, uuid):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess FROM testcase_result WHERE testcase_name = %s AND uuid = %s LIMIT 1"
        cursor.execute(sql, (testcaseName, uuid))
        return cursor.fetchone()