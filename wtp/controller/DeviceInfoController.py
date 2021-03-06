# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen9
'''

import json

import lazyxml
import tornado.web

from manager.DeviceManager import DeviceManager
from manager.ThreadPoolManager import ThreadPoolManager

from models.TestcaseResultDao import TestcaseResultDao

class DeviceInfoController(tornado.web.RequestHandler):
    def get(self):
        dicts = DeviceManager().getDeviceInfoList().toDict()
        dicts['threadNumber'] = ThreadPoolManager().threadNumber

        if self.get_argument('rel', None):
            api_type = self.get_argument('rel', 'xml')
            pretty = self.get_argument('pretty', 'true').lower() == 'true'
            if api_type == 'json':
                if pretty:
                    devices_info = json.dumps(dicts, indent=4)
                else:
                    devices_info = json.dumps(dicts)
            elif api_type == 'xml':
                if pretty:
                    devices_info = lazyxml.dumps(dicts, root='device_list', cdata=False, indent='    ')
                else:
                    devices_info = lazyxml.dumps(dicts, root='device_list', cdata=False)
            else:
                raise Exception('unsupported argument: ' + api_type)
            if pretty:
                self.render('msg.html', msg=devices_info)
            else:
                self.write(devices_info)
        elif self.get_argument('caseid', None):
            caseid = self.get_argument('caseid', '0')
            device_info = TestcaseResultDao().get_device_info(caseid)
            if device_info:
                msg = json.loads(device_info[0])
                msg = json.dumps(msg, indent=4)
            else:
                msg = 'no device info found'
            self.render('msg.html', msg=msg)
        else:
            self.render('devices.html', info=dicts)