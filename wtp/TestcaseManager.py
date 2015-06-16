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

from CommonLib import callCommand
from DeviceManager import DeviceManager
from Singleton import singleton
from TestcaseResultDao import TestcaseResultDao
from ThreadPoolManager import ThreadPoolManager
from Configuration import Configuration

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
				sys.stderr.writelines(uninstallCommand)
				TestcaseResultDao().update(testcase.testcaseResult, callCommand(uninstallCommand))
				
				installCommand = "adb -s %s install %s" % (deviceInfo.serial, testcase.apkpath)
				sys.stderr.writelines(installCommand)
				TestcaseResultDao().update(testcase.testcaseResult, callCommand(installCommand))
				deviceInfo.installed_apps[testcase.package] = testcase.version

				##为新设备初始化测试环境
				for init in testcase.init:
				    init = self._replaceMacro(init, deviceInfo, testcase);
				    sys.stderr.writelines(init)
				    TestcaseResultDao().update(testcase.testcaseResult, ['【init info】:\r\n']+callCommand(init))
				
            for prepare in testcase.prepares:
                prepare = self._replaceMacro(prepare, deviceInfo, testcase);
                TestcaseResultDao().update(testcase.testcaseResult, callCommand(prepare))
                
            for command in testcase.commands:
                command = self._replaceMacro(command, deviceInfo, testcase);
                sys.stderr.writelines(command)
                last_echo = callCommand(command)
                TestcaseResultDao().update(testcase.testcaseResult, last_echo)
                            
            testcase.testcaseResult.isEnd = 1
            test_state = last_echo[-7:]
            testcase.testcaseResult.run_time = test_state[1].strip().split(': ')[1]  ##获取执行时间
            if test_state[3].split()[0]=="OK":  ##判定是否通过
                testcase.testcaseResult.isSuccess = 1
            else:
                testcase.testcaseResult.isSuccess = 0
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