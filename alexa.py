#!/usr/bin/env python
#coding:utf-8
import time
import socket
import traceback
import threading
import multiprocessing
import requests
from bs4 import BeautifulSoup
import gevent
from gevent import monkey
monkey.patch_socket()


class Site(object):
    """
        To test the advantage of the gevent compared to multithreading,
    I crawled the http://www.alexa.com/topsites/global and resovle the
    domain names contains in the page.
    """
    def __init__(self):
        #"http://www.alexa.com/topsites/global;[0-19]"
        self.baseURL   = "http://www.alexa.com/topsites/global;"
        self.timeout   = 5 #seconds
        self.totalPage = 20 #0-19
        self.domain    = []
        self.ipaddr    = []
    def getURList(self, page):
        """Get all the domains of the page"""
        urList  = []
        req = requests.get(self.baseURL+str(page))
        #req = requests.get(self.baseURL+str(page), proxies={"http": "socks5://127.0.0.1:1080"})
        soup = BeautifulSoup(req.text, "lxml")
        lst = soup.find_all(class_="site-listing")
        for l in lst:
            self.domain.append(l.find("a").string)

    def resolve(self, domain):
        """
        socket.getaddrinfo(host, port[, family[, socktype[, proto[, flags]]]])
        Just return the Ipv4 TCP info.
        """
        try:
            ret = socket.getaddrinfo(domain, 80, 2, 1, 6)
            ip  = ret[0][4][0]
            self.ipaddr.append(ip)
        except Exception, e:
            print traceback.format_exc(e)


def common():
    start = time.time()
    site = Site()
    for page in xrange(site.totalPage):
        site.getURList(page)
    end = time.time()
    print "***" * 10 + "common" + "***" * 10
    print "Total domains: {0}".format(len(site.domain))
    print "Total used %0.2f seconds." % (end - start)

def multithread():
    start = time.time()
    site = Site()
    threads = []
    for page in xrange(site.totalPage):
        t = threading.Thread(target=site.getURList, args=(page,))
        t.start()
        threads.append(t)
        print "page: {0} was added".format(page)
    for thread in threads:
        thread.join()
    end = time.time()
    print "***" * 10 + "multithreading" + "***" * 10
    print "Total domains: {0}".format(len(site.domain))
    print "Total used %0.2f seconds." % (end - start)

def multiprocess():
    start = time.time()
    site  = Site()
    pool  = multiprocessing.Pool(processes=4)
    #pool.map_async(site.getURList, xrange(site.totalPage))
    pool.map_async(t(x), range(site.totalPage))
    pool.close()
    pool.join()
    end = time.time()
    print "***" * 10 + "multiprocessing" + "***" * 10
    print "Total domains: {0}".format(len(site.domain))
    print "Total used %0.2f seconds." % (end - start)

def gevt():
    start = time.time()
    site  = Site()
    threads = []
    for page in xrange(site.totalPage):
        threads.append(gevent.spawn(site.getURList, page))
    gevent.joinall(threads)
    end = time.time()
    print "***" * 10 + "gevent" + "***" * 10
    print "Total domains: {0}".format(len(site.domain))
    print "Total used %0.2f seconds." % (end - start)


if __name__ == "__main__":
    def t(x):
        return x
    #common()
    multithread()
    #multiprocess()
    gevt()
