#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zlib
import time
import threading
import xml.etree.ElementTree as etree
from request import Request

'''
发送消息线程
'''
class ChatSendThread(threading.Thread):
    def __init__(self,include,serverid,msg,chattype):
        threading.Thread.__init__(self)
        self.serverid = serverid
        self.request  = Request(include)
        self.msg = msg
        self.chattype=chattype
        
    def run(self):
        url = "http://s%d.as.yaowan.com/root/chat!send.action?%d" %(self.serverid,long(time.time()*1000))
        channel = self.request.include.channel.get(self.chattype)[0]
        data = {"channel":channel,
                "contant":self.msg,
                "recver":self.request.include.channel.get(self.chattype)[1]}
        reqinfo = self.request.request(url,data)
        res = zlib.decompress(reqinfo.read())
        print 'chat send res:',res
'''
聊天线程
'''
class ChatThread(threading.Thread):
    def __init__(self,include,serverid,playerinfo):
        threading.Thread.__init__(self)
        self.stoped     = False
        self.include    = include
        self.chat       = Chat(include)
        self.serverid   = serverid
        self.playerinfo = playerinfo

    def stop(self):
        self.stoped = True
        
    def isStoped(self):
        return self.stoped

    def run(self):
        print "聊天线程启动"
        while True:
            if self.stoped:
                print u"请求聊天信息线程停止"
                return
            url = "http://s%d.as.yaowan.com/root/chat.action?%d" %(self.serverid,long(time.time()*1000))
            self.chatinfo = self.chat.getChatInfo(url)
            if not  self.chatinfo:
                continue
            # 国家类型聊天
            nationchatloglist = self.chatinfo.nationchatloglist
            self.showChatMsg(nationchatloglist,2)
            
            # 全服类型聊天
            serverchatloglist = self.chatinfo.serverchatloglist
            self.showChatMsg(serverchatloglist,1)
            time.sleep(12)

    def showChatMsg(self,chatloglist,chattype):
        if chatloglist and len(chatloglist)>0:
            msg = self.include.CHAT_TYPE[chattype]
            for chatlog in chatloglist:
                print u"[%s]%s：%s" %(msg,chatlog.name,chatlog.content)
'''
聊天信息
'''
class Chat():
    
    def __init__(self,include):
        self.request = Request(include)

    '''
    请求聊天URL，解析得到ChatInfo对象
    '''
    def getChatInfo(self,url):
        data = {'length'  :30,
                'channel' :"1,2,3,4,5,6,7,8,9",
                'time'    :0}
        reqinfo = self.request.request(url,data,jsonFormat=False)
        res = zlib.decompress(reqinfo.read())
        if res:
            res = res[res.find("<?xml"):]
            # 解析成ChatInfo对象
            chatinfo = ChatInfo()
            try:
                chatXML = etree.XML(res)
            except:
                print u"[error]读取聊天信息失败"
                return None
            for child in chatXML.getchildren():
                if child.tag=="state":
                   chatinfo.state = child.text
                elif child.tag=="message":
                    chatinfo.message = child.text
                elif child.tag=="chats":
                    # 聊天主信息
                    for chattype in child.getchildren():
                        if chattype.tag=="nationchatlog":
                            # 国家聊天
                            nationchatloglist = []
                            for childlog in chattype.getchildren():
                                chatlog = self.getChatLog(childlog)
                                nationchatloglist.append(chatlog)
                            chatinfo.nationchatloglist = nationchatloglist
                        if chattype.tag=="serverchatlog":
                            # 服务器消息
                            serverchatloglist = []
                            # DOTO
                            for childlog in chattype.getchildren():
                                chatlog = self.getChatLog(childlog)
                                serverchatloglist.append(chatlog)
                            chatinfo.serverchatloglist = serverchatloglist
            return chatinfo
        return None

    def getChatLog(self,child):
        chatlog          = ChatLog()
        chatlog.playerid = child.find("playerid").text
        chatlog.name     = child.find("name").text
        chatlog.content  = child.find("content").text
        chatlog.time     = child.find("time").text
        return chatlog

'''
聊天Action返回的主对象
'''
class ChatInfo():
    '''
    state: 状态
    message: 消息
    nationchatloglist: 国家聊天列表
    serverchatloglist: 服务器消息列表
    '''
    def __init__(self,state=None,message=None,nationchatloglist=None,serverchatloglist=None):
        self.state = state
        self.message = message
        self.nationchatloglist = nationchatloglist
        self.serverchatloglist = serverchatloglist

'''
聊天日志
'''
class ChatLog():
    '''
    playerid : 玩家ID(服务器消息时：-2)
    name     : 玩家名称
    content  : 具体内容
    time     : 发送时间
    '''
    def __init__(self,playerid=None,name=None,content=None,time=None):
        self.playerid = playerid
        self.name     = name
        self.content  = content
        self.time     = time
