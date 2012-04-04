#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import urllib2
import threading
import xml.etree.ElementTree as etree
from request import Request
from updateinfo import PlayerUpdateInfo
from timehelp import TimeHelp

'''
委派
'''
class TradeThread(threading.Thread):
    
    '''
    include: include对象
    serverid: 服务器ID
    playerinfo: playerinfo对象
    userconfig: 用户配置对象
    '''
    def __init__(self,include,serverid,playerinfo,config):
        threading.Thread.__init__(self)
        self.stoped       = False
        self.include      = include
        self.request      = Request(include)
        self.config       = config
        self.serverid     = serverid
        self.playerinfo   = playerinfo
        self.timehelp     = TimeHelp()

    def stop(self):
        self.stoped = True

    def isStoped(self):
        return self.stoped

    def run(self):
        # 获得玩家的委派商人信息
        playerMerchant = self.getPlayerMerchant()
        # 判断钱币是否达到最低限制和是否正在CD中
        mincoins = self.config._defaultConfig.get("coins-minlimit")
        if int(self.playerinfo.copper) < mincoins:
            print "钱币小于%d，停止委派" %(mincoins)
            self.stoped = True
        print "auto market cdflag:",int(playerMerchant.cdflag),",cd:",int(playerMerchant.cd)
        if int(playerMerchant.cdflag)==1 and int(playerMerchant.cd)>0:
            print "委派CD中，停止委派,剩余：%s" %(self.timehelp.getDownTime(int(playerMerchant.cd)))
            self.include.tradeCD = int(playerMerchant.cd)
            self.include.tradeCDFlag = True
            self.stoped = True
        while True:
            if self.stoped:
                print "自动委派线程停止"
                return
            # 委派马商
            if not playerMerchant:
                self.stoped = True
                print "委派失败，返回值为空"
                return
            playerMerchant = self.marketTrade(playerMerchant)
            if not playerMerchant.tradesn:
                print '委派失败，未获取到委派结果'
                self.stoped = True
                return
            print playerMerchant.message
            marketresult = self.marketConfirm(playerMerchant)
            if marketresult:# 卖出货物成功
                # 判断委派返回的玩家钱币是否达到最低限制，true:则停止委派
                if int(marketresult.playerupdateinfo.copper) < mincoins:
                    print "钱币小于%d，停止委派" %(mincoins)
                    self.stoped = True
                    return
            else:           # 卖出货物失败
                if playerMerchant.playerupdateinfo and playerMerchant.playerupdateinfo.copper:
                    if int(playerMerchant.playerupdateinfo.copper) < mincoins:
                        print "钱币小于%d，停止委派" %(mincoins)
                        self.stoped = True
                        return
                
            if int(playerMerchant.cdflag)==1: 
                msg = "委派CD中，停止委派,剩余：%s" %(self.timehelp.getDownTime(int(playerMerchant.cd)))
                print msg
                self.include.tradeCD = int(playerMerchant.cd)
                self.include.tradeCDFlag = True
                self.stoped = True
                return
            time.sleep(1)

    '''
    获得玩家的马商信息
    '''
    def getPlayerMerchant(self):
        url = "http://s%d.as.yaowan.com/root/market!getPlayerMerchant.action?%d" %(self.serverid,long(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        print "market res:",res
        # get xml str
        return self.resolveMerXML(res)


    '''
    解析玩家的马商信息和委派过后的马商信息
    content: 要解析的内容
    返回 PlayerMerchant 对象
    '''
    def resolveMerXML(self,content):
        res = content[content.find("<?xml"):]
        if not res:
            return None
        results  = etree.XML(res)
        childli  = results.getchildren()
        playerMerchant = PlayerMerchant()
        merchantlist = []
        for child in childli:
            # 委派结果
            if child.tag=="merchandise":
                merchandiseid      = child.find("merchandiseid").text
                merchandisename    = unicode(child.find("merchandisename").text).encode("utf-8")
                merchandiselv      = child.find("merchandiselv").text
                merchandisequality = child.find("merchandisequality").text
                limitlv            = child.find("limitlv").text
                pic                = child.find("pic").text
                equiptype          = child.find("equiptype").text
                attribute          = child.find("attribute").text
                hp                 = child.find("hp").text
                cost               = child.find("cost").text
                stagename          = child.find("stagename").text
                merchandise = Merchandise(merchandiseid,merchandisename,merchandiselv,merchandisequality,limitlv,pic,equiptype,attribute,hp,cost,stagename)
                playerMerchant.merchandise = merchandise

            if child.tag=="merchant":
                merchantid    = child.find("merchantid").text
                merchantname  = unicode(child.find("merchantname").text).encode("utf-8")
                merchantintro = child.find("merchantintro").text
                cost          = child.find("cost").text
                nextcharge    = child.find("nextcharge").text
                merchant = Merchant(merchantid,merchantname,merchantintro,cost,nextcharge)
                merchantlist.append(merchant)
            if child.tag=="playerupdateinfo":
                #print 'trade playerupdateinfo:',child.getchildren()
                if child.find("copper"):
                    copper = child.find("copper").text
                    updateinfo = PlayerUpdateInfo()
                    updateinfo.copper = copper
                    playerMerchant.playerupdateinfo = updateinfo
            if child.tag=="state":
                state = child.text
                playerMerchant.state = state
            if child.tag=="cd":
                cd = child.text
                playerMerchant.cd = cd
            if child.tag=="cdflag":
                cdflag = child.text
                playerMerchant.cdflag = cdflag
            if child.tag=="free":
                free = child.text
                playerMerchant.free = free
            if child.tag=="gold":
                gold = child.text
                playerMerchant.gold = gold
            if child.tag=="tradesn":
                tradesn = child.text
                playerMerchant.tradesn = tradesn
            if child.tag=="message":
                message = unicode(child.text).encode("utf-8")
                playerMerchant.message = message
        playerMerchant.merchantlist = merchantlist
        return playerMerchant


    '''
    马商委派
    '''
    def marketTrade(self,param):                
        # 得到marketfile中最高的那个商人
        merchant = param.merchantlist[0]
        for i in range(len(param.merchantlist)):
            if int(param.merchantlist[i].merchantid)==5:
                merchant = param.merchantlist[i-1]
                break

        data = {'merchantId' : int(merchant.merchantid),
                     'gold'  : int(param.gold)}
        url = "http://s%d.as.yaowan.com/root/market!trade.action?%d" %(self.serverid,long(time.time()*1000))
        reqinfo = self.request.request(url,data,jsonFormat=False)
        res = zlib.decompress(reqinfo.read())
        # 得到返回的委派货物和商人信息
        playerMerchant = self.resolveMerXML(res)
        return playerMerchant
        
        
    '''
    判断委派的货物是否需要卖出
    '''
    def marketConfirm(self,playerMerchant):
        if (int(playerMerchant.merchandise.limitlv) < self.config._defaultConfig.get("trade-limitlv")) or (int(playerMerchant.merchandise.attribute) < self.config._defaultConfig.get("trade-attribute")):
            # 卖出货物
            data = {'tradeSN' : playerMerchant.tradesn}
            url = "http://s%d.as.yaowan.com/root/market!confirm.action?%d" %(self.serverid,long(time.time()*1000))
            reqinfo = self.request.request(url,data,jsonFormat=False)
            res = zlib.decompress(reqinfo.read())
            res = res[res.find("<?xml"):]
            if not res:
                print "卖出货物%s失败" %(playerMerchant.merchandise.merchandisename)
                return None
            results  = etree.XML(res)
            childli  = results.getchildren()
            # 返回结果对象
            marketresult = MarketResult()
            for child in childli:
                if child.tag=="state":
                    state = child.text
                    if int(state)!=1:
                        print "卖出货物%s失败" %(playerMerchant.merchandise.merchandisename)
                        return None
                    marketresult.state = state
                if child.tag=="usesize": # 使用大小
                    usesize = child.text
                    marketresult.usesize = usesize
                if child.tag=="cost":
                    cost = child.text
                    marketresult.cost = cost
                if child.tag=="playerupdateinfo":
                    copper = child.find("copper").text
                    updateinfo = PlayerUpdateInfo()
                    updateinfo.copper = copper
                    marketresult.playerupdateinfo = updateinfo
            msg = "卖出货物%s成功，获得%d钱币" %(playerMerchant.merchandise.merchandisename,int(cost))
            print msg
            return marketresult
        else:
            msg = "货物%s属性或级别大于配置参数，没有卖出" %(playerMerchant.merchandise.merchandisename)
            print msg
            return None

'''
卖出委派货物的返回结果对象

'''
class MarketResult():
    
    '''
    state            :状态
    usesize          : 仓库使用大小(个数)
    cost             : 货物卖出得到的钱币
    playerupdateinfo : PlayerUpdateInfo对象
    '''
    def __init__(self,state=None,usesize=None,cost=None,playerupdateinfo=None):
        self.state            = state
        self.usesize          = usesize
        self.cost             = cost
        self.playerupdateinfo = playerupdateinfo


'''
玩家委派对象
'''    
class PlayerMerchant():
    '''
    state           : 状态
    merchandise     : 委派货物对象
    merchantlist    : 委派商人对象集合
    cd              : CD时间(毫秒）
    cdflag          : cd标记（0：可用，1：不可用）
    free            : 免费次数
    gold            : 金币?
    tradesn         : 委派的商品SN(编号)
    message         : 委派的消息
    playerupdateinfo : PlayerUpdateInfo对象
    '''
    def __init__(self,state=None,merchandise=None,merchantlist=None,cd=None,cdflag=None,free=None,gold=None,tradesn=None,message=None,playerupdateinfo=None):
        self.state            = state
        self.merchandise      = merchandise
        self.merchantlist     = merchantlist
        self.cd               = cd
        self.cdflag           = cdflag
        self.free             = free
        self.gold             = gold
        self.playerupdateinfo = playerupdateinfo
        # 委派过后才有
        self.tradesn          = tradesn
        self.message          = message
        


'''
委派商人对象
'''
class Merchant():
    '''
    merchantid     : 商人ID
    merchantname   : 商人名称
    merchatntintro : 商人介绍
    cost           : 委派所需钱币
    nextcharge     : 未知？
    '''
    def __init__(self,merchantid=None,merchantname=None,merchantintro=None,cost=None,nextcharge=None):
        self.merchantid    = merchantid
        self.merchantname  = merchantname
        self.merchantintro = merchantintro
        self.cost          = cost
        self.nextcharge    = nextcharge

'''
委派结果：货物对象
'''
class Merchandise():
    '''
    merchandiseid      : 货物ID
    merchandisename    : 货物名称
    merchandiselv      : 货物星级
    merchandisequality : 货物质量
    limitlv            : 限制级别
    pic                : 货物拼音
    equiptype          : 装备类型
    attribute          : 属性
    hp                 : 血量？
    cost               : 价值钱币
    stagename          : 阶段名称
    '''
    def __init__(self,merchandiseid=None,merchandisename=None,merchandiselv=None,merchandisequality=None,limitlv=None,pic=None,equiptype=None,attribute=None,hp=None,cost=None,stagename=None):
        self.merchandiseid      = merchandiseid
        self.merchandisename    = merchandisename
        self.merchandiselv      = merchandiselv
        self.merchandisequality = merchandisequality
        self.limitlv            = limitlv
        self.pic                = pic
        self.equiptype          = equiptype
        self.attribute          = attribute
        self.hp                 = hp
        self.cost               = cost
        self.stagename          = stagename
