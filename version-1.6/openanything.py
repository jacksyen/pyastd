#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self,req,fp,code,msg,headers):
        print "smart 301",headers
        result = urllib2.HTTPRedirectHandler.http_error_301(self,req,fp,code,msg,headers)
        result.status = code
        return result
    
    def http_error_302(self,req,fp,code,msg,headers):
        print "smart 302:",headers
        result = urllib2.HTTPRedirectHandler.http_error_302(self,req,fp,code,msg,headers)
        result.status = code
        return result

