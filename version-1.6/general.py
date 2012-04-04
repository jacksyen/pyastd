#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request
from timehelp import TimeHelp
from updateinfo import PlayerUpdateInfo
'''
武将训练(武魂，训练)
'''

class GeneralThread(threading.Thread):
    
    def __init__(self,include,serverid,playerinfo,config):
        threading.Thread.__init__(self)        
        self.request  = Request(include)
        self.serverid = serverid
        self.playerinfo = playerinfo
        self.config = config
        self.stoped = False
        
    def stop(self):
        self.request.include.logger.warning(u"开始训练师线程停止")
        self.stoped = True

    def isStoped(self):
        return self.stoped
    
    '''
    开启训练师
    '''
    def openTrainer(self,trainer):
        url = "http://s%d.as.yaowan.com/root/trainer!openTrainer.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"gold":0,
                "trainerId":trainer.trainerid}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            # 这里没判断失败情况
            self.request.include.logger.info(u"开启训练师%s成功" %(trainer.name))
        
    
    '''
    判断是否需要开启训练师
    根据配置文件决定开启哪些训练师
    '''
    def isNeedOpenTrainer(self,trainers):
        # 当前剩余武魂
        wuhun = trainers.wuhun
        openTrainers = self.config._defaultConfig.get("trainer-list")
        for trainer in trainers.trainerlist:
            if trainer.name in openTrainers:
                # 如果开启当前训练师武魂大于剩余武魂，则跳过
                # 这里减去了张星彩训练师减少的10%武魂比例
                if trainer.whnum*0.9>wuhun:
                    continue
                # 训练师"张星彩"特例，在剩余次数<=1时就开启
                if (trainer.name!=u"张星彩" and trainer.times<=5) or (trainer.name==u"张星彩" and trainer.times<=2):
                    # 开启
                    self.openTrainer(trainer)
                    wuhun = wuhun-trainer.whnum


    '''
    获得武将训练及训练师信息
    '''
    def getTrainGeneralInfo(self):
        url = "http://s%d.as.yaowan.com/root/general!getTrainGeneralInfo.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        if res:
            if res.find("<?xml")<0:
                self.request.include.logger.warning(u"获取武将训练信息失败，重新请求...")
                time.sleep(2)
                return self.getTrainGeneralInfo()
            res = res[res.find("<?xml"):]
            infoXML = etree.XML(res)
            generalinfo = GeneralInfo()
            generallist    = []
            timemodellist  = []
            trainmodellist = []
            for child in infoXML.getchildren():
                if child.tag=="state":
                    generalinfo.state = child.text
                if child.tag=="general":
                    general = General()
                    general.generalid    = child.findtext("generalid")
                    general.generallevel = int(child.findtext("generallevel"))
                    general.trainflag    = child.findtext("trainflag")
                    general.generalexp   = int(child.findtext("generalexp"))
                    general.autogrow     = int(child.findtext("autogrow"))
                    general.nextlevelexp = child.findtext("nextlevelexp")
                    general.generalname  = child.findtext("generalname")
                    general.pic          = child.findtext("pic")
                    general.shiftlv      = int(child.findtext("shiftlv"))
                    general.trainmodel   = child.findtext("trainmodel")
                    general.exppermin    = child.findtext("exppermin")
                    general.jyungong     = child.findtext("jyungong")
                    general.jyungongexp  = child.findtext("jyungongexp")
                    generallist.append(general)
                if child.tag=="timemodel":
                    timemodel = TimeModel()
                    timemodel.time = child.findtext("time")
                    timemodel.cost = child.findtext("cost")
                    timemodellist.append(timemodel)
                if child.tag=="trainmodel":
                    trainmodel = TrainModel()
                    trainmodel.times = child.findtext("times")
                    trainmodel.name  = child.findtext("name")
                    trainmodel.cost  = child.findtext("cost")
                    trainmodellist.append(trainmodel)
                if child.tag=="currentnum":
                    generalinfo.currentnum = child.text
                if child.tag=="maxnum":
                    generalinfo.maxnum = child.text
                if child.tag=="cost":
                    generalinfo.cost = child.text
                if child.tag=="cd":
                    generalinfo.cd = int(child.text)
                if child.tag=="cdflag":
                    generalinfo.cdflag = int(child.text)
                if child.tag=="goldguide":
                    generalinfo.goldguide = child.text
                if child.tag=="tfnum":
                    generalinfo.tfnum = child.text
                if child.tag=="generaldto":
                    generaldto = GeneraldTo()
                    generaldto.generalid           = child.findtext("generalid")
                    generaldto.generalname         = child.findtext("generalname")
                    generaldto.leader              = child.findtext("leader")
                    generaldto.forces              = child.findtext("forces")
                    generaldto.intelligence        = child.findtext("intelligence")
                    generaldto.enchantleader       = child.findtext("enchantleader")
                    generaldto.enchantforces       = child.findtext("enchantforces")
                    generaldto.enchantintelligence = child.findtext("enchantintelligence")
                    generaldto.skillname           = child.findtext("skillname")
                    generaldto.skillintro          = child.findtext("skillintro")
                    generaldto.solidernum          = child.findtext("solidernum")
                    generaldto.maxsolidernum       = child.findtext("maxsolidernum")
                    generaldto.generalexp          = child.findtext("generalexp")
                    generaldto.generallevel        = child.findtext("generallevel")
                    generaldto.intro               = child.findtext("intro")
                    generaldto.nextlevelexp        = child.findtext("nextlevelexp")
                    generaldto.troopid             = child.findtext("troopid")
                    generaldto.trooptype           = child.findtext("trooptype")
                    generaldto.trooplevel          = child.findtext("trooplevel")
                    generaldto.troopstagename      = child.findtext("troopstagtename")
                    generaldto.trooptypename       = child.findtext("trooptypename")
                    generaldto.troopname           = child.findtext("troopname")
                    generaldto.troopintro          = child.findtext("troopintro")
                    generaldto.pic                 = child.findtext("pic")
                    generaldto.online              = child.findtext("online")
                    generaldto.trainflag           = child.findtext("trainflag")
                    generalinfo.generaldto = generaldto
                if child.tag=="trainers":                    
                    trainers = Trainers()
                    trainerlist = []
                    for cchild in child.getchildren():
                        if cchild.tag=="wuhun":
                            trainers.wuhun = int(cchild.text)
                        if cchild.tag=="totalcost":
                            trainers.totalcost = child.text
                        if cchild.tag=="totalgoldcost":
                            trainers.totalgoldcost = child.text
                        if cchild.tag=="gold":
                            trainers.gold = child.text
                        if cchild.tag=="trainer":
                            trainer = Trainer()
                            trainer.trainerid   = cchild.findtext("trainerid")
                            trainer.name        = cchild.findtext("name")
                            trainer.whnum       = int(cchild.findtext("whnum"))
                            trainer.basictimes  = cchild.findtext("basistimes")
                            trainer.times       = int(cchild.findtext("times"))
                            trainer.lvlimit     = cchild.findtext("lvlimit")
                            trainer.effectintro = cchild.findtext("effectintro")
                            trainer.intro       = cchild.findtext("intro")
                            trainer.pic         = cchild.findtext("pic")
                            trainerlist.append(trainer)
                        trainers.trainerlist = trainerlist
                    generalinfo.trainers = trainers
                if child.tag=="playerupdateinfo":
                    updateinfo = PlayerUpdateInfo()
                    updateinfo.traincurrentnum = child.findtext("traincurrentnum")
                    updateinfo.maxtrainnum = child.findtext("maxtrainnum")
                    updateinfo.kfzonestate = child.findtext("kfzonestate")                    
                    generalinfo.playerupdateinfo = updateinfo
            generalinfo.generallist = generallist
            generalinfo.timemodellist  = timemodellist
            generalinfo.trainmodelist = trainmodellist
            return generalinfo
        return None


    '''
    判断武将中是否有成吉思汗
    若有的话，并且级别小于主城8级，则打开自动转生功能
    '''
    def openAutoShift(self,generallist):
        for general in generallist:
            # 排除不转生的武将
            if general.generalname in self.config._defaultConfig.get("general-nogrow"):
                continue
            if general.autogrow==0 and ((general.shiftlv+8)<=self.playerinfo.playerlevel):
                # 打开自动转生功能
                url = "http://s%d.as.yaowan.com/root/general!setAutoShift.action?%d" %(self.serverid,int(time.time()*1000))
                data = {"generalId":general.generalid,
                        "isAutoShift":1}
                reqinfo = self.request.request(url,data)
                res = zlib.decompress(reqinfo.read())
                if res:
                    res = res[res.find("<?xml"):]
                    self.request.include.logger.info(u"武将%s转生级别%d比主城%d级小于%d级以下，打开自动转生功能" %(general.generalname,general.generallevel,self.playerinfo.playerlevel,8))

    def run(self):
        while True:
            if self.stoped:
                return
            # 获取武将训练及训练师信息
            generalinfo = self.getTrainGeneralInfo()
            if not generalinfo:
                self.request.include.logger.error(u"未获取到武将/训练师信息")
                self.stop()
                return
            if not generalinfo.trainers or not generalinfo.trainers.wuhun:
                self.request.include.logger.error(u"未获取到武魂数量，重新获取..")
                continue
            # 根据配置文件判断是否需要开启训练师
            self.isNeedOpenTrainer(generalinfo.trainers)
            # 武将自动转生功能
            if self.config._defaultConfig.get("general-autogrow"):
                self.openAutoShift(generalinfo.generallist)
            # 如果突飞CD为0或没红，停止线程
            if generalinfo.cd==0 or generalinfo.cdflag==0:
                self.request.include.logger.warning(u"突飞结束，停止开始训练师线程")
                self.stop()
                #time.sleep(5*60)
            else:
                #print "训练师线程%d秒后开启" %(generalinfo.cd/1000+10)
                time.sleep(generalinfo.cd/1000+10)
        

'''
武将训练及训练师信息
'''
class GeneralInfo():
    '''
    state            : 状态
    generallist      : 武将集合
    timemodellist    : 训练时间模式集合
    trainmodellist   : 训练模式集合
    currentnum       : 当前训练人数
    maxnum           : 最大训练人数
    cost             : 钱币
    cd               : 突飞CD
    cdflag           : 突飞CD标记
    goldguide        : 金币指导?(-1)
    tfnum            : ?
    generaldto       : 武将详细信息
    trainers         : 训练师集合
    playerupdateinfo : 玩家更新信息(不一定存在)
    '''
    def __init__(self,state=None,generallist=None,timemodellist=None,trainmodellist=None,currentnum=None,maxnum=None,cost=None,cd=None,cdflag=None,goldguide=None,tfnum=None,generaldto=None,trainers=None,playerupdateinfo=None):
        self.state            = state
        self.generallist      = generallist
        self.timemodellist    = timemodellist
        self.trainmodellist   = trainmodellist
        self.currentnum       = currentnum
        self.maxnum           = maxnum
        self.cost             = cost
        self.cd               = cd
        self.cdflag           = cdflag
        self.goldguide        = goldguide
        self.tfnum            = tfnum
        self.generaldto       = generaldto
        self.trainers         = trainers
        self.playerupdateinfo = playerupdateinfo

'''
武将对象
'''
class General():

    '''
    generalid    : 武将ID
    generallevel : 武将级别
    trainflag    : 训练标志（0：未训练）
    generalexp   : 武将经验
    autogrow     : 自动转生(0:否，1:是)
    nextlevelexp : 下一级所需经验
    generalname  : 武将名称
    pic          : 图片名(武将拼音名)
    shiftlv      : 转生级别
    trainmodel   : 训练模式(null:未训练)
    exppermin    : 每分钟经验
    jyungong     : 突飞所需军工
    jyungongexp  : 军工突飞所得经验

    '''
    def __init__(self,generalid=None,generallevel=None,trainflag=None,generalexp=None,autogrow=None,nextlevelexp=None,generalname=None,pic=None,shiftlv=None,trainmodel=None,exppermin=None,jyungong=None,jyungongexp=None):
        self.generalid    = generalid
        self.generallevel = generallevel
        self.trainflag    = trainflag
        self.generalexp   = generalexp
        self.autogrow     = autogrow
        self.nextlevelexp = nextlevelexp
        self.generalname  = generalname
        self.pic          = pic
        self.shiftlv      = shiftlv
        self.trainmodel   = trainmodel
        self.exppermin    = exppermin
        self.jyungong     = jyungong
        self.jyungongexp  = jyungongexp

'''
训练武将时间对象
'''
class TimeModel():
    '''
    time: 时间(单位:hours)
    cost: 所需资源(钱币或金币)
    '''
    def __init__(self,time=None,cost=None):
        self.time = time
        self.cost = cost

'''
训练武将模式
'''
class TrainModel():
    '''
    times: 时间倍数
    name: 模式名称
    cost: 金币
    '''
    def __init__(self,times=None,name=None,cost=None):
        self.times = times
        self.name = name
        self.cost = cost


'''
武将详细信息
'''
class GeneraldTo():
    '''
    generalid           :武将ID
    generalname         :武将名称
    leader              :属性统
    forces              :属性勇
    intelligence        :属性智
    enchantleader       :魔化统
    enchantforces       :魔化勇
    enchantintelligence :魔化智
    skillname           :?
    skillintro          :?
    solidernum          :兵力
    maxsolidernum       :最大兵力
    generalexp          :普通经验
    generallevel        :普通级别
    intro               :说明
    nextlevelexp        :下一级所需经验
    troopid             :部队ID
    trooptype           :部队类型
    trooplevel          :部队级别
    troopstagename      :部队阶段名称
    trooptypename       :部队类型名称
    troopname           :部队兵种
    troopintro          :部队说明
    pic                 :武将图片名称
    online              :在线?
    trainflag           :训练标志
    '''
    def __init__(self,generalid=None,generalname=None,leader=None,forces=None,intelligence=None,enchantleader=None,enchantforces=None,enchantintelligence=None,skillname=None,skillintro=None,solidernum=None,maxsolidernum=None,generalexp=None,generallevel=None,intro=None,nextlevelexp=None,troopid=None,trooptype=None,trooplevel=None,troopstagename=None,trooptypename=None,troopname=None,troopintro=None,pic=None,online=None,trainflag=None):
        self.generalid           =  generalid
        self.generalname         = generalname
        self.leader              = leader
        self.forces              = forces
        self.intelligence        = intelligence
        self.enchantleader       = enchantleader
        self.enchantforces       = enchantforces
        self.enchantintelligence = enchantintelligence
        self.skillname           = skillname
        self.skillintro          = skillintro
        self.solidernum          = solidernum
        self.maxsolidernum       = maxsolidernum
        self.generalexp          = generalexp
        self.generallevel        = generallevel
        self.intro               = intro
        self.nextlevelexp        = nextlevelexp
        self.troopid             = troopid
        self.trooptype           = trooptype
        self.trooplevel          = trooplevel
        self.troopstagename      = troopstagename
        self.trooptypename       = trooptypename
        self.troopname           = troopname
        self.troopintro          = troopintro
        self.pic                 = pic
        self.online              = online
        self.trainflag           = trainflag

'''
训练师列表对象
'''
class Trainers():
    '''
    wuhun             :武魂数量
    totalcost         :训练师全开所需总武魂
    totalgoldcostgold :训练师全开金币
    gold              :金币
    trainerlist       :训练师集合
    '''
    def __init__(self,wuhun=None,totalcost=None,totalgoldcost=None,gold=None,trainerlist=None):
        self.wuhun         = wuhun
        self.totalcost     = totalcost
        self.totalgoldcost = totalgoldcost
        self.gold          = gold
        self.trainerlist   = trainerlist

'''
训练师对象
'''
class Trainer():
    '''
    trainerid   : 训练师ID
    name        : 训练师名称
    whnum       : 开启所需武魂
    basictimes  : 基本时间（次数）
    times       : 剩余次数
    lvlimit     : 开启所需级别
    effectintro : 功效说明
    inrto       : 说明
    pic         : 图片名称
    '''
    def __init__(self,trainerid=None,name=None,whnum=None,basictimes=None,times=None,lvlimit=None,effectintro=None,inrto=None,pic=None):
        self.trainerid   = trainerid
        self.name        = name
        self.whnum       = whnum
        self.basictimes  = basictimes
        self.times       = times
        self.lvlimit     = lvlimit
        self.effectintro = effectintro
        self.inrto       = inrto
        self.pic         = pic


