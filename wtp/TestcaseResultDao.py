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
            if testcaseResult.result_id:
                sql = "UPDATE testcase_result SET result=%s, isEnd=%s, isSuccess=%s, run_time=%s WHERE id=%s"
                cursor.execute(sql, ("", "0", "0", "0", testcaseResult.result_id))
            else:
                sql = "INSERT INTO testcase_result(testcase_name, uuid, set_id, run_log_id) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (testcaseResult.testcaseName, testcaseResult.uuid, testcaseResult.set_id, testcaseResult.run_log_id))
        except Exception, e:
            sys.stderr.write(str(e))
            self.conn.rollback()
        
    def update(self, testcaseResult, resultList=[]):
        if isinstance(resultList, list):
            for result in resultList:
                testcaseResult.result += result
        else:
            testcaseResult.result = str(resultList)
        cursor = self.getCursor()
        try:
            sql = "UPDATE testcase_result SET result = %s, isEnd = %s, isSuccess = %s, run_time=%s WHERE testcase_name = %s AND uuid = %s"
            cursor.execute(sql, (testcaseResult.result, testcaseResult.isEnd, testcaseResult.isSuccess, testcaseResult.run_time, testcaseResult.testcaseName, testcaseResult.uuid))
        except Exception, e:
            print e
            self.conn.rollback()
            
    def retrieveLastOne(self, testcaseName):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess FROM testcase_result WHERE testcase_name = %s ORDER BY ID DESC LIMIT 1"
        cursor.execute(sql, (testcaseName,))
        return cursor.fetchone()

    def retrieveById(self, id):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess FROM testcase_result WHERE id = %s LIMIT 1"
        cursor.execute(sql, (id,))
        return cursor.fetchone()

    def retrieve(self, testcaseName, uuid):
        cursor = self.getCursor()
        sql = "SELECT result, isEnd, isSuccess FROM testcase_result WHERE testcase_name = %s AND uuid = %s LIMIT 1"
        cursor.execute(sql, (testcaseName, uuid))
        return cursor.fetchone()

    def retrieveBySetId(self, set_id):
        cursor = self.getCursor()
        sql = "SELECT id, testcase_name, isEnd, isSuccess, run_time, run_log_id FROM testcase_result WHERE set_id = %s"
        cursor.execute(sql, (set_id,))
        return cursor.fetchall()

import base64
@singleton
class TestcaseRunLogDao(BaseDao):
    def __init__(self):
        BaseDao.__init__(self)

    def insert(self, name, content):
        content = base64.encodestring(content)
        cursor = self.getCursor()
        try:
            sql = "INSERT INTO testcase_run_log(name, content) VALUES ('%s', '%s')"  % (name, content)
            # print sql
            cursor.execute(sql)
            last_id = int(cursor.lastrowid)
            self.conn.commit()
            return  last_id
        except Exception, e:
            print e, 'Error in %s.%s' % (self.__class__, self.__module__)
            self.conn.rollback()

    def getRowById(self, id):
        try:
            cursor = self.getCursor()
            sql = "SELECT id, name, content FROM testcase_run_log WHERE id=%s"  % id
            cursor.execute(sql)
            r = list(cursor.fetchone())
            r[2] = base64.decodestring(r[2])
            return r
        except Exception, e:
            print e, 'Error in %s.%s' % (self.__class__, self.__module__)
            self.conn.rollback()

