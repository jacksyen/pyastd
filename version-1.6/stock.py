#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request

'''
贸易信息
'''
class StockThread(threading.Thread):
    
    def __init__(self,include,serverid,playerinfo,config):
        threading.Thread.__init__(self)        
        self.stoped = False
        self.request  = Request(include)
        self.serverid = serverid
        self.playerinfo = playerinfo
        self.config = config

    '''
    请求贸易URL
    '''
    def getStockInfo(self):
        url = "http://s%d.as.yaowan.com/root/stock.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        if res:
            if res.find("<?xml")<0:
                self.request.include.logger.warning(u"获取贸易信息失败，重新请求...")
                time.sleep(2)
                return self.getStockInfo()                
            res = res[res.find("<?xml"):]
            resXML = etree.XML(res)
            childli  = resXML.getchildren()
            stockinfo = StockInfo()
            goodlist  = []
            for child in childli:
                if child.text:
                    if child.tag =="state":
                        stockinfo.state = child.text
                    elif child.tag =="currentpositon":
                        stockinfo.currentpositon = int(child.text)
                    elif child.tag =="postion":
                        stockinfo.postion = int(child.text)
                    elif child.tag =="goodid":
                        stockinfo.goodid = int(child.text)
                    elif child.tag =="numleft":
                        stockinfo.numleft = int(child.text)
                    elif child.tag =="cd":
                        stockinfo.cd = int(child.text)
                    elif child.tag =="cantrade":
                        stockinfo.cantrade = int(child.text)
                    elif child.tag =="nowstate":
                        stockinfo.nowstate = child.text
                elif child.tag=="playerupdateinfo":
                    pass
                else:
                    if child.find("goodid")==None:
                        continue
                    goodinfo = GoodInfo()
                    goodinfo.goodid        = int(child.find("goodid").text)
                    goodinfo.name          = child.find("name").text
                    goodinfo.price         = int(child.find("price").text)
                    goodinfo.num           = int(child.find("num").text)
                    goodinfo.cd            = int(child.find("cd").text)
                    goodinfo.originalprice = int(child.find("originalprice").text)
                    goodinfo.storage       = int(child.find("storage").text)
                    goodinfo.buyprice      = child.find("buyprice").text
                    goodinfo.alter         = child.find("alter").text
                    goodlist.append(goodinfo)
            stockinfo.goodlist = goodlist
            return stockinfo
        return None

    def stop(self):
        self.stoped = True
        self.request.include.logger.warning(u"贸易线程停止")

    def isStoped(self):
        return self.stoped

    def run(self):
        self.request.include.logger.info(u"自动贸易功能开启")
        while True:
            if self.stoped:
                return
            # 获得贸易信息
            stockinfo = self.getStockInfo()
            if not stockinfo:
                self.request.include.logger.error(u"获取贸易信息失败")
                self.stop()
                return
            # 判断是否需要买入或卖出
            self.isNeedStock(stockinfo)
            # 每5分钟读取一次
            time.sleep(5*60)

    '''
    判断是否需要贸易
    '''
    def isNeedStock(self,stockinfo):
        if stockinfo.cd==1:
            self.request.include.logger.info(u"贸易CD中")
            return
        if stockinfo.numleft>0:
            self.request.include.logger.info(u"贸易次数已存在")
            return
        if stockinfo.cantrade==0:
            self.request.include.logger.info(u"贸易停盘中")
            return
        if len(self.config._defaultConfig.get("stock-goodg"))==0:
            self.request.include.logger.error(u"贸易配置参数不正确")
            return
        for g in self.config._defaultConfig.get("stock-goodg"):
            for goodinfo in stockinfo.goodlist:
                if g == goodinfo.name:
                    # 如果库存大于0
                    if goodinfo.storage>0:
                        #print "商品%s原价比为：%.1f" %(goodinfo.name,goodinfo.getProportion())
                        if goodinfo.getProportion()>=125 or (g==u"铁矿" and goodinfo.getProportion()>=117) or (g==u"苹果" and goodinfo.getProportion()>=117): # 卖出(除了铁矿,苹果在原价比117%时卖出，其它都是125%卖出)
                            url = "http://s%d.as.yaowan.com/root/stock!tradeStock.action?%d" %(self.serverid,int(time.time()*1000))
                            data = {'tradeType':1,
                                    'num':99,
                                    'goodId':goodinfo.goodid}
                            reqinfo = self.request.request(url,data)
                            res = zlib.decompress(reqinfo.read())
                            self.request.include.logger.info(u"商品%s原价比为：%.1f,卖出%d次" %(goodinfo.name,goodinfo.getProportion(),99))
                            return
                    if (stockinfo.postion-stockinfo.currentpositon)>=goodinfo.num:
                        #print "商品%s原价比为：%.1f" %(goodinfo.name,goodinfo.getProportion())
                        if goodinfo.getProportion()<=70:  # 买入
                            url = "http://s%d.as.yaowan.com/root/stock!tradeStock.action?%d" %(self.serverid,int(time.time()*1000))
                            data = {'tradeType':0,
                                    'num':99,
                                    'goodId':goodinfo.goodid}
                            reqinfo = self.request.request(url,data)
                            res = zlib.decompress(reqinfo.read())
                            self.request.include.logger.info(u"商品%s原价比为：%.1f,买入%d次" %(goodinfo.name,goodinfo.getProportion(),99))
                            return

'''
贸易对象
'''
class StockInfo():
    
    '''
    state          : 状态
    currentpositon : 当前贸易占用的位置
    postion        : 贸易总位置
    goodid         : 当前贸易的商品ID
    numleft        : 当前商品的贸易次数
    cd             : 贸易剩余CD
    cantrade       : 是否可以贸易（1：可以，0:贸易停盘）
    nowstate       : 当前贸易状态说明
    goodlist       : 贸易商品集合
    '''
    def __init__(self,state=None,currentpositon=None,postion=None,goodid=None,
                numleft=None,cd=None,cantrade=None,nowstate=None,goodlist=None):
        self.state          = state
        self.currentpositon = currentpositon
        self.postion        = postion
        self.goodid         = goodid
        self.numleft        = numleft
        self.cd             = cd
        self.cantrade       = cantrade
        self.nowstate       = nowstate
        self.goodlist       = goodlist

class GoodInfo():
    
    '''
    goodid: 商品ID
    name: 商品名
    price: 最新价格
    num: 交易量
    cd: 贸易CD
    originalprice:原来的价格（不知是哪个原来）
    storage: 库存
    buyprice: 买入价格
    alter: 提示
    '''
    def __init__(self,goodid=None,name=None,price=None,num=None,cd=None,
                 originalprice=None,storage=None,buyprice=None,alter=None):
        self.goodid        = goodid
        self.name          = name
        self.price         = price
        self.num           = num
        self.cd            = cd
        self.originalprice = originalprice
        self.storage       = storage
        self.buyprice      = buyprice
        self.alter         = alter

    '''
    获得商品原价比,百分比
    例如:118.9
    '''
    def getProportion(self):
        return round(self.price*1.0/self.originalprice*100,1)
