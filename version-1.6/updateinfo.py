#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
更新玩家信息对象
'''
class PlayerUpdateInfo():
    
    '''
    copper          : 铜币
    food            : 食物
    forces          : 兵力
    traincurrentnum : 当前训练武将数
    maxtrainnum     : 最大训练武将数
    kfzonestate     : ?(开发区状态)
    '''
    def __init__(self,copper=None,food=None,forces=None,traincurrentnum=None,maxtrainnum=None,kfzonestate=None):
        self.copper = copper
        self.food   = food
        self.forces = forces
        self.traincurrentnum = traincurrentnum
        self.maxtrainnum = maxtrainnum
        self.kfzonestate = kfzonestate
