# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 22:55:30 2016

@author: lixiang
"""

import urllib2
import socket
import time
from bs4 import BeautifulSoup    #besutifulsoup的第三版  

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

sleep_time=30

def getUrlRespHtml(url):
    heads = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Charset':'GB2312,utf-8;q=0.7,*;q=0.7', 
            'Accept-Language':'zh-cn,zh;q=0.5', 
            'Cache-Control':'max-age=0', 
            'Connection':'keep-alive', 
            'Host':'John', 
            'Keep-Alive':'115', 
            'Referer':url, 
            'User-Agent':'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.14) Gecko/20110221 Ubuntu/10.10 (maverick) Firefox/3.6.14'}
 
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener) 
    req = urllib2.Request(url)
    opener.addheaders = heads.items()
#    respHtml = opener.open(req).read()
#    return respHtml.decode('gbk').encode('utf-8')
    try:
        respHtml = opener.open(req).read()
    except urllib2.HTTPError, e:
        print e.code
    return respHtml

def getCities():
    site='http://pm25.in'
    html = getUrlRespHtml(site)
    soup = BeautifulSoup(html) 
    hrefs = soup.find("div",{"class":"all"}).find_all('a')
    cs=[]
    for href in hrefs:
        c=href['href']
        c=c[1:len(c)]
        cs.append(c)
#    cs=cs[0:10]
    return list(set(cs))
    
def getCurrentHour():
    socket.setdefaulttimeout(60) # 60 秒钟后超时
    file_c = open('city.txt','a')
    file_s = open('site.txt','a')
#    cities=['beijing','tianjin','shanghai']
    cities=getCities()
    print 'city count is：'+str(len(cities))
#    city='tianjin'
    for city in cities:
        ind=cities.index(city)
        if ind%50==0:
            time.sleep(sleep_time)
        site ='http://pm25.in/' + city + '.html'  
        print str(ind)+' '+site
    #    html = urllib2.urlopen(site)  
        html = getUrlRespHtml(site)
        soup = BeautifulSoup(html) 
        #时间        
        dt = soup.find('div',{'class':'live_data_time'}).find('p').string
        dt = dt.split('：')[1]
        #城市数据
        cityAQI = soup.find_all("div",{"class":"value"})        
        file_c.write(city+'\t')
        file_c.write(dt+'\t')
        for ind_aqi in range(len(cityAQI)-1):
            aqi=cityAQI[ind_aqi]
            temp='-'
            if aqi.string!=None:
                file_c.write(aqi.string.split()[0]+'\t')
            else:
                file_c.write(temp+'\t')
        file_c.write('\n')
        #各个站点数据
        trs=soup.find_all('tr')
        for ind_s in range(1,len(trs)):
            file_s.write(city+'\t')
            file_s.write(dt+'\t')
            tr=trs[ind_s]
            siteAQI=tr.find_all('td')
            for aqi in siteAQI:
                temp='-'
                if aqi.string!=None:
                    file_s.write(aqi.string.split()[0]+'\t')
                else:
                    file_s.write(temp+'\t')
            file_s.write('\n')
    file_c.close()
    file_s.close()

if __name__ == '__main__': 
    while True:
        t1=time.time()
        getCurrentHour()
        t2=time.time()
        print '单次下载勇士%s s' % (t2-t1)
        time.sleep(3600-t2+t1)