# -*- coding: utf-8 -*-
'''
Created on Jun 1, 2015

@author: chenchen
'''

class Condition:
    def __init__(self, sim=False, resolution=None):
        self.sim = sim
        self.resolution = resolution

    def attr_dict(self):
        return {
            'sim' : self.sim,
            'resolution' : self.resolution,
            }