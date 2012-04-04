#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request
from timehelp import TimeHelp
from chat import ChatSendThread
from maincity import DraughtThread,FormationThread

'''
自动征战线程
'''
class BattleThread(threading.Thread):
    
    def __init__(self,include,serverid,playerinfo,config):
        threading.Thread.__init__(self)        
        self.stoped     = False
        self.request    = Request(include)
        self.serverid   = serverid
        self.playerinfo = playerinfo
        self.config     = config
        self.timehelp   = TimeHelp()        
        self.armiesId   = self.request.include.legion_battle.get(self.config._defaultConfig.get("battle-legion"))
        
    def stop(self):
        self.request.include.logger.info(u"自动刷军团线程停止")
        if self.config._defaultConfig.get("battle-autoformat"):
            # 调整阵型为雁行阵
            formatThread = FormationThread(self.request.include,self.serverid,160)
            formatThread.start()
        self.stoped = True

    def isStoped(self):
        return self.stoped

    def run(self):
        self.request.include.logger.info(u"自动刷%s军团功能启动" %(self.config._defaultConfig.get("battle-legion")))
        # 调整阵型为：八卦阵
        if self.config._defaultConfig.get("battle-autoformat"):
            formatThread = FormationThread(self.request.include,self.serverid,120)
            formatThread.start()
        while True:
            if self.stoped:
                return
            if self.playerinfo.forces<=10000:
                draughtThread = DraughtThread(self.request.include,self.serverid,self.playerinfo)
                draughtThread.start()
            if self.playerinfo.token==0:
                self.request.include.logger.info(u"军令数量为0")                
                self.stop()
                return
            if self.playerinfo.tokencdflag==1:
                if self.playerinfo.tokencd>0:
                    chatSendThread = ChatSendThread(self.request.include,self.serverid,u"征战CD中，剩余:%s" %(self.timehelp.getDownTime(self.playerinfo.tokencd)),u"国家")
                    chatSendThread.start()
                    self.request.include.logger.info(u"征战CD中，剩余 %s" %(self.timehelp.getDownTime(self.playerinfo.tokencd)))
                    self.stop()
                    return
            # 获得征战队伍信息
            battleTeamInfo = self.getTeamInfo()
            role = None
            if len(battleTeamInfo.memberlist)>0:
                for member in battleTeamInfo.memberlist:
                    if member.playerid == int(self.playerinfo.playerid):
                        if member.role=="CREATER":
                            # 解散队伍
                            self.dismissTeam()
                        elif member.role=="COMMON":
                            # 退出队伍
                            self.quitTeam()
                        break
            # 重新获得队伍信息
            battleTeamInfo = self.getTeamInfo()
            # 判断是否存在合适的征战队伍,返回合适的队伍
            team = self.isExistsTeam(battleTeamInfo)
            if team:
                # 加入征战队伍
                if not self.joinTeam(team):
                    self.stop()
                    return 
                role = "COMMON"
            else:
                # 若配置文件中不可以创建征战队伍，就跳过继续等待加入队伍
                if not self.config._defaultConfig.get("battle-autocreate"):
                    while True:
                        battleTeamInfo = self.getTeamInfo()
                        team = self.isExistsTeam(battleTeamInfo)
                        if team:
                            # 加入征战队伍
                            if not self.joinTeam(team):
                                self.stop()
                                return
                            role = "COMMON"
                            break
                        time.sleep(3)
                else:
                    # 创建征战队伍
                    url = "http://s%d.as.yaowan.com/root/multiBattle!createTeam.action?%d" %(self.serverid,int(time.time()*1000))
                    data = {"rule":"4:0;2",
                            "armiesId":self.armiesId}
                    reqinfo = self.request.request(url,data,jsonFormat=False)
                    res = zlib.decompress(reqinfo.read())
                    print "create:",res
                    role = "CREATER"
            sendnum = 0
            battlePer = {}
            while True:
                battleTeamInfo = self.getTeamInfo()
                # 判断加入的队伍是否已经开始
                if battleTeamInfo.sceneevent:
                    playerbattleinfo = battleTeamInfo.sceneevent.playerbattleinfo
                    if playerbattleinfo:
                        self.playerinfo.token   = playerbattleinfo.token
                        self.playerinfo.tokencd = playerbattleinfo.tokencd
                        self.playerinfo.tokencdflag = playerbattleinfo.tokencdflag
                        self.playerinfo.forces  = playerbattleinfo.forces
                        #print "剩余总军工:",playerbattleinfo.jyungong
                        self.request.include.logger.info(u"剩余总军工：%d" %(playerbattleinfo.jyungong))
                        break

                # 判断加入的队伍是否存在
                if len(battleTeamInfo.memberlist)==0:
                    self.request.include.logger.info(u"征战队伍解散")
                    break
                if role=="CREATER":
                    for member in battleTeamInfo.memberlist:
                        if member.playername.find("u老鬼")>=0:
                            battlePer.setdefault("laogui",1)
                        elif member.playername.find(u"米粥")>=0:
                            battlePer.setdefault("mizhou",1)
                        elif member.playername.find(u"不停")>=0:
                            battlePer.setdefault("buting",1)
                        elif member.playername.find(u"豆包")>=0:
                            battlePer.setdefault("doubao",1)
                        elif member.playername.find(u"人民")>=0:
                            battlePer.setdefault("renming",1)
                        elif member.playername.find(u"猪猪")>=0:
                            battlePer.setdefault("zhuzhu",1)
                        elif member.playername.find(u"亚特")>=0:
                            battlePer.setdefault("yate",1)
                        elif member.playername.find(u"来时")>=0:
                            battlePer.setdefault("laishi",1)
                        elif member.playername.find(u"小馬")>=0:
                            battlePer.setdefault("xiaomage",1)
                        elif member.playername.find(u"睡觉")>=0:
                            battlePer.setdefault("shuijiao",1)
                    # 自己创建的队伍需要6个成员以上才能开启
                    if battleTeamInfo.currentnum>=5 or (len(battlePer.items())>=2 and battleTeamInfo.currentnum>=4):
                        # 开始征战,获得征战结果
                        battleInfo = self.getBattleInfo()
                        if battleInfo.sceneevent:
                            playerbattleinfo = battleInfo.sceneevent.playerbattleinfo
                            if playerbattleinfo:
                                self.playerinfo.token   = playerbattleinfo.token
                                self.playerinfo.tokencd = playerbattleinfo.tokencd
                                self.playerinfo.tokencdflag = playerbattleinfo.tokencdflag
                                self.playerinfo.forces  = playerbattleinfo.forces
                                print u"剩余总军工:",playerbattleinfo.jyungong
                                break
                    else:
                        print u"征战队伍已开启，需要%d个成员才能开始..." %(5-battleTeamInfo.currentnum)
                        if (5-battleTeamInfo.currentnum)<=1:
                            if sendnum<=1:
                                chatSendThread = ChatSendThread(self.request.include,self.serverid,u"闯王=%d" %(5-battleTeamInfo.currentnum),"国家")
                                chatSendThread.start()
                                sendnum = sendnum + 1
                    time.sleep(3)
                time.sleep(3)
                
            
            '''
            # 未知
            url = "http://s%d.as.yaowan.com/root/battle.action?%d "  %(self.serverid,int(time.time()*1000))
            reqinfo = self.request.request(url)
            res = zlib.decompress(reqinfo.read())
            print reqinfo            
            '''

    '''
    加入征战队伍
    team: 队伍信息
    '''
    def joinTeam(self,team):
        url = "http://s%d.as.yaowan.com/root/multiBattle!joinTeam.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"teamId":team.teamid}
        reqinfo = self.request.request(url,data,jsonFormat=False)
        res = zlib.decompress(reqinfo.read())
        if res.find(u"军令还没有冷却")>=0:
            self.request.include.logger.warning(u"军令还没有冷却，不可以征战")
            return False
        self.request.include.logger.info(u"加入由玩家:%s 创建的征战队伍" %team.teamname)
        print 'join:',res
        return True

    '''
    退出队伍
    '''
    def quitTeam(self):
        self.request.include.logger.info(u"退出队伍")
        url = "http://s%d.as.yaowan.com/root/multiBattle!quit.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        print 'quit:',res

    '''
    解散队伍
    '''
    def dismissTeam(self):
        self.request.include.logger.info(u"解散队伍")
        url = "http://s%d.as.yaowan.com/root/multiBattle!dismiss.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        print 'dismiss:',res

    '''
    判断是否存在合适的征战队伍
    '''
    def isExistsTeam(self,battleTeamInfo):
        for team in battleTeamInfo.teamlist:
            if self.playerinfo.league==2:
                if team.condition.find(u"魏国")>=0 and (team.currentnum!=team.maxnum):
                    return team
            if team.condition.find(u"吴国")>=0 and (team.currentnum!=team.maxnum):
                return team
            if team.condition.find(u"英雄")>=0 and (team.currentnum!=team.maxnum):
                return team
        return None    
    '''
    玩家自己创建，获得征战结果
    返回BattleInfo对象
    '''
    def getBattleInfo(self):
        url = "http://s%d.as.yaowan.com/root/multiBattle!battle.action?%d"  %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]            
            resXML = etree.XML(res)
            childli  = resXML.getchildren()
            battleInfo = BattleInfo()
            for child in childli:
                if child.tag=="state":
                    battleInfo.state = child.text
                if child.tag=="message":
                    battleInfo.message = child.text
                if child.tag=="sceneevent":
                    sceneevent = SceneEvent()
                    for cchild in child:
                        if cchild.tag=="scene":
                            sceneevent.scene = child.text
                        if cchild.tag=="kfzonestate":
                            sceneevent.kfzonestate = child.text
                        if cchild.tag=="playerbattleinfo":
                            print 'battle playerbattleinfo:',cchild.getchildren()
                            forces           = int(cchild.find("forces").text)
                            if cchild.findtext("jyungong"):
                                jyungong         = int(cchild.find("jyungong").text)
                            else:
                                jyungong     = -1
                            token            = int(cchild.find("token").text)
                            tokencd          = int(cchild.find("tokencd").text)
                            tokencdflag      = int(cchild.find("tokencdflag").text)
                            kfzonestate      = cchild.find("kfzonestate").text
                            playerbattleinfo = PlayerBattleInfo(forces,jyungong,token,tokencd,tokencdflag,kfzonestate)
                            sceneevent.playerbattleinfo = playerbattleinfo
                    battleInfo.sceneevent = sceneevent
            return battleInfo

    '''
    获得征战队伍信息
    '''
    def getTeamInfo(self):
        url = "http://s%d.as.yaowan.com/root/multiBattle!getTeamInfo.action?%d" %(self.serverid,int(time.time()*1000))
        data = {"armiesId":self.armiesId}
        reqinfo = self.request.request(url,data,jsonFormat=False)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]            
            resXML = etree.XML(res)
            childli  = resXML.getchildren()
            battleTeamInfo = BattleTeamInfo()
            teamlist = []
            memberlist = []
            for child in childli:
                if child.tag=="state":
                    battleTeamInfo.state = child.text
                if child.tag=="maxnum":
                    battleTeamInfo.maxnum = int(child.text)
                if child.tag=="currentnum":
                    battleTeamInfo.currentnum = int(child.text)
                if child.tag=="armies":                    
                    _id       = child.find("id").text
                    name      = child.find("name").text
                    level     = child.find("level").text
                    minplayer = child.find("minplayer").text
                    maxplayer = child.find("maxplayer").text
                    maxwinnum = child.find("maxwinnum").text
                    battlenum = child.find("battlenum").text
                    honor     = child.find("honor").text
                    itemname  = child.find("itemname").text
                    armynum   = child.find("armynum").text
                    _filter   = child.find("filter").text
                    itempic   = child.find("itempic").text
                    armies = Armies(_id,name,level,minplayer,maxplayer,maxwinnum,battlenum,honor,itemname,armynum,_filter,itempic)
                    battleTeamInfo.armies = armies
                if child.tag=="team":
                    teamid     = child.find("teamid").text
                    teamname   = child.find("teamname").text
                    maxnum     = int(child.find("maxnum").text)
                    targetname = child.find("targetname").text
                    currentnum = int(child.find("currentnum").text)
                    condition  = child.find("condition").text
                    team = Team(teamid,teamname,maxnum,targetname,currentnum,condition)
                    teamlist.append(team)
                if child.tag=="member":
                    playername    = child.find("playername").text
                    playerid      = int(child.find("playerid").text)
                    playerlevel   = child.find("playerlevel").text
                    role          = child.find("role").text
                    attlv         = child.find("attlv").text
                    deflv         = child.find("deflv").text
                    makemode      = child.find("makemode").text
                    maxsolidernum = child.find("maxsolidernum").text
                    solidernum    = child.find("solidernum").text
                    member = Member(playername,playerid,playerlevel,role,attlv,deflv,makemode,maxsolidernum,solidernum)
                    memberlist.append(member)
                if child.tag=="sceneevent":
                    sceneevent = SceneEvent()
                    for cchild in child:
                        if cchild.tag=="scene":
                            sceneevent.scene = child.text
                        if cchild.tag=="kfzonestate":
                            sceneevent.kfzonestate = child.text
                        if cchild.tag=="playerbattleinfo":
                            print 'playerbattleinfo:',cchild.getchildren()
                            if cchild.findtext("forces"):
                                forces           = int(cchild.find("forces").text)
                            else:
                                forces = -1
                            if cchild.findtext("jyungong"):
                                jyungong         = int(cchild.find("jyungong").text)
                            else:
                                jyungong = -1
                            if cchild.findtext("token"):
                                token = int(cchild.findtext("token"))
                            else:
                                token = -1
                            tokencd          = int(cchild.find("tokencd").text)
                            tokencdflag      = int(cchild.find("tokencdflag").text)                                
                            kfzonestate      = cchild.find("kfzonestate").text
                            playerbattleinfo = PlayerBattleInfo(forces,jyungong,token,tokencd,tokencdflag,kfzonestate)
                            sceneevent.playerbattleinfo = playerbattleinfo
                    battleTeamInfo.sceneevent = sceneevent
            battleTeamInfo.teamlist = teamlist
            battleTeamInfo.memberlist = memberlist
            
            return battleTeamInfo
''' 
自己创建，然后开始征战获得的对象
'''
class BattleInfo():
    '''
    state    : 请求状态
    message  : ？
    sceneevnent: 征战结果信息
    '''
    def __init__(self,state=None,message=None,sceneevent=None):
        self.state = state
        self.message = message
        self.sceneevent = sceneevent
            
class BattleTeamInfo():
    
    '''
    state      : 请求状态
    armies     : NPC部队信息
    teamlist   : 组队列表
    maxnum     : 最大人数
    currentnum : 当前队伍人数
    memberlist : 新建队伍的人员信息
    sceneevent : 征战结果信息
    '''
    def __init__(self,armies=None,teamlist=None,maxnum=None,currentnum=None,memberlist=None,sceneevent=None):
        self.armies     = armies
        self.teamlist   = teamlist
        self.maxnum     = maxnum
        self.currentnum = currentnum
        self.memberlist = memberlist
        self.sceneevent = sceneevent

class Armies():
    '''
    id        : NPC部队ID
    name      : NPC部队名称
    level     : NPC部队级别
    minplayer : 最少玩家数
    maxplayer : 最多玩家数
    maxwinnum : 最大连胜数
    battlenum : ?
    honor     : 获得军攻
    itemname  : 有概率获得的物品名称
    armynum   : NPC部队数量
    filter    : ?
    itempic   : NPC部队图片
    '''
    def __init__(self,_id=None,name=None,level=None,minplayer=None,maxplayer=None,maxwinnum=None,
                 battlenum=None,honor=None,itemname=None,armynum=None,_filter=None,itempic=None):
        self.id        = _id
        self.name      = name
        self.level     = level
        self.minplayer = minplayer
        self.maxplayer = maxplayer
        self.maxwinnum = maxwinnum
        self.battlenum = battlenum
        self.honor     = honor
        self.itemname  = itemname
        self.armynum   = armynum
        self.filter    = _filter
        self.itempic   = itempic

class Team():
    '''
    teamid     : 征战组队ID
    teamname   : 队伍名称
    maxnum     : 最大数量
    targetname : 目标名称
    currentnum : 当前人数
    condition  : 部队进入限制（根据此字段判断国家名称）
    '''
    def __init__(self,teamid=None,teamname=None,maxnum=None,targetname=None,currentnum=None,condition=None):
        self.teamid     = teamid
        self.teamname   = teamname
        self.maxnum     = maxnum
        self.targetname = targetname
        self.currentnum = currentnum
        self.condition  = condition

class Member():
    '''
    playername    : 玩家名称
    playerid      : 玩家ID
    playerlevel   : 玩家级别
    role          : 角色(CREATER/COMMON)
    attlv         : 攻击级别
    deflv         : 防御级别
    makemode      : 构造模式?(0)
    maxsolidernum : 最大兵力数量
    solidernum    : 兵力数量
    '''
    def __init__(self,playername=None,playerid=None,playerlevel=None,role=None,attlv=None,deflv=None,makemode=None,
                 maxsolidernum=None,solidernum=None):
        self.playername    = playername
        self.playerid      = playerid
        self.playerlevel   = playerlevel
        self.role          = role
        self.attlv         = attlv
        self.deflv         = deflv
        self.makemode      = makemode
        self.maxsolidernum = maxsolidernum
        self.solidernum    = solidernum

'''
征战结果对象
'''
class SceneEvent():
    '''
    scene            : 多人战斗
    kfzonestate      : ?开发区状态
    playerbattleinfo : 征战后玩家信息
    '''
    def __init__(self,scene=None,kfzonestate=None,playerbattleinfo=None):
        self.scene = scene
        self.kfzonestate = kfzonestate
        self.playerbattleinfo = playerbattleinfo
        

'''
征战后的玩家信息
'''
class PlayerBattleInfo():
    '''
    forces      : 剩余兵力
    jyungong    : 剩余总军工
    token       : 剩余军令
    tokencd     : 剩余军令CD
    tokencdflag : 军令CD标志（0：可用，1：不可用）
    kfzonestate : 开发区状态?
    '''
    def __init__(self,forces=None,jyungong=None,token=None,tokencd=None,tokencdflag=None,kfzonestate=None):
        self.forces      = forces
        self.jyungong    = jyungong
        self.token       = token
        self.tokencd     = tokencd
        self.tokencdflag = tokencdflag
        self.kfzonestate = kfzonestate
