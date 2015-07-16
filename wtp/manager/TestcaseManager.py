# -*- coding: utf-8 -*-
'''
Created on May 26, 2015

@author: chenchen
'''

import Queue
import json
import thread
import time
import sys

from threadpool import makeRequests

from utils.Singleton import singleton
from utils.CommonLib import callCommand

from manager.DeviceManager import DeviceManager
from manager.ThreadPoolManager import ThreadPoolManager

from models.TestcaseResultDao import TestcaseResultDao
from models.Configuration import Configuration


@singleton
class TestcaseManager:
    def __init__(self):
        self.times_to_reboot = int(Configuration().dicts['times_to_reboot'])
        self.queue = Queue.Queue()
        thread.start_new_thread(self._processOnBackground, ())
        
    def _processOnBackground(self):
        while True:
            if self.queue.empty():
                time.sleep(1)
                continue
            
            testcase_list = []
            for i in range(len(DeviceManager()._deviceInfoList.available_device_list)):  ###根据空闲设备数来控制并发量
                if not self.queue.empty():
                    testcase_list.append(self.queue.get())
                else:    ##用例取完则退出
                    break

            req_list = []
            for testcase in testcase_list:
                deviceInfo = DeviceManager().shiftDevice(testcase.condition)
                if not deviceInfo:     ##没有设备则用例送回队列
                    self.queue.put(testcase)
                    time.sleep(1)
                    continue
                req_list.append({'deviceInfo':deviceInfo, 'testcase':testcase})

            if not req_list:
                continue

            requests = makeRequests(self._runTestcase, req_list)
            [ThreadPoolManager().threadPool.putRequest(req) for req in requests]
            ThreadPoolManager().threadPool.wait()
    
    ''' 增加工作请求，将请求加入到工作队列中 '''
    def process(self, testcase):
        self.queue.put(testcase)

    def _runTestcase(self, *args, **kwds):
        try:
            deviceInfo = args[0]['deviceInfo']
            testcase = args[0]['testcase']
            testcase.testcaseResult.deviceInfo = json.dumps(deviceInfo.toDict())			
            TestcaseResultDao().insert(testcase.testcaseResult)
            
			###-------------检查是否需要重新安装被测程序---------------------#
            if (testcase.package not in deviceInfo.installed_apps) or \
                (deviceInfo.installed_apps[testcase.package] != testcase.version):  ##未安装过##版本不一致则重新安装
				
				uninstallCommand = "adb -s %s uninstall %s" % (deviceInfo.serial, testcase.package) ##卸载软件
				sys.stderr.writelines(uninstallCommand+'\r\n')
				TestcaseResultDao().update(testcase.testcaseResult, [u'【uninstall apk】:%s\r\n' % uninstallCommand]+callCommand(uninstallCommand))
				
				installCommand = "adb -s %s install %s" % (deviceInfo.serial, testcase.apkpath)
				sys.stderr.writelines(installCommand+'\r\n')
				TestcaseResultDao().update(testcase.testcaseResult, [u'【install apk】:%s\r\n' % installCommand]+callCommand(installCommand))
				deviceInfo.installed_apps[testcase.package] = testcase.version

				##为新设备初始化测试环境
				for init in testcase.init:
				    init = self._replaceMacro(init, deviceInfo, testcase)
				    sys.stderr.writelines(init+'\r\n')
				    TestcaseResultDao().update(testcase.testcaseResult, [u'【init info】:%s\r\n' % init]+callCommand(init))
				
            for prepare in testcase.prepares:
                prepare = self._replaceMacro(prepare, deviceInfo, testcase)
                sys.stderr.writelines(prepare+'\r\n')
                TestcaseResultDao().update(testcase.testcaseResult, [u'【prepare info】:%s\r\n' % prepare]+callCommand(prepare))
                
            for command in testcase.commands:
                command = self._replaceMacro(command, deviceInfo, testcase)
                sys.stderr.writelines(command+'\r\n')
                last_echo = callCommand(command)
                TestcaseResultDao().update(testcase.testcaseResult, [u'【command info】:%s\r\n' % command]+last_echo)
                            
            testcase.testcaseResult.isEnd = 1
            test_state = last_echo[-10:]
            # print test_state
            for i in test_state:
                if 'Time' in i:
                    testcase.testcaseResult.run_time = i.strip().split(': ')[1]  ##获取执行时间
                elif 'FAILURES' in i:
                    testcase.testcaseResult.isSuccess = 0
                elif 'OK' in i:
                    testcase.testcaseResult.isSuccess = 1
            TestcaseResultDao().update(testcase.testcaseResult)
        finally:
            deviceInfo.run_times += 1
            if deviceInfo.run_times%self.times_to_reboot==0:  ##达到指定次数则重启设备
                callCommand("adb -s %s reboot"%deviceInfo.serial)
                time.sleep(10)  ##等待重启
            else:
                DeviceManager().resetDevice(deviceInfo)

    def _replaceMacro(self, original, deviceInfo, testcase):
        original = original.replace("${SERIAL}", deviceInfo.serial)
        original = original.replace("${WORKSPACE}", testcase.testcasepath[0:testcase.testcasepath.rindex('/')])
        
        return original

    def get_size(self):
        return  self.queue.qsize()

    def empty(self):
        while not self.queue.empty():
            self.queue.get()

    def remove_by_parent_uuid(self, uuid):
        dump_list = []
        while not self.queue.empty():
            dump_list.append(self.queue.get())
        [self.queue.put(i) for i in dump_list if i.parent_uuid!=uuid]

    def remove_by_uuid(self, uuid):
        dump_list = []
        while not self.queue.empty():
            dump_list.append(self.queue.get())
        [self.queue.put(i) for i in dump_list if i.uuid!=uuid]

    def get_dump_list(self):
        dump_list = []
        case_list = []
        while not self.queue.empty():
            testcase = self.queue.get()
            dump_list.append([testcase.name, testcase.description, testcase.uuid, testcase.parent_uuid])
            case_list.append(testcase)
        [self.queue.put(i) for i in case_list]
        return dump_list