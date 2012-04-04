#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request

'''
自动宴会线程
'''
class DinnerThread(threading.Thread):
    
    def __init__(self,include,serverid,playerinfo):
        threading.Thread.__init__(self)
        self.request    = Request(include)
        self.serverid   = serverid
        self.playerinfo = playerinfo
        
    def stop(self):
        self.stoped = True

    def isStoped(self):
        return self.stoped

    '''
    获得Dinner对象
    '''
    def getAllDinner(self):
        url = "http://s%d.as.yaowan.com/root/dinner!getAllDinner.action?%d" %(self.serverid,int(time.time()*1000))
        reqinfo = self.request.request(url)
        res = zlib.decompress(reqinfo.read())
        if not res:
            return None
        if res.find("<?xml")<0:
            self.request.include.logger.warning(u"获取宴会信息失败，重新请求...")
            time.sleep(2)
            return self.getAllDinner()
        res = res[res.find("<?xml"):]
        print "getalldinner res:",res
        resXML = etree.XML(res)
        childli  = resXML.getchildren()
        dinner = Dinner()
        teamlist = []
        for child in childli:
            if child.tag == "state":
                dinner.state = int(child.text)
            if child.tag == "teamstate":
                dinner.teamstate = child.text
            if child.tag == "starttime":
                dinner.starttime = child.text
            if child.tag == "endtime":
                dinner.endtime = child.text
            if child.tag == "starttime1":
                dinner.starttime1 = child.text
            if child.tag == "endtime1":
                dinner.endtime1 = child.text
            if child.tag == "team":
                team = DinnerTeam()
                team.teamid = child.find("teamid").text
                team.type  = child.find("type").text
                team.creator =unicode(child.find("creator").text).encode("utf-8")
                team.nation = unicode(child.find("nation").text).encode("utf-8")
                team.num = child.find("num").text
                team.maxnum = child.find("maxnum").text
                team.minnum = child.find("minnum").text
                teamlist.append(team)
            if child.tag == "normaldinner":
                normal = Normaldinner()
                normal.num  = int(child.find("num").text)
                normal.maxnum = int(child.find("maxnum").text)
                normal.jungong = int(child.find("jungong").text)
                dinner.normaldinner = normal
            if child.tag == "identity":
                dinner.identity = child.text
            if child.tag == "membernum":
                dinner.membernum = child.text
            if child.tag == "minmembernum":
                dinner.minmembernum = child.text
            if child.tag == "creator":
                creator = CreatorGuest()
                creator.playerid = child.find("playerid").text
                creator.name     = child.find("name").text
                creator.level    = child.find("level").text
                creator.wine     = child.find("wine").text
                dinner.creator   = creator
            if child.tag == "guest":
                guest = CreatorGuest()
                guest.playerid = child.find("playerid").text
                guest.name     = child.find("name").text
                guest.level    = child.find("level").text
                guest.wine     = child.find("wine").text
                dinner.guest   = guest
        dinner.teamlist = teamlist
        return dinner

    def run(self):
        while True:
            # 获得所有宴会队伍
            dinner = self.getAllDinner()
            # 判断是否获取到信息，失败则停止线程
            if not dinner or dinner.state !=1:
                self.request.include.logger.error(u"获取宴会信息失败，线程停止")
                self.stop()
                return
            if dinner.membernum and dinner.creator:
                # 退出
                url = "http://s%d.as.yaowan.com/root/dinner!leaveDinner.action?%d" %(self.serverid,int(time.time()*1000))
                reqinfo = self.request.request(url,data)
                res = zlib.decompress(reqinfo.read())
                self.request.include.logger.error(u"退出宴会队伍")
                print 'leave dinner res:',res
                time.sleep(5)
                continue
            if dinner.normaldinner:
                if dinner.normaldinner.num==0:
                    self.request.include.logger.warning(u"宴会剩余次数为0，跳过")
                    return
            teamId = None
            for team in dinner.teamlist:
                if team.nation.find("吴国")>=0:
                    teamId = team.teamid
                    break
            if not teamId:
                time.sleep(5)
                continue
            # 确定是否加入
            url = "http://s%d.as.yaowan.com/root/dinner!preJoinDinner.action?%d" %(self.serverid,int(time.time()*1000))
            data = {"teamId":team.teamid}
            reqinfo = self.request.request(url,data)
            res = zlib.decompress(reqinfo.read())
            print 'preJoinDinner:',res

            # 加入
            url = "http://s%d.as.yaowan.com/root/dinner!joinDinner.action?%d" %(self.serverid,int(time.time()*1000))
            data = {"teamId":team.teamid}
            reqinfo = self.request.request(url,data)
            res = zlib.decompress(reqinfo.read())
            self.request.include.logger.info(u"加入由%s创建的宴会队伍" %(team.creator))
            print 'joinDinner:',res
        
            while True:
                # 判断是否已经开启
                '''url = "http://s%d.as.yaowan.com/root/dinner!getAllDinner.action?%d" %(self.serverid,int(time.time()*1000))
                reqinfo = self.request.request(url)
                res = zlib.decompress(reqinfo.read())
                #print "join last getalldinner:",res'''
                # 获得所有宴会队伍
                dinner = self.getAllDinner()
                if not dinner.membernum and not dinner.creator:
                    # 这里需要找到宴会开启后的返回数据
                    self.request.include.logger.info(u"宴会队伍已经开启")
                    break
                time.sleep(3)

class Dinner():
    '''
    state : 状态
    teamstate: 组队状态
    starttime: 开始时间
    endtime: 结束时间
    startime : 开始时间1
    endtime: 结束时间
    teamlist: 队伍集合
    normaldinner: 标准宴会
    # 加入后得到的信息
    identity: ?身份
    membernum: 加入人数
    minmembernum: 最少人数
    creator: 创建者信息
    guest: 加入者信息
    '''
    def __init__(self,state=None,teamstate=None,starttime=None,endtime=None,starttime1=None,endtime1=None,teamlist=None,normaldinner=None,identity=None,membernum=None,minmembernum=None,creator=None,guest=None):
        self.state      = state
        self.teamstate  = teamstate
        self.starttime  = starttime
        self.endtime    = endtime
        self.starttime1 = starttime1
        self.endtime1   = endtime1
        self.teamlist   = teamlist
        self.normaldinner = normaldinner
        # 加入后得到的信息
        self.identity     = identity
        self.membernum    = membernum
        self.minmembernum = minmembernum
        self.creator      = creator
        self.guest        = guest

'''
创建者和加入者对象
'''
class CreatorGuest():
    '''
    playerid : 玩家ID
    name: 玩家名称
    level: 玩家级别
    wine: 酒?
    '''
    def __init__(self,playerid=None,name=None,level=None,wine=None):
        self.playerid = playerid
        self.name     = name
        self.level    = level
        self.wine     = wine

class DinnerTeam():
    '''
    teamid: 队伍ID
    _type: 宴会类型
    creator: 创建者
    nation: 国家
    num: 人数
    maxnum: 最大人数
    minnum: 最小人数
    '''
    def __init__(self,teamid=None,_type=None,creator=None,nation=None,num=None,maxnum=None,minnum=None):
        self.teamid  = teamid
        self.type    = _type
        self.creator = creator
        self.nation  = nation
        self.num     = num
        self.maxnum  = maxnum
        self.minnum  = minnum

class Normaldinner():
    
    def __init__(self,num=None,maxnum=None,jungong=None):
        self.num = num
        self.maxnum = maxnum
        self.jungong = jungong
