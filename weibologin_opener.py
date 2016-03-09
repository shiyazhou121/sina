#coding:utf-8
import requests
import base64
import re
import urllib,urllib2
import rsa
import json
import binascii
import cookielib


#记录cookies
cj = cookielib.LWPCookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support,urllib2.HTTPHandler)
urllib2.install_opener(opener)  

def weibologin(username,password):
    #得到编码后的用户名
    su  = base64.b64encode(urllib.quote(username))
    url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=account&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.15)&_=1446812708916' %su
    url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
    #得到servertime,nonce, pubkey,rsakv
    resp = urllib2.urlopen(url_prelogin)
    json_data  = re.search('\((.*)\)', resp.read()).group(1)
    data       = json.loads(json_data)
    servertime = data['servertime']
    nonce      = data['nonce']
    pubkey     = data['pubkey']
    rsakv      = data['rsakv']
    #得到编码后的密码，经过rsa加密
    rsaPublickey= int(pubkey,16)
    key = rsa.PublicKey(rsaPublickey,65537)
    message = str(servertime) +'\t' + str(nonce) + '\n' + str(password)
    sp = binascii.b2a_hex(rsa.encrypt(message,key))
    #生成post包
    postdata = {
                        'entry': 'weibo',
                        'gateway': '1',
                        'from': '',
                        'savestate': '7',
                        'userticket': '1',
                        'ssosimplelogin': '1',
                        'vsnf': '1',
                        'vsnval': '',
                        'su': su,
                        'service': 'miniblog',
                        'servertime': servertime,
                        'nonce': nonce,
                        'pwencode': 'rsa2',
                        'sp': sp,
                        'encoding': 'UTF-8',
                        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                        'returntype': 'META',
                        'rsakv' : rsakv,
                        }
                        
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}
    #进行post登陆

    post_data = urllib.urlencode(postdata)
    req = urllib2.Request(url_login, post_data, headers)
    content = urllib2.urlopen(req).read()
    print content
    #得到返回的重定向网址
    login_url = re.findall("location.replace(.*)'",content)
    print login_url[0][2:]
    #得到用户名
    resp = opener.open(login_url[0][2:])
    uid = re.findall('"uniqueid":"(.*?)",',resp.read())[0]
    #登陆个人主页
    print uid
    url = "http://weibo.com/u/"+uid
    print url
    #验证是否登陆成功
    resp = opener.open(url).read()
    lg = re.findall('<meta content="(.*?)，',resp)[0]
    print lg
    if lg =='SpringSkyYz':
        print 'login success!'
    else:
        print 'login fall!'
if __name__ =='__main__':
    weibologin('18810207008','sky123')
