# -*- coding: utf-8 -*-
'''
Created on May 15, 2015

@author: chenchen
'''
from TornadoProcessor import TornadoProcessor

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Main:
    def __init__(self):
        TornadoProcessor().run()
    
if __name__ == '__main__':
    Main()