#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request
from timehelp import TimeHelp

'''
外城
'''
class OutCityThread(threading.Thread):
    
    def __init__(self,include,serverid,playerinfo,config):
        threading.Thread.__init__(self)        
        self.request    = Request(include)
        self.serverid   = serverid
        self.playerinfo = playerinfo
        self.config     = config
    
    '''
    获取外城采集信息
    返回GetPickSpace对象
    '''
    def getPickSpace(self):
        url = "http://s%d.as.yaowan.com/root/outCity!getPickSpace.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        #print 'outcity res:',res
        if res:
            if res.find("<?xml")<0:
                self.request.include.logger.warning(u"获取外城采集信息失败，重新请求...")
                time.sleep(2)
                return self.getPickSpace()
            res = res[res.find("<?xml"):]
            #print 'outcity res xml:',res
            infoXML = etree.XML(res)
            pickspace = GetPickSpace()
            pickdtolist = []
            trainmodeldlist = []
            for child in infoXML.getchildren():
                if child.tag=="state":
                    pickspace.state = child.text
                if child.tag=="pickevent":
                    _id                 = child.findtext("id")
                    name                =child.findtext("name") 
                    _type               = child.findtext("type")
                    intro               = child.findtext("intro")
                    pickevent           = PickEvent(_id,name,_type,intro)
                    pickspace.pickevent = pickevent
                if child.tag=="playerpickdto":
                    _id = child.findtext("id")
                    workernum     = int(child.findtext("workernum"))
                    profit        = child.findtext("profit")
                    pattern       = child.findtext("pattern")
                    patternid     = child.findtext("patternid")
                    endtime       = int(child.findtext("endtime"))
                    safepick      = child.findtext("safepick")
                    safepickcost  = child.findtext("safepickcost")
                    playerpickdto = PlayerPickdTo(_id,workernum,profit,pattern,patternid,endtime,safepick,safepickcost)
                    pickdtolist.append(playerpickdto)
                if child.tag=="trainmodeldto":
                    _id           = child.findtext("id")
                    times         = child.findtext("times")
                    name          = child.findtext("name")
                    cost          = child.findtext("cost")
                    trainmodeldto = TrainModeldTo(_id,times,name,cost)
                    trainmodeldlist.append(trainmodeldto)
                if child.tag=="cjclevel":
                    pickspace.cjclevel = child.text
                if child.tag=="kjlevel":
                    pickspace.kjlevel = child.text
                if child.tag=="areaname":
                    pickspace.areaname = child.text
                if child.tag=="spacefree":
                    pickspace.spacefree = child.text
                if child.tag=="maxspacefree":
                    pickspace.maxspacefree = child.text
                if child.tag=="workernum":
                    pickspace.workernum = int(child.text)
            pickspace.playerpickdtolist = pickdtolist
            pickspace.trainmodeldtolist = trainmodeldlist
            return pickspace
        return None

    '''
    判断是否可以采集，若可以则直接收取
    '''
    def isPickdto(self,pickdtolist):
        isPick = False
        for pick in pickdtolist:
            # 采集CD结束
            if pick.endtime==0:
                # 收取
                self.endPick(pick.id)
                isPick = True
                # 开始工作(等待测试!!)
                self.startPick(pick.workernum)
                # 重新获取GetPickSpace对象
                self.isPickdto(self.getPickSpace().playerpickdtolist)
                break
        # 等待
        if not isPick:
            i=0
            minEndTime = pickdtolist[i].endtime
            for pick in pickdtolist:
                if i>=len(pickdtolist)-1:
                    print u'采集CD:',minEndTime
                    break
                if minEndTime>pickdtolist[i+1].endtime:
                    minEndTime = pickdtolist[i+1].endtime
                i=i+1

    '''
    开始采集
    workerNum: 工作人数
    '''
    def startPick(self,workerNum):
        url = "http://s%d.as.yaowan.com/root/outCity!startPick.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"workerNum":workerNum}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            print 'startpick:',res
            self.request.include.logger.info(u"采集场%d个工人开工" %workernum)

    '''
    收取玉石
    '''
    def endPick(self,pickSpaceId):
        url = "http://s%d.as.yaowan.com/root/outCity!endPick.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"advance"     :0,          # 提前收取
                "safePick"    :0,          # 安全采集
                "pickSpaceId" :pickSpaceId # 采集空间ID
                }
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            self.request.include.logger.info(u"采集场收取玉石,返回结果:%s" %res)

    '''
    判断是否有空余的工人
    是否需要开工
    pickspace: GetPickSpace对象
    '''
    def isNeedBegin(self,pickspace):
        # 如果空余的工人小于配置文件中的次数，则一次开工
        # 否则，分次数开工
        opennum = self.config._defaultConfig.get("refine-opennum")
        print 'pickspace.workernum:',pickspace.workernum,",opennum:",opennum
        if pickspace.workernum<=opennum:
            self.startPick(pickspace.workernum)
        else:
            num = pickspace.workernum/opennum
            if pickspace.workernum%opennum>0:
                num = num+1
            while num>0:
                self.startPick(opennum)
                num = num -1
        
    def run(self):
        # 获取GetPickSpace对象
        pickspace = self.getPickSpace()
        if not pickspace:
            self.request.include.logger.error(u"获取外城采集场信息失败，采集线程停止")
            return
        if pickspace.workernum==0:
            self.request.include.logger.warning(u"没有闲置的工人,采集线程停止")
            return
        # 判断是否需要开工
        self.isNeedBegin(pickspace)
        # 重新获取采集信息
        pickspace = self.getPickSpace()
        if not pickspace.playerpickdtolist or len(pickspace.playerpickdtolist)==0:
            print u"获取外城采集信息失败，跳过...."
            return
        # 判断是否可以采集
        self.isPickdto(pickspace.playerpickdtolist)


'''
外城采集空间对象
'''
class GetPickSpace():
    '''
    state             : 状态
    pickevent         : 采集事件
    playerpickdtolist : 玩家采集队列集合
    trainmodeldtolist : 训练模式集合
    cjclevel          : 采集场等级
    kjlevel           : 矿井等级
    areaname          : 地区名称
    spacefree         : 剩余空间
    maxspacefree      : 最大空间
    workernum         : 工作人数
    '''
    def __init__(self,state=None,pickevent=None,playerpickdtolist=None,trainmodeldtolist=None,cjclevel=None,kjlevel=None,areaname=None,spacefree=None,maxspacefree=None,workernum=None):
        self.state             = state
        self.playerpickdtolist = playerpickdtolist
        self.trainmodeldtolist = trainmodeldtolist
        self.cjclevel          = cjclevel
        self.kjlevel           = kjlevel
        self.areaname          = areaname
        self.spacefree         = spacefree
        self.maxspacefree      = maxspacefree
        self.workernum         = workernum
        

'''
采集模式对象
'''
class TrainModeldTo():
    '''
    _id:模式ID
    times: 时间
    name:模式名称
    cost:金币
    '''
    def __init__(self,_id=None,times=None,name=None,cost=None):
        self.id    = _id
        self.times = times
        self.name  = name
        self.cost  = cost

'''
玩家采集对象 
'''
class PlayerPickdTo():
    '''
    workernum    : 开工人数
    profit       : 利润
    pattern      : 模式(正常模式/加强模式)
    pattenid     : 模式ID
    endtime      : 结束时间CD
    safepick     : 安全采集
    safepickcost : 安全采集成本
    '''
    def __init__(self,_id=None,workernum=None,profit=None,pattern=None,patternid=None,endtime=None,safepick=None,safepickcost=None):
        self.id           = _id
        self.workernum    = workernum
        self.profit       = profit
        self.pattern      = pattern
        self.patternid    = patternid
        self.endtime      = endtime
        self.safepick     = safepick
        self.safepickcost = safepickcost

'''
采集事件
'''
class PickEvent():
    '''
    _id   : 采集事件ID
    name  : 采集事件名称
    type  : 采集事件类型
    intro : 说明
    '''
    def __init__(self,_id=None,name=None,_type=None,intro=None):
        self.id    = _id
        self.name  = name
        self.type  = _type
        self.intro = intro
