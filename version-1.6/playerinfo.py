#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
玩家信息对象
'''
class PlayerInfo():

    '''
    tokencd:       军令CD（毫秒）
    tokencdflag:   军令CD标志    imposecd:      征收CD（毫秒）
    imposecdflag:  征收CD标志
    protectcd:     城池保护CD
    playerid:      玩家ID
    playername:    玩家名称
    playerlevel:   玩家级别
    copper:        铜币
    food:          粮食
    forces:        兵力
    sys_gold:      系统赠送的金币
    user_gold:     玩家充值的剩余金币
    jyungong:      军工
    prestige:      威望
    nation:        国家名
    year:          游戏中的年数
    season:        游戏中的季节(1,2,3,4)
    token:         军令数量
    maxtoken:      最大军令数量
    transfercd:    迁移CD
    traincurrentnum:当前训练武将数
    maxtrainnum:   最大训练位
    stockcd:       贸易CD
    inspirestate:  鼓舞状态(1/0)
    inspirecd:     鼓舞CD（毫秒）
    maxfood:       最大粮食数量
    maxcoin:       最大钱币数量
    maxforce:      最大兵力
    isinkfzone:    是否在开发区
    kfzoneid:      开发区ID
    kfzonesate:    开发区建筑收取倒计时
    '''
    def __init__(self,tokencd=None,tokencdflag=None,imposecd=None,
                 imposecdflag=None,protectcd=None,playerid=None,
                 playername=None,playerlevel=None,copper=None,
                 food=None,forces=None,sys_gold=None,user_gold=None,
                 jyungong=None,prestige=None,nation=None,
                 year=None,season=None,token=None,maxtoken=None,
                 transfercd=None,traincurrentnum=None,maxtrainnum=None,
                 stockcd=None,inspirestate=None,inspirecd=None,
                 maxfood=None,maxcoin=None,maxforce=None,isinkfzone=None,
                 kfzoneid=None,kfzonesate=None,league=None):
        self.tokencd         = tokencd
        self.tokencdflag     = tokencdflag
        self.imposecd        = imposecd
        self.imposecdflag    = imposecdflag
        self.protectcd       = protectcd
        self.playerid        = playerid
        self.playername      = playername
        self.playerlevel     = playerlevel
        self.copper          = copper
        self.food            = food
        self.forces          = forces
        self.sys_gold        = sys_gold
        self.user_gold       = user_gold
        self.jyungong        = jyungong
        self.prestige        = prestige
        self.nation          = nation
        self.year            = year
        self.season          = season
        self.token           = token
        self.maxtoken        = maxtoken
        self.transfercd      = transfercd
        self.traincurrentnum = traincurrentnum
        self.maxtrainnum     = maxtrainnum
        self.stockcd         = stockcd
        self.inspirestate    = inspirestate
        self.inspirecd       = inspirecd
        self.maxfood         = maxfood
        self.maxforce        = maxforce
        self.maxtrainnum     = maxtrainnum
        self.isinkfzone      = isinkfzone
        self.kfzoneid        = kfzoneid
        self.kfzonesate      = kfzonesate
        self.league          = league
        
    '''
    获得玩家金币总数
    '''
    def getgold(self):
        return str(int(self.sys_gold) + int(self.user_gold))

    def getseason(self):
        if self.season == '1':
            return "春"
        elif self.season == '2':
            return "夏"
        elif self.season == '3':
            return "秋"
        elif self.season == '4':
            return "冬"
        else:
            return "未知"

    def getnation(self):
        if self.nation == '3':
            return "吴国"
        elif self.nation == '2':
            pass
        elif self.nation == '1':
            pass
        else:
            return "未知" 
