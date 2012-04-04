#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request
from updateinfo import PlayerUpdateInfo
'''
精炼
'''

class RefineThread(threading.Thread):

    def __init__(self,include,serverid,playerinfo):
        threading.Thread.__init__(self)        
        self.request  = Request(include)
        self.serverid = serverid
        self.playerinfo = playerinfo
        self.stoped = False

    def stop(self):
        self.request.include.logger.info(u"精炼线程停止")
        self.stoped = True

    def isStoped(self):
        return self.stoped
    
    '''
    获取精炼信息
    '''
    def getRefineInfo(self):
        url = "http://s%d.as.yaowan.com/root/refine!getRefineInfo.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        if res:
            if res.find("<?xml")<0:
                self.request.include.logger.warning(u"获取精炼信息失败，重新请求...")
                time.sleep(2)
                return self.getRefineInfo()
            res = res[res.find("<?xml"):]
            print 'refine res:',res
            infoXML = etree.XML(res)
            refineInfo = RefineInfo()
            refinergrouplist = []
            refinerlist = []
            for child in infoXML.getchildren():
                if child.tag=="state":
                    refineInfo.state = child.text
                if child.tag=="refinenum":
                    refineInfo.refinenum = int(child.text)
                if child.tag=="maxrefinenum":
                    refineInfo.maxrefinenum = child.text
                if child.tag=="surplursleft":
                    refineInfo.surplursleft = child.text
                if child.tag=="copper":
                    refineInfo.copper = child.text
                if child.tag=="percost":
                    refineInfo.percost = child.text
                if child.tag=="allcost":
                    refineInfo.allcost = child.text
                if child.tag=="refinergroup":
                    refinergroup        = RefinerGroup()
                    refinergroup.time   = int(child.findtext("time"))
                    refinergroup.id     = child.findtext("id")
                    refinergroup.cdflag = int(child.findtext("cdflag"))
                    refinergrouplist.append(refinergroup)
                if child.tag=="refiner":
                    refiner = Refiner()
                    refiner.id    = child.findtext("id")
                    refiner.color = child.findtext("color")
                    refiner.name  = child.findtext("name")
                    refiner.stone = child.findtext("stone")
                    refiner.order = child.findtext("order")
                    refiner.desc  = child.findtext("desc")
                    refinerlist.append(refiner)
                if child.tag=="playerupdateinfo":
                    updateinfo = PlayerUpdateInfo()
                    updateinfo.kfzonestate = child.findtext("kfzonestate")
                    refineInfo.playerupdateinfo = updateinfo
            refineInfo.refinergrouplist = refinergrouplist
            refineInfo.refinerList = refinerlist
            return refineInfo
        return None

    def run(self):
        if self.stoped:
            return
        refineInfo = self.getRefineInfo()
        if not refineInfo:
            self.request.include.logger.error(u"获取精炼信息失败")
            self.stop()
            return
        # 判断精炼次数是否为0，是则停止线程
        if refineInfo.refinenum==0:
            self.request.include.logger.warning(u"精炼次数为0")
            self.stop()
            return

        # 开启精炼队列
        refinergroup = refineInfo.refinergrouplist
        for refiner in refinergroup:
            if refiner.time==0 and refiner.cdflag==0:
                # 开启精炼
                url = "http://s%d.as.yaowan.com/root/refine!refine.action?%d" %(self.serverid,int(time.time()*1000))
                reqinfo = self.request.request(url)
                res = zlib.decompress(reqinfo.read())
                if not res or res.find("<?xml")<0:
                    self.request.include.logger.warning(u"开始精炼失败，没有空闲的工人")
                    self.stop()
                    return
                self.request.include.logger.info(u"精炼成功，返回:%s" %res)


'''
精炼信息对象
'''
class RefineInfo():

    '''
    state            : 状态
    refinenum        : 精炼次数
    maxrefienum      : 最大精炼次数
    surplursleft     : 余料累计
    copper           : 精炼消耗钱币
    percost          : 升级金币
    allcost          : 刷新金币
    refinergrouplist : RefinerGroup集合
    refinerList      : 精炼集合
    playerupdateinfo : 玩家更新信息
    '''
    def __init__(self,state=None,refinenum=None,maxrefinenum=None,surplursleft=None,copper=None,percost=None,allcost=None,refinergrouplist=None,refinerList=None,playerupdateinfo=None):
        self.state            = state
        self.refinenum        = refinenum
        self.maxrefinenum     = maxrefinenum
        self.surplursleft     = surplursleft
        self.copper           = copper
        self.percost          = percost
        self.allcost          = allcost
        self.refinergrouplist = refinergrouplist
        self.refinerList      = refinerList
        self.playerupdateinfo = playerupdateinfo


'''
精炼队列
'''
class RefinerGroup():
    '''
    time: CD时间
    id  : 队列ID
    cdflag: cd标记(1:cd中/0:未CD)
    '''
    def __init__(self,time=None,id=None,cdflag=None):
        self.time   = time
        self.id     = id
        self.cdflag = cdflag


'''
精炼对象
'''
class Refiner():
    '''
    _id   : 精炼对象ID
    color : 精炼对象颜色
    name  : 精炼名称
    stone : ? 精炼石头
    order : 精炼排序
    desc  : 精炼说明
    '''
    def __init__(self,_id=None,color=None,name=None,stone=None,order=None,desc=None):
        self.id = _id
        self.color = color
        self.name = name
        self.stone = stone
        self.order = order
        self.desc = desc
        








