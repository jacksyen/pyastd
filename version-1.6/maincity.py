#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request
from updateinfo import PlayerUpdateInfo
'''
主城中的操作
'''

'''
更换阵型
'''
class FormationThread(threading.Thread):
    
    '''
    formationid:
        120: 八卦阵
        160: 雁行阵
    '''
    def __init__(self,include,serverid,formationid):
        threading.Thread.__init__(self)        
        self.request  = Request(include)
        self.serverid = serverid
        self.formationId = formationid

    def run(self):
        # 获得所有阵型
        '''
        url = "http://s%d.as.yaowan.com/root/general!formation.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        print 'general format:',res
        '''
        # 调整阵型
        url = "http://s%d.as.yaowan.com/root/general!saveDefaultFormation.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"formationId":self.formationId}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            infoXML = etree.XML(res)
            for child in infoXML.getchildren():
                if child.tag=="message":
                    print child.text
                    break
            

'''
补兵
'''
class DraughtThread(threading.Thread):

    def __init__(self,include,serverid,playerinfo):
        threading.Thread.__init__(self)        
        self.request  = Request(include)
        self.serverid = serverid
        self.playerinfo = playerinfo

    def run(self):
        self.request.include.logger.info(u"兵力不足10000")
        '''
        # 请求征兵操作
        url = "http://s%d.as.yaowan.com/root/mainCity!preDraught.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        print 'preDraught res:',res
        '''
        
        '''
        补充兵力
        '''
        url = "http://s%d.as.yaowan.com/root/mainCity!draught.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"forceNum":10000}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            infoXML = etree.XML(res)
            updateinfo = PlayerUpdateInfo()
            for child in infoXML.getchildren():
                if child.tag=="playerupdateinfo":
                    food = child.find("food").text
                    forces = child.find("forces").text
                    kfzonestate = child.find("kfzonestate").text
                    updateinfo.food = food
                    updateinfo.forces = forces
                    updateinfo.kfzonestate =kfzonestate
                    if updateinfo.forces:
                        self.request.include.logger.info(u"补充10000兵力成功")
                    else:
                        self.request.include.logger.info(u"补充10000兵力失败")


'''
粮食买卖
'''
class FoodBandCThread(threading.Thread):

    def __init__(self,include,serverid,playerinfo):
        threading.Thread.__init__(self)        
        self.stoped = False
        self.request  = Request(include)
        self.serverid = serverid
        self.playerinfo = playerinfo
        
    '''
    获取粮市信息
    '''
    def getPreFoodBandC(self):
        url = "http://s%d.as.yaowan.com/root/mainCity!preFoodBandC.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        #print 'preFoodBandC res:',res
        if res:
            if res.find("<?xml")<0:
                self.request.include.logger.warning(u"获取粮食买卖信息失败，重新请求...")
                time.sleep(2)
                return self.getPreFoodBandC()
            res = res[res.find("<?xml"):]
            infoXML = etree.XML(res)
            foodbandc = FoodBandC()
            for child in infoXML.getchildren():
                if child.tag=="state":
                    foodbandc.state = child.text
                if child.tag=="buyprice":
                    foodbandc.buyprice = float(child.text)
                if child.tag=="price":
                    foodbandc.price = float(child.text)
                if child.tag=="isup":
                    foodbandc.isup = bool(child.text)
                if child.tag=="bsmax":
                    foodbandc.bsmax = int(child.text)
                if child.tag=="crutrade":
                    foodbandc.crutrade = int(child.text)
                if child.tag=="maxtrade":
                    foodbandc.maxtrade = int(child.text)
                if child.tag=="playerupdateinfo":
                    updateinfo = PlayerUpdateInfo()
                    updateinfo.food = child.findtext("food")
                    updateinfo.kfzonestate = child.findtext("kfzonestate")
                    foodbandc.playerupdateinfo = updateinfo        
            return foodbandc
        return None

    def stop(self):
        self.stoped = True

    def isStoped(self):
        return self.stoped

    '''
    卖出粮食
    '''
    def sellFood(self,foodbandc):
        url = "http://s%d.as.yaowan.com/root/mainCity!foodBandC.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"sell":foodbandc.maxtrade-foodbandc.crutrade}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            self.request.include.logger.info(u"卖出粮食%d,返回:%s" %(foodbandc.maxtrade-foodbandc.crutrade,res))
    
    '''
    买入粮食
    '''
    def buyFood(self,foodbandc):
        url = "http://s%d.as.yaowan.com/root/mainCity!foodBandC.action?%d" %(self.serverid,int(time.time()*1000))
        if foodbandc.bsmax==0:
            print "粮仓已满，不能买入"
            return
        data = {"buy":foodbandc.maxtrade-foodbandc.crutrade}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            self.request.include.logger.info(u"买入粮食%d,返回:%s" %(foodbandc.maxtrade-foodbandc.crutrade,res))

    def run(self):
        while True:
            if self.stoped:
                return
            # 获取粮市信息
            foodbandc = self.getPreFoodBandC()
            if foodbandc.crutrade==foodbandc.maxtrade:
                self.request.include.logger.info(u"今日粮食交易量用完，线程停止")
                self.stop()
                return
            # 偶数天卖出，奇数天买入
            if time.localtime().tm_mday%2==0:
                # 卖出
                if foodbandc.buyprice>1.9:
                    self.sellFood(foodbandc)
            else:
                # 买入
                if foodbandc.buyprice<0.6:
                    self.buyFood(foodbandc)
            # 每30分钟读取一次
            time.sleep(30*60)
        
'''
粮食交易对象
'''
class FoodBandC():
    '''
    state            : 状态
    buyprice         : 买入价格
    price            : 价格
    isup             : 是否上涨
    bsmax            : 粮仓最大剩余量
    crutrade         : 当前买入量
    maxtrade         : 最大买入量
    playerupdateinfo : 玩家更新信息
    '''
    def __init__(self,state=None,buyprice=None,price=None,isup=None,bsmax=None,crutrade=None,maxtrade=None,playerupdateinfo=None):
        self.state            = state
        self.buyprice         =buyprice
        self.price            =price
        self.isup             = isup
        self.bsmax            = bsmax
        self.crutrade         = crutrade
        self.maxtrade         = maxtrade
        self.playerupdateinfo = playerupdateinfo
