# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen9
'''

import json
import lazyxml
import tornado.web
from manager.TestcaseManager import TestcaseManager

class QueueController(tornado.web.RequestHandler):
    def get(self):
        queue_size = TestcaseManager().get_size()
        queue_list = TestcaseManager().get_dump_list()
        dicts = {'queue_size':queue_size, 'queue_list':queue_list}
        # print dicts
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
        else:
            self.render('queue.html', info=dicts)

    def post(self):
        action = self.get_argument('action', None)
        if action=='empty':
            TestcaseManager().empty()
        elif action=='remove':
            uuid = self.get_argument('uuid', None)
            if uuid:
                TestcaseManager().remove_by_uuid(uuid)
            parent_uuid = self.get_argument('parent_uuid', None)
            if parent_uuid:
                TestcaseManager().remove_by_parent_uuid(parent_uuid)
        self.write({'errorCode':0, 'msg':'success'})

