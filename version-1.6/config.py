#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config():

    def __init__(self):
        self._defaultConfig = {"coins-minlimit"    : 50000,
                               "trade-autostate"   : False,                   # autostate: 委派自动状态(False:未启用，True：启用)
                               "trade-option"      : 0,                       # option   : 委派选项（0:马商 ，1：披风商)
                               "trade-attribute"   : 243,                     # attribute: 卖出委派物品最高属性值限制
                               "trade-limitlv"     : 55,                      # limitlv  : 卖出委派物品最高级别限制
                               "stock-autostate"   : True,                    # autostate: 贸易自动状态(False:未启用，True：启用)
                               "stock-goodg"       : [u"苹果",u"铁矿"],        # [2,65,140](2：商品ID，65：商品买入最低价，140：商品卖出最高价)
                               "battle-autostate"  : True,                    # 征战自动状态(False:未启用，True:启用)
                               "battle-autocreate" : False,                   # 征战是否可以创建队伍
                               "battle-autoformat" : False,                   # 征战是否自动改变阵型
                               "battle-legion"     : u"金辽",                  # 自动征战的军团名称
                               "dinner-autostate"  : True,                    # 自动宴会状态(False:未启用，True:启用)
                               "secreatry-auto"    : True,                    # 秘书模块功能
                               "trainer-autoopen"  : True,                    # 训练师是否自动开启
                               "trainer-list"      : [u"卢植",u"郑玄",u"黄承彦",u"马云禄",u"关凤",u"吕玲绮",u"张星彩"],   # 训练师开启集合
                               "general-autogrow"  : True,                    # 武将自动转生(此功能必须基于训练自动开启状态)
                               "general-nogrow"    : [u"刘表"],                # 自动转生功能排除的武将名称集合
                               "refine-autostate"  : True,                    # 精炼是否自动开启
                               "refine-opennum"    : 7                        # 每次精炼的工人是几个
                               }
