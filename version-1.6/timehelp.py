# -*- coding: utf-8 -*-
import time

'''
时间帮助类
'''
class TimeHelp():
    '''
    将毫秒数转换成时间字符串，"2011-12-09 12:00:00"
    t: 毫秒数
    '''
    def getStrTime(self,t):
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(t/1000))

    '''
    将毫秒数转换成倒计时字符串，"01:20:10"或"40:59"
    millseconds:毫秒数
    '''
    def getDownTime(self,millseconds):
        if millseconds<3600*1000:
            return time.strftime("%M:%S",time.gmtime(millseconds/1000))
        return time.strftime("%H:%M:%S",time.gmtime(millseconds/1000))
