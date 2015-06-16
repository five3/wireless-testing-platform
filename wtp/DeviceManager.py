# -*- coding: utf-8 -*-
"""
Created on Dec 18, 2014

@author: chenchen
"""

import json
import random
import thread
from threading import Lock
import time

from CommonLib import callCommand, write
from Condition import Condition
from DeviceInfo import DeviceInfo
from DeviceInfoList import DeviceInfoList
from DeviceUtils import DeviceUtils
from Singleton import singleton


@singleton
class DeviceManager():
    _deviceInfoList = None
    _lock = Lock()
    
    ''' singleton device manager '''
    def __init__(self):
        if self._deviceInfoList == None:
            self._deviceInfoList = DeviceInfoList()
            self.refresh(True)
            thread.start_new_thread(self._refreshPeriodly, ())
            
    def getDeviceInfoList(self):
        return self._deviceInfoList
    
    def shiftDevice(self, condition=Condition()):
        try:
            self._lock.acquire()
        
            available_device_len = len(self._deviceInfoList.available_device_list)
            if available_device_len <= 0:
                return None
            
            aimed_index = None
            ks = self._deviceInfoList.available_device_list.keys()  ##��Ч�豸Ŀ¼
            if condition.sim:
                ''' XXX loadbalance '''
                for k in ks:
                    available_device = self._deviceInfoList.relDeviceList[k]
                    if available_device.sim_state == condition.sim:
                        aimed_index = k
                        break
            else:
                i = random.randint(0, available_device_len - 1)
                aimed_index = ks[i]
                
            if not aimed_index:
                return None
                
            self._deviceInfoList.available_device_list.pop(aimed_index)  ##����ЧĿ¼ɾ��
            deviceInfo = self._deviceInfoList.relDeviceList[aimed_index] 
            DeviceUtils.lockDevice(deviceInfo.serial)
            
            return deviceInfo
        finally:
            self._lock.release()
#         
    def resetDevice(self, deviceInfo):
        try:
            self._lock.acquire()            
            DeviceUtils.unlockDevice(deviceInfo.serial)
        finally:
            self._lock.release()
    
    def refresh(self, isFirst=False):
        temp_unavailable_device_list = {}  ##��ʱ��Ч�豸�б�
        temp_processing_device_list = {}
        temp_available_device_list = {}
        temp_available_serial_list = []  ##��ǰ��Ч�����豸
        
        try:
            self._lock.acquire()            
            adb_dvc = callCommand("adb devices")[1:]
            for dvc_info in adb_dvc:
                try:
                    dvc_info = dvc_info.strip()
                    if not dvc_info:
                        continue
                    
                    serial = dvc_info.split()[0]
                    if dvc_info.split()[1] == 'device':  ##��Ч�豸
                        temp_available_serial_list.append(serial)
                        if serial not in self._deviceInfoList.relDeviceList: ##�״ν����������ʼ���豸��Ϣ
                            DeviceUtils.unlockDevice(serial)
                            self._deviceInfoList.relDeviceList[serial] = DeviceInfo(serial)
                        
                        if DeviceUtils.isDeviceLocked(serial):
                            temp_processing_device_list[serial] = 1
                        else:
                            temp_available_device_list[serial] = 1
                    else:
                        temp_unavailable_device_list[serial] = DeviceInfo(serial, False)
                except Exception, e:
                    import traceback
                    print traceback.format_exc()
					
            for k in self._deviceInfoList.relDeviceList.keys():  ##����Ƴ����豸
                if k not in temp_available_serial_list:
                    del self._deviceInfoList.relDeviceList[k]
					
            self._deviceInfoList.unavailable_device_list = temp_unavailable_device_list  ##������Ч�豸�б�
            self._deviceInfoList.processing_device_list = temp_processing_device_list  ##����ִ���豸Ŀ¼
            self._deviceInfoList.available_device_list = temp_available_device_list  ##���ÿ����豸Ŀ¼
        finally:
            self._lock.release()
                 
    def _refreshPeriodly(self):
        while True:
            self.refresh()
            time.sleep(2)

    def printDeviceInfoListToConsole(self):
        write('DEVICE_STATUS', json.dumps(self._deviceInfoList.toDict()))
