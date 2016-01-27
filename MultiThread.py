# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 14:28:14 2016

@author: lixiang
"""

import urllib2
import socket
import time
from bs4 import BeautifulSoup    #besutifulsoup的第三版  
import threading
from Queue import Queue
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

sleep_time=60
socket.setdefaulttimeout(60) # 60 秒钟后超时
#q是任务队列    
q = Queue()
lock = threading.Lock()
requireCount=0
numT=5

class AQISpider:
    def __init__(self):
        self.cities=self.getCities()
        self.file_c = open('city.txt','a')
        self.file_s = open('site.txt','a')
        
    def getUrlRespHtml(self,url):
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
        try:
            respHtml = opener.open(req).read()
        except urllib2.HTTPError, e:
            print e.code
        return respHtml
    
    def getCities(self):
        site='http://pm25.in'
        html = self.getUrlRespHtml(site)
        soup = BeautifulSoup(html) 
        hrefs = soup.find("div",{"class":"all"}).find_all('a')
        cs=[]
        for href in hrefs:
            c=href['href']
            c=c[1:len(c)]
            cs.append(c)
#        cs=cs[0:10]
        return list(set(cs))
        
    def getCurrentHour(self):
        print 'city count is：'+str(len(self.cities))
        multi=MultiThread(numT,len(self.cities))
        multi._do(self.working)
        self.file_c.close()
        self.file_s.close()
        print u'数据下载完毕'
    
    def working(self):
        while True:
            arguments = q.get()
            self.do_somthing_using(arguments)
            q.task_done() 
            
    def do_somthing_using(self,ind):
        city=self.cities[ind]
        site ='http://pm25.in/' + city + '.html'  
        print str(ind)+' '+site
    #    html = urllib2.urlopen(site)  
        html = self.getUrlRespHtml(site)
        soup = BeautifulSoup(html) 
        #时间        
        dt = soup.find('div',{'class':'live_data_time'}).find('p').string
        dt = dt.split('：')[1]
        #城市数据
        cityAQI = soup.find_all("div",{"class":"value"})        
        data_c=[city,dt]
        for ind_aqi in range(len(cityAQI)-1):
            aqi=cityAQI[ind_aqi]
            if aqi.string!=None:
                data_c.append(aqi.string.split()[0])
            else:
                data_c.append('-')
        #各个站点数据
        trs=soup.find_all('tr')
        for ind_s in range(1,len(trs)):
            tr=trs[ind_s]
            siteAQI=tr.find_all('td')
            data_s=[city,dt]
            for aqi in siteAQI:
                if aqi.string!=None:
                    data_s.append(aqi.string.split()[0])
                else:
                    data_s.append('-')
        self._save(self.file_c,data_c)
        self._save(self.file_s,data_s)
        self.file_c.flush()
        self.file_s.flush()
        ##################
        #####没执行5次进入休眠
        ###################
        global requireCount   
        if lock.acquire():
            requireCount+=1
            print 'requireCount---'+str(requireCount)
            if requireCount%50==0:
                print 'sleep %s s' % sleep_time
                time.sleep(sleep_time)
            lock.release()
            
    def _save(self, file ,data):
        file.write(str(data)+'\n')
        
class MultiThread:
    def __init__(self,NUM,JOBS):
        #NUM是并发线程总数
        #JOBS是有多少任务
        self.NUM = NUM
        self.JOBS =JOBS
    def _do(self,working):
        #fork NUM个线程等待队列
        for i in range(self.NUM):
            t = threading.Thread(target=working)
            t.setDaemon(True)
            t.start()
        #把JOBS排入队列
        for i in range(self.JOBS):
            q.put(i)
        #等待所有JOBS完成
        q.join()    
            
if __name__ == '__main__': 
    while True:
        t1=time.time()
        spider = AQISpider()
        spider.getCurrentHour()
        t2=time.time()
        print '单次下载用时%s s' % (t2-t1)
        time.sleep(3600-t2+t1)
