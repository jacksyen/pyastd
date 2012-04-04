#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request
from updateinfo import PlayerUpdateInfo

'''
小秘书模块
'''

'''
获得秘书模块数据线程
'''
class SecretaryThread(threading.Thread):

    def __init__(self,include,serverid,playerinfo):
        threading.Thread.__init__(self)        
        self.request  = Request(include)
        self.serverid = serverid
        self.playerinfo = playerinfo

    '''
    收取军团粮食    
    lin: 剩余次数
    '''
    def worldImpose(self,lin):
        url = "http://s%d.as.yaowan.com/root/world!impose.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"resId":10}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        print "world impose res",res
        lin = lin-1
        if lin>0:
            self.worldImpose(lin)

    '''
    领取俸禄
    '''
    def officerSaveSalary(self):
        url = "http://s%d.as.yaowan.com/root/officer!saveSalary.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        self.request.include.logger.info(u"领取俸禄,返回结果：%s" %res)        

    '''
    获取秘书信息
    '''
    def getSecretary(self):
        url = "http://s%d.as.yaowan.com/root/secretary.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        #print 'secreatary res:',res
        if res:
            if res.find("<?xml")<0:
                self.request.include.logger.warning(u"获取秘书信息失败，重新请求...")
                time.sleep(2)
                return self.getSecretary()
            res = res[res.find("<?xml"):]
            #print 'secr res xml:',res
            infoXML = etree.XML(res)
            secretary = Secretary()
            for child in infoXML.getchildren():
                if child.tag=="state":
                    secretary.state = child.text
                if child.tag=="liid":
                    secretary.liid = child.text
                if child.tag=="lin":
                    secretary.lin = int(child.text)
                if child.tag=="ss":
                    secretary.ss = int(child.text)
                if child.tag=="fp":
                    secretary.fp = child.text
                if child.tag=="name":
                    secretary.name = child.text
                if child.tag=="lv":
                    secretary.lv = child.text
                if child.tag=="pic":
                    secretary.pic = child.text
                if child.tag=="fun":
                    secretary.fun = child.text
                if child.tag=="tasknum":
                    secretary.tasknum = child.text
                if child.tag=="maxtokennum":
                    secretary.maxtokennum = child.text
                if child.tag=="cd":
                    secretary.cd = child.text
                if child.tag=="tokennum":
                    secretary.tokennum = child.text
                if child.tag=="makenum":
                    secretary.makenum = child.text
                if child.tag=="freer":
                    secretary.freer = child.text
                if child.tag=="task":
                    tasklist = []
                    for cchild in child.getchildren():
                        task = Task()
                        if cchild.tag=="tid":
                            task.tid = cchild.text
                        if cchild.tag=="tname":
                            task.tname = cchild.text
                        if cchild.tag=="tstate":
                            task.tstaet = cchild.text
                        if cchild.tag=="cd":
                            task.cd = cchild.text
                        if cchild.tag=="num":
                            task.num = cchild.text
                        if cchild.tag=="name":
                            task.name = cchild.text
                        tasklist.append(task)
                    secretary.tasklist = tasklist
                if child.tag=="playerupdateinfo":
                    updateinfo = PlayerUpdateInfo()
                    updateinfo.kfzonestate = child.findtext("kfzonestate")
                    secretary.playerupdateinfo = updateinfo
            return secretary
        return None

    def run(self):
        # 获取秘书信息
        secreatry = self.getSecretary()
        
        if not secreatry:
            self.request.include.logger.error(u"获取秘书信息失败,秘书线程停止")
            return
        # 判断是否需要收取军团粮食
        if secreatry.lin>0:
            print u"收取粮食%d次" %(secreatry.lin)
            self.request.include.logger.info(u"收取粮食%d次" %(secreatry.lin))
            # 收取粮食
            self.worldImpose(secreatry.lin)
        
        # 判断是否需要领取俸禄
        if secreatry.ss:
            print u"领取俸禄"
            self.officerSaveSalary()



'''
秘书对象
'''
class Secretary():
    
    '''
    state            : 状态
    liid             : ?
    lin              : 农田收取剩余次数
    ss               :俸禄是否领取（1：未领取，0：已领取）
    fp               :当前粮价
    name             : 秘书名称
    lv               : 秘书级别
    pic              : 秘书图片名称
    fun              : ?
    tasknum          : 任务最大数
    maxtokennum      : 最大可领取军令个数
    cd               : 领取军令CD
    tokennum         : 已领取军令数量
    makenum          : 剩余纺织次数
    freer            : 免费委派（0：已用完，1：未用）
    tasklist         : 任务详细集合
    playerupdateinfo : 玩家更新信息
    '''
    def __init__(self,state=None,liid=None,lin=None,ss=None,fp=None,name=None,lv=None,pic=None,fun=None,tasknum=None,maxtokennum=None,cd=None,tokennum=None,makenum=None,freer=None,tasklist=None,playerupdateinfo=None):
        self.state            = state
        self.liid             = liid
        self.lin              = lin
        self.ss               = ss
        self.fp               = fp
        self.name             = name
        self.lv               = lv
        self.pic              = pic
        self.fun              = fun
        self.tasknum          = tasknum
        self.maxtokennum      = maxtokennum
        self.cd               = cd
        self.tokennum         = tokennum
        self.makenum          = makenum
        self.freer            = freer
        self.tasklist         = tasklist
        self.playerupdateinfo = playerupdateinfo

'''
秘书任务对象
'''
class Task():
    '''
    tid    : 任务ID
    tname  : 任务名称
    tstate : 任务状态(active/)
    cd     : 任务执行CD
    num    : 次数
    name   : 名称
    '''
    def __init__(self,tid=None,tname=None,tstate=None,cd=None,num=None,name=None):
        self.tid    = tid
        self.tname  = tname
        self.tstate = tstate
        self.cd     = cd
        self.num    = num
        self.name   = name
