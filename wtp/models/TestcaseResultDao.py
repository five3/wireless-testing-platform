# -*- coding: utf-8 -*-
'''
Created on Jun 2, 2015

@author: chenchen
'''
import sys

import MySQLdb

from utils.Singleton import singleton


class BaseDao:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = MySQLdb.connect(
                host='172.16.95.14',
                user='root',
                passwd='root',
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
class TestcaseNumDao(BaseDao):
    def __init__(self):
        BaseDao.__init__(self)

    def insert(self, parent_uuid, num):
        cursor = self.getCursor()
        try:
            sql = '''insert into testcase_num (parent_uuid, num) values (%s, %s)'''
            cursor.execute(sql, (parent_uuid, num))
            self.conn.commit()
        except Exception, e:
            sys.stderr.write(str(e))
            self.conn.rollback()

    def get_num(self, parent_uuid):
        cursor = self.getCursor()
        sql = '''select num from testcase_num where parent_uuid=%s'''
        cursor.execute(sql, (parent_uuid, ))
        return cursor.fetchone()


@singleton
class TestcaseResultDao(BaseDao):
    def __init__(self):
        BaseDao.__init__(self)

    def insert(self, testcaseResult):
        cursor = self.getCursor()
        try:
            sql = "INSERT INTO testcase_result(testcase_name, memo, uuid, parent_uuid, device_info, device_name) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (testcaseResult.testcaseName, testcaseResult.memo, testcaseResult.uuid, testcaseResult.parentUuid, testcaseResult.deviceInfo, testcaseResult.deviceName))
        except Exception, e:
            sys.stderr.write(str(e))
            self.conn.rollback()
        
    def update(self, testcaseResult, resultList=[]):
        try:
            testcaseResult.result += ''.join(resultList)
        except:
            for i in resultList:
                print type(i), i, unicode(i)
            raise Exception('编码错误')
        
        cursor = self.getCursor()
        try:
            sql = "UPDATE testcase_result SET result = %s, isEnd = %s, isSuccess = %s, run_time=%s WHERE testcase_name = %s AND uuid = %s"
            cursor.execute(sql, (testcaseResult.result, testcaseResult.isEnd, testcaseResult.isSuccess, testcaseResult.run_time, testcaseResult.testcaseName, testcaseResult.uuid))
        except Exception, e:
            sys.stderr.write(str(e))
            self.conn.rollback()

    def retrieveAllInOneJob(self, parentUuid):
        cursor = self.getCursor()
        sql = "SELECT testcase_name, memo, device_name, isEnd, isSuccess, run_time, result, device_info, parent_uuid, id FROM testcase_result WHERE parent_uuid = %s"
        cursor.execute(sql, (parentUuid,))
        return cursor.fetchall()
		
    def retrieveLastOne(self, testcaseName):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess, parent_uuid FROM testcase_result WHERE testcase_name = %s ORDER BY ID DESC LIMIT 1"
        cursor.execute(sql, (testcaseName,))
        return cursor.fetchone()

    def retrieve(self, testcaseName, uuid):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess FROM testcase_result WHERE testcase_name = %s AND uuid = %s LIMIT 1"
        cursor.execute(sql, (testcaseName, uuid))
        return cursor.fetchone()

    def get_device_info(self, caseid):
        cursor = self.getCursor()
        sql = "SELECT device_info FROM testcase_result WHERE id=%s LIMIT 1"
        cursor.execute(sql, (caseid, ))
        return cursor.fetchone()