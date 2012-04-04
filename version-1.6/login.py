#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  傲视天地登录助手
#  Author      : Jack Syen
#  Created     : 2011.11.11
#  Description : as.yaowan.com
#  Time-stamp: <2011-11-11 23:35:37 jacksyen>
import sys,os
import urllib
import urllib2
import cookielib
import time
import re
import gzip,StringIO
import zlib
import socket
import httplib
import threading
import openanything
import xml.etree.ElementTree as etree
from include import Include
from cityinfo import CityInfo,CityBuild,BuildCD
from request import Request
from playerinfo import PlayerInfo
from chat import ChatThread,ChatSendThread
from config import Config
from trade import TradeThread
from stock import StockThread
from battle import BattleThread
from timehelp import TimeHelp
from dinner import DinnerThread
from maincity import FormationThread,FoodBandCThread
from secretary import SecretaryThread
from outcity import OutCityThread
from general import GeneralThread
from refine  import RefineThread

httplib.HTTPConnection.debuglevel = 1

class yaowan(object):
    def __init__(self,username=None,password=None,serverid=295):
        self.include  = Include(username)
        self.config   = Config()
        self.username = username
        self.password = password
        self.serverid = serverid
        self.timehelp = TimeHelp()

    def start(self):
        self.include.addheaders = [('Content-Type', 'application/x-www-form-urlencoded'),
                                   ('User-agent','Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'),#'Mozilla/5.0(X12;Unixx86_64;9.0.0) By JackSyen'),
                                   ('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                                   ('Accept-Language','zh-cn,zh;q=0.5'),
                                   ('Accept-Encoding','gzip,deflate'),
                                   ('Accept-Charset','GB2312,utf-8;q=0.7,*;q=0.7'),
                                   ('Referer','http://as.yaowan.com'),
                                   ('Host','as.yaowan.com'),
                                   ('Connection','keep-alive'),
                                   ('Cookie','pageReferrInSession=; cnzz_a2184393=0; sin2184393=; rtime=0; ltime=1326903486641; cnzz_eid=66719180-1326902030-; cnzz_a2343924=0; sin2343924=; AJSTAT_ok_pages=1; AJSTAT_ok_times=1')]
        self.Request = Request(self.include)

        self.include.logger.info(u"-------%s开始登录--------" %(self.username))
        if self.username and self.password:
            self.login()
        else:
            self.include.logger.warning(u"用户名或密码为空,程序退出...")
            exit(-1)
        #print "login last cookie:",self.include.cj
        self.initAS()
        
    def login(self):
        url = 'http://as.yaowan.com/Default.php?m=user&action=loginform&astd=1'
        data = {'username' : self.username,
                'password' : self.password,
                'buttion'  : ''}
        self.Request.request(url,data,jsonFormat=False)
        # check login result
        #print "cj:",self.include.cj
        if len(re.findall("userid=\d+",str(self.include.cj)))>0:
            self.include.logger.info(u"登录成功")
        else:
            self.include.logger.error(u"登录失败,程序退出...")
            exit(-1)

    '''
    def getXmlName(self,url):
        if url:
            result = re.findall(r"root/(\w+!?\w+)",url)
            if len(result)>0:
                return str(self.serverid)+"_"+str(result[0])+'.xml'
            return str(self.serverid)+"_"+str(int(time.time()))+"unknown.xml"
            '''

    def initAS(self):
        url = "http://www.yaowan.com/?m=game&game_id=15&district_id=%d" %(683)
        #print "url:",url
        
        self.Request.request(url)  # redicet to http://s322.as.yaowan.com
        
        url = "http://s%d.as.yaowan.com/root/server!getServerTime.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.Request.request(url)
        servertime = self.getServerTime(reqinfo)
        self.include.serverTime = servertime
        self.include.logger.info(u"服务器时间：%s" %(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.include.serverTime/1000))))
        self.gameTimer = GameTimer(self.include)
        self.gameTimer.start()
        
        url = "http://s%d.as.yaowan.com/root/server!getPlayerInfoByUserId.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.Request.request(url)
        #zlib decompress
        res = zlib.decompress(reqinfo.read())
        res = res[res.find("<?xml"):]
        #print 'playerinfo res:',res
        self.playerinfo = self.getPlayerInfo(res)

        if not self.playerinfo.playerid:
            self.include.logger.error(u"未获取到玩家ID，程序退出...")
            exit(-1)
        self.include.logger.info(u"玩家ID:%d,名称：%s,级别：%d" %(self.playerinfo.playerid,self.playerinfo.playername,self.playerinfo.playerlevel))
        
        url = "http://s%d.as.yaowan.com/root/server!getSessionId.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.Request.request(url)
        
        url = "http://s%d.as.yaowan.com/root/mainCity.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.Request.request(url)
        #zlib decompress
        res = zlib.decompress(reqinfo.read())
        res = res[res.find("<?xml"):]
        self.cityinfo = self.getCityInfo(res)
        
        # 如果获取主城信息失败，则表示有验证码
        if len(self.cityinfo.buildlist)==0:
            self.include.logger.error(u"未获取到主城信息，程序退出")
            exit(-1)
            url = "http://s%d.as.yaowan.com/root/validateCode!redirect.action?%d" %(self.serverid,int(time.time()*1000))
            reqinfo = self.Request.request(url)
            #zlib decompress
            res = zlib.decompress(reqinfo.read())
            res = res[res.find("<?xml"):]
            print 'validatecode res:',res
            url = "http://s%d.as.yaowan.com/root/validateCode.action?%d" %(self.serverid,int(time.time()*1000))
            reqinfo = self.Request.request(url)
            #image/jpeg decomress
            print 'validateCode img res:',reqinfo.read()

            #send validate code
            '''
            url = "http://s%d.as.yaowan.com/root/validateCode!code.action?%d" %(self.serverid,int(time.time()*1000))
            #zlib decompress
            res = zlib.decompress(reqinfo.read())
            res = res[res.find("<?xml"):]
            print 'send validate code:',res
            '''
        # 聊天线程
        chatThread = ChatThread(self.include,self.serverid,self.playerinfo)
        chatThread.start()

        # 开发区线程
        if self.playerinfo.isinkfzone == "true":
            self.include.logger.info(u"当前正在开发区中")

        # 全局设置线程
        # 自动委派
        self.tradeThread = None
        if self.config._defaultConfig.get("trade-autostate"):
            self.include.logger.log(u"自动委派功能开启")
            self.tradeThread = TradeThread(self.include,self.serverid,self.playerinfo,self.config)
            self.tradeThread.start()
        # 自动贸易
        if self.config._defaultConfig.get("stock-autostate"):
            self.stockThread = StockThread(self.include,self.serverid,self.playerinfo,self.config)
            self.stockThread.start()

        # 自动征战
        self.battleThread = None
        #print "CD:",self.playerinfo.tokencd,",flag:",self.playerinfo.tokencdflag
        if self.config._defaultConfig.get("battle-autostate"):
            # 在军攻加成时间段才开始(13:00~14:00/20:00~23:00)
            servertime = self.gameTimer.include.serverTime
            localtime = time.localtime(servertime/1000)
            print 'battle localtime:',time.strftime("%Y-%m-%d %H:%M:%S",localtime)
            # 开始征战线程
            #self.battleThread = BattleThread(self.include,self.serverid,self.playerinfo,self.config)
            #self.battleThread.start()
            if 20<=localtime.tm_hour<23 or (13<=localtime.tm_hour<14):
            #if 11<=localtime.tm_hour<14 or 20<=localtime.tm_hour<23:
                # 开始征战线程
                self.battleThread = BattleThread(self.include,self.serverid,self.playerinfo,self.config)
                self.battleThread.start()

        # 自动宴会                
        if self.config._defaultConfig.get("dinner-autostate"):
            self.dinnerThread = None

        # 自动秘书线程（领取俸禄/粮食）
        if self.config._defaultConfig.get("secreatry-auto"):
            self.secretaryThread = SecretaryThread(self.include,self.serverid,self.playerinfo)
            self.secretaryThread.start()

        # 自动采集线程
        self.outcityThread = OutCityThread(self.include,self.serverid,self.playerinfo,self.config)
        self.outcityThread.start()

        # 自动粮食买卖
        self.foodBandCThread = FoodBandCThread(self.include,self.serverid,self.playerinfo)
        self.foodBandCThread.start()

        # 自动开启训练师
        if self.config._defaultConfig.get("trainer-autoopen"):
            self.generalThread = GeneralThread(self.include,self.serverid,self.playerinfo,self.config)
            self.generalThread.start()

        # 精炼工人线程
        if self.playerinfo.playerlevel>=130 and self.config._defaultConfig.get("refine-autostate"):
            self.refineThread = RefineThread(self.include,self.serverid,self.playerinfo)
            self.refineThread.start()
        
        # 主线程
        while True:
            # 判断委派线程
            if self.config._defaultConfig.get("trade-autostate"):
                if self.tradeThread.include.tradeCDFlag:
                    self.tradeThread.include.tradeCD = self.tradeThread.include.tradeCD - 1000
                    if self.tradeThread.include.tradeCD<1000*10 and self.tradeThread.include.tradeCD>0:
                        print u"委派倒计时：",self.tradeThread.include.tradeCD/1000
                    if self.tradeThread.include.tradeCD<0:
                        if self.tradeThread:
                            self.tradeThread = TradeThread(self.tradeThread.include,self.tradeThread.serverid,self.tradeThread.playerinfo,self.config)
                            self.tradeThread.start()
            # 判断征战线程
            if self.config._defaultConfig.get("battle-autostate"):
                servertime = self.gameTimer.include.serverTime
                localtime = time.localtime(servertime/1000)
                if 20<=localtime.tm_hour<23 or (13<=localtime.tm_hour<14):
                #if 20<=localtime.tm_hour<23 or (localtime.tm_hour==13 and localtime.tm_min<30):
                #if 11<=localtime.tm_hour<14 or 20<=localtime.tm_hour<23:
                    if not self.battleThread:
                        self.battleThread = BattleThread(self.include,self.serverid,self.playerinfo,self.config)
                        self.battleThread.start()
                    else:
                        # 继续开始征战
                        if self.battleThread.playerinfo.token>0:
                            if self.battleThread.playerinfo.tokencdflag==1:
                                self.battleThread.playerinfo.tokencd = self.battleThread.playerinfo.tokencd - 1000
                                '''
                                if self.battleThread.playerinfo.tokencd<1000*10 and self.battleThread.playerinfo.tokencd>0:
                                    print "征战倒计时：",self.battleThread.playerinfo.tokencd/1000
                                    if self.battleThread.playerinfo.tokencd<=1000*3 and self.battleThread.playerinfo.tokencd>0:
                                        chatSendThread = ChatSendThread(self.include,self.serverid,"征战倒计时 %d" %(self.battleThread.playerinfo.tokencd/1000),"guojia")
                                        chatSendThread.start()
                                        '''
                                if self.battleThread.playerinfo.tokencd<=0:
                                    if self.battleThread.stoped:
                                        self.battleThread = BattleThread(self.include,self.battleThread.serverid,self.battleThread.playerinfo,self.battleThread.config)
                                        self.battleThread.start()
                        else:
                            self.battleThread.stoped = True
                else:
                    if self.battleThread:
                        self.battleThread.stoped = True

            # 判断宴会线程
            if self.config._defaultConfig.get("dinner-autostate"):
                servertime = self.gameTimer.include.serverTime
                localtime = time.localtime(servertime/1000)
                if 10<=localtime.tm_hour<14 or 19<=localtime.tm_hour<23:
                    if not self.dinnerThread:
                        self.dinnerThread = DinnerThread(self.include,self.serverid,self.playerinfo)
                        self.dinnerThread.start()
                else:
                    self.dinnerThread = None
            time.sleep(1)
    '''
    获得CityInfo对象
    res: 请求URL返回的XML字符串
    '''
    def getCityInfo(self,res):
        if not res:
            print "playerinfo result is null,exit..."
            exit(-1)
            return
        infoXML = etree.XML(res)
        cityinfo = CityInfo()
        buildlist = []
        corlist  = []
        for child in infoXML.getchildren():
            # 主城建筑
            if child.tag=="maincitydto":
                id_            = child.find("id").text
                buildid        = child.find("buildid").text
                buildname      = child.find("buildname").text
                intro          = child.find("intro").text
                cityid         = child.find("cityid").text
                playerid       = child.find("playerid").text
                buildlevel     = child.find("buildlevel").text
                nextcopper     = child.find("nextcopper").text
                cdtime         = child.find("cdtime").text
                lastcdtime     = child.find("lastcdtime").text
                lastupdatetime = child.find("lastupdatetime").text
                citybuild = CityBuild(id_,buildid,buildname,intro,cityid,playerid,
                                     buildlevel,nextcopper,cdtime,lastcdtime,lastupdatetime)
                buildlist.append(citybuild)
            # 建造队列
            if child.tag=="constructordto":
                cid     = int(child.find("cid").text)
                cdflag  = int(child.find("cdflag").text)
                ctime   = int(child.find("ctime").text)
                buildcd = BuildCD(ctime,cid,cdflag)
                #正在建造CD中
                if cdflag:
                    endtime = int(time.time()+ctime)
                    buildcd.endtime = endtime
                corlist.append(buildcd)
        cityinfo.buildlist   = buildlist
        cityinfo.buildcdlist = corlist
        return cityinfo
        
        
    '''
    获得PlayerInfo对象
    res: 请求URL返回的XML字符串
    '''
    def getPlayerInfo(self,res):
        if not res:
            print "playerinfo result is null,exit..."
            exit(-1)
            return
        infoXML = etree.XML(res)
        for child in infoXML.getchildren():
            if child.tag=="player":
                tokencd         = int(child.find("tokencd").text)
                tokencdflag     = int(child.find("tokencdflag").text)
                imposecd        = child.find("imposecd").text
                imposecdflag    = child.find("imposecdflag").text
                protectcd       = child.find("protectcd").text
                playerid        = int(child.find("playerid").text)
                playername      = child.find("playername").text
                playerlevel     = int(child.find("playerlevel").text)
                copper          = child.find("copper").text
                food            = child.find("food").text
                forces          = int(child.find("forces").text)
                sys_gold        = child.find("sys_gold").text
                user_gold       = child.find("user_gold").text
                jyungong        = child.find("jyungong").text
                prestige        = child.find("prestige").text
                nation          = child.find("nation").text
                year            = child.find("year").text
                season          = child.find("season").text
                token           = int(child.find("token").text)
                maxtoken        = child.find("maxtoken").text
                isinkfzone      = child.find("isinkfzone").text
                kfzoneid        = child.find("kfzoneid").text
                kfzonesate      = int(child.find("kfzonesate").text)
                transfercd      = child.find("transfercd").text
                traincurrentnum = child.find("traincurrentnum").text
                maxtrainnum     = child.find("maxtrainnum").text
                stockcd         = child.find("stockcd").text
                inspirestate    = child.find("inspirestate").text
                inspirecd       = child.find("inspirecd").text
                league          = int(child.find("league").text)
                playerinfo = PlayerInfo(tokencd,tokencdflag,imposecd,imposecdflag,protectcd,playerid,playername,playerlevel,
                                        copper,food,forces,sys_gold,user_gold,jyungong,prestige,nation,year,season,
                                        token,maxtoken,transfercd,traincurrentnum,maxtrainnum,stockcd,inspirestate,inspirecd)
                playerinfo.isinkfzone = isinkfzone
                playerinfo.kfzoneid   = kfzoneid
                playerinfo.kfzonesate = kfzonesate
                playerinfo.league     = league
            elif child.tag=="limitvalue":
                if playerinfo:
                    playerinfo.maxfood = child.find("maxfood").text
                    playerinfo.maxcoin = child.find("maxcoin").text
                    playerinfo.maxforce = child.find("maxforce").text
        return playerinfo

    '''
    获得服务器时间
    '''
    def getServerTime(self,res):
        #zlib decompress
        resXML = zlib.decompress(res.read())
        resXML = resXML[resXML.find("<?xml"):]
        timexml = etree.XML(resXML)
        rtime = int(timexml.find("time").text)
        # 因为傲视服务器的时间比当前大8小时，这里减去，便于用户查看
        rtime = rtime - 8*60*60*1000
        print "rtime:",self.timehelp.getStrTime(rtime)
        return rtime

'''
傲视服务器时间线程
'''
class GameTimer(threading.Thread):
    
    def __init__(self,include):
        threading.Thread.__init__(self)
        self.include = include
        
    def run(self):
        while True:
            self.include.serverTime = self.include.serverTime + 1000
            time.sleep(1)

__VERSION__ = '1.6'
if __name__ == '__main__':
    #print __doc__
    from optparse import OptionParser
    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage, version="%prog " + __VERSION__)
    parser.add_option("-u","--user",action="store",type="string",dest="user",help=u"登录用户名")
    parser.add_option("-p","--pwd","--password",action="store",type="string",dest="pwd",help=u"登录密码")
    parser.add_option("-s","--serverid",action="store",type="int",dest="serverid",default="295",help=u"登录服务器ID，默认为295")
    (options,args) = parser.parse_args()
    if not options.user or not options.pwd or not options.serverid:
        print '参数不正确，程序退出'
        exit(-1)
    pyastd = yaowan(options.user,options.pwd,options.serverid)
    pyastd.start()
