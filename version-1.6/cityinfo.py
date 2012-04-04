#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
玩家城池信息对象
'''
class CityInfo():
   
    '''
    buildlist   : 主城建筑对象list集合
    buildcdlist : 建造CD对象list集合
    '''
    def __init__(self,buildlist=None,buildcdlist=None):
        self.buildlist    = buildlist
        self.buildcdlist = buildcdlist


'''
主城建筑对象
'''
class CityBuild(): 
    '''
    类型都未转换
    id             : 
    build          : 建筑ID
    buildname      : 建筑名称
    intro          : 说明
    cityid         : 城池ID
    playerid       : 玩家ID
    buildlevel     : 建筑级别
    nextcopper     : 下一级升级所需铜币
    cdtime         : 下一级升级建造CD（分钟）
    lastcdtime     : 最后CD时间？
    lastupdatetime : 最后更新时间
    '''
    def __init__(self,id=None,buildid=None,buildname=None,intro=None,cityid=None,playerid=None,buildlevel=None,nextcopper=None,cdtime=None,lastcdtime=None,lastupdatetime=None):
        self.id             = id
        self.buildid        = buildid
        self.buildname      = buildname
        self.intro          = intro
        self.cityid         = cityid
        self.playerid       = playerid
        self.buildlevel     = buildlevel
        self.nextcopper     = nextcopper
        self.cdtime         = cdtime
        self.lastcdtime     = lastcdtime
        self.lastupdatetime = lastupdatetime

'''
类型都转换成了整数型
建造CD对象
'''
class BuildCD():
    '''
    ctime  : 队列剩余CD时间（毫秒）
    cid    : 队列ID
    cdflag : 队列标识（1：CD中）
    endtime: 队列结束时间（按服务器时间计算）
    '''
    def __init__(self,ctime=None,cid=None,cdflag=None,endtime=None):
        self.ctime   = ctime
        self.cid     = cid
        self.cdflag  = cdflag
        self.endtime = endtime
