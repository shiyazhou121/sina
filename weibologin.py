#coding:utf-8
import requests
import base64
import re
import urllib,urllib2
import rsa
import json
import binascii
import time
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

session = requests.Session()
def weibologin(username,password):
    #得到编码后的用户名
    su  = base64.b64encode(urllib.quote(username))
    url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=account&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.15)&_=1446812708916' %su
    url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
    #得到servertime,nonce, pubkey,rsakv
    resp = session.get(url_prelogin)
    json_data  = re.search('\((.*)\)', resp.content).group(1)
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
    #进行post登陆
    resp = session.post(url_login,data=postdata)
    print resp.content
    #得到返回的重定向网址
    login_url = re.findall('location.replace\(\'(.*?)\'',resp.content)
    #得到用户名
    resp = session.get(login_url[0])
    uid = re.findall('"uniqueid":"(.*?)",',resp.content)[0]
    #登陆个人主页
    url = "http://weibo.com/u/"+uid
    #验证是否登陆成功
    resp = session.get(url).content
    lg = re.findall('<meta content="(.*?)，',resp)[0]
    print lg
    if lg =='SpringSkyYz':
        print 'login success!'
    else:
        print 'login fall!'

def crawler(url):
    html = session.get(url).content
    return html


def get_total(url):
    html = crawler(url)
    start = html.find('{"pid":"pl_weibo_directtop","js":')
    end = html.find('}',start)
    return html[start:end+1]

if __name__ =='__main__':
    weibologin('18810207008','sky123')
