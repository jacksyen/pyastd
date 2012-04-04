#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import urllib2
import cookielib
import os,datetime,time
from openanything import SmartRedirectHandler

class Include:
    
    def __init__(self,username):
        # 编码
        self.CODEC = "utf-8"
        
        # 重试次数
        self.retryNum = 0

        # 服务器时间
        self.serverTime = 0

        # 服务器列表 dict
        #self.SERVER_LIST = AllServerList().serverList
        
        # cookie信息
        self.cj = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(SmartRedirectHandler(),cookie_handler)
        urllib2.install_opener(self.opener)

        # 初始化参数
        self.tradeCD     = -1     # 委派CD（毫秒）        
        self.tradeCDFlag = False  # 委派CD标志（True:CD中，False:未CD）

        # 开发区
        self.devZoneBuildCD    = []     # 开发区建筑[(1,0,endtime,devzone)]
        
        self.CHAT_TYPE = [u"私聊",u"全服",u"国家",u"地区",u"附近",
                          u"军团",u"战役",u"黑名单"]
        self.channel = {u"国家" :[3,"%E5%9B%BD%E5%AE%B6"],
                        u"地区" :[4,"%E5%9C%B0%E5%8C%BA"],
                        u"附近" :[5,"%E9%99%84%E8%BF%91"],
                        u"军团" :[6,"%E5%86%9B%E5%9B%A2"]}
        # 征战军团ID
        self.legion_battle = {u"闯王":900016,
                              u"金辽":900021,
                              u"蒙古":900022,
                              u"水浒":900023}

        self.logger = self.getLogger(username)
    '''
    获取日志信息
    '''
    def getLogger(self,username):
        path = "log"
        if not os.path.exists(path):
            os.mkdir(path)
        path += "/%s" %(time.strftime("%Y-%m",time.localtime()))
        if not os.path.exists(path):
            os.mkdir(path)
        # 日志系统
        logger = logging.getLogger()
        handler = logging.FileHandler('%s/%s_%s.log' %(path,username,time.strftime("%Y-%m-%d",time.localtime())))
        farmatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(farmatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
