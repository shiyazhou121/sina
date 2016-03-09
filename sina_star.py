#coding:utf-8
import requests
import base64
import re
import urllib2,urllib
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
    time.sleep(3)
    html = session.get(url).content
    con = etree.HTML(html)
    return con

def deal(data):
    if len(data) == 0:
        return ''
    elif len(data) == 1:
        return data[0].strip()
    else:
        return ' '.join(data)

def get_content(url):
    con = crawler(url)
    all_url = con.xpath('//h4/a/@href')
    return all_url

def get_each(id):
    url = 'http://ku.ent.sina.com.cn/star/%s' %id
    con = crawler(url)
    #明星名
    name = con.xpath('//h1[@class="pname"]/text()')[0].strip()
    #类型
    style_url = 'http://ku.ent.sina.com.cn/star/base/%s'%id
    con3 = session.get(style_url).content
    style = re.findall('职业：</span>(.*?)</p>',con3)[0].strip()
    #人气排名
    person_tot = con.xpath('//p[@class="person-tot"]/span/text()')[0].strip()
    #参与人气排名的人数
    like_star_num = con.xpath('//span[@class="red like_star_num"]/text()')[0].strip()
    #浏览该明星的人数
    watch_num = con.xpath('//span[@class="red"][1]/text()')[0].strip()
    score_url = 'http://ku.ent.sina.com.cn/comment/score/detail_score?res_id=%s&res_name=star&position=left'%id
    con1 = crawler(score_url)
    #评分
    score = con1.xpath('//span[@class="red resAutoScore"]/text()')[0].strip()
    #参与评分的人数
    person_num = con1.xpath('//span[@class="red2"]/text()')[0].strip()
    return name.encode('utf-8')+'|'+style.encode('utf-8')+'|'+score.encode('utf-8')+'|'+person_num.encode('utf-8')+'|'+person_tot.encode('utf-8')+'|'+like_star_num.encode('utf-8')+'|'+watch_num.encode('utf-8')

def download(num):
    url = 'http://ku.ent.sina.com.cn/star/search&qq-pf-to=pcqq.c2c&area=1&page_no=%s'%num
    all_url = get_content(url)
    for each in all_url:
        start = each.find('star/')
        id = each[start+5:]
        need = get_each(id)
        print need
        f = open('sina_star.txt','a+')
        f.write(need+'\n')
        f.close()   
        time.sleep(5)


if __name__=='__main__':
    weibologin('18810207008','sky123')
    for i in range(1,445):
        download(str(i))
        print 'this page is end!:%s' %str(i)