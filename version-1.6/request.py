#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket

# 改变全局参数，设置超时时间，可是这样还是无法检测到
socket.setdefaulttimeout(5)

class Request():

    def __init__(self,include):
        self.include = include
        
    def getZipFile(self,content):
        return gzip.GzipFile(fileobj=StringIO.StringIO(content)).read()

    def request(self,url,data={},jsonFormat=True):
        if self.include.retryNum==3:
            print u"重试次数达到3次..."
            exit(-1)
        dataEncoded = urllib.urlencode(data)

        if data:
            req = urllib2.Request(url,data=dataEncoded)
        else:
            req = urllib2.Request(url)
        try:
            res = self.include.opener.open(req)
            #print res.url
            #print res.getcode()
            #print res.info()
            #print self.cj
            if 0:
                test = self.include.opener.open(urllib2.Request('http://www.yaowan.com/?m=user&action=ChgUserInfo'))
                isgzip = test.headers.get("Content-Encoding")
                if isgzip:
                    print self.getZipFile(test.read())
                else:
                    print test.read()
                   #self.cj.save('as.cookie')
        except urllib2.URLError, err:
            print u"获取 URL 发生错误: %s." %err
            print u"重试......"
            self.include.retryNum = self.include.retryNum + 1
            return self.request(url, data, jsonFormat)
        except KeyboardInterrupt:
            print u"用户打断!"
            exit(-1)
        except socket.error, err:
            print u"socket 发生错误: %s." %err
            print u"重试......"
            self.include.retryNum = self.include.retryNum + 1
            return self.request(url, data, jsonFormat)
        except ValueError, err:
            print u"JSON 格式发生错误: %s." %err
            self.include.retryNum = self.include.retryNum + 1
            return self.request(url, data, jsonFormat)
        return res
