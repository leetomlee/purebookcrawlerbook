# -*- coding: utf-8 -*-
import json
import random
import time

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from lxml import etree

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
book = mydb["xbiquge"]

user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

import logging  # 引入logging模块

logging.basicConfig(level=logging.INFO)  # 设置日志级别


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


def getScores():
    find = book.find({}, {"_id": 1, "author": 1, "book_name": 1, "rate": 1})
    for f in find:
        try:
            f["rate"]
            continue
        except Exception as e:
            print(e)
        try:
            id = f["_id"]
            author = f["author"]
            name = f["book_name"]
            url = "https://www.qidian.com/search?kw=%s" % name
            html = getHTML(url)
            lis = html.xpath("//*[@id='result-list']/div/ul/li")
            for li in lis:
                bookInfoUrl = "https:" + li.xpath("div/a/@href")[0]
                bookImgUrl = "https:" + li.xpath('div/a/img/@src')[0]
                bookNames = li.xpath("div[2]/h4/a/text()")
                if len(bookNames) == 0:
                    bookNames = li.xpath("div[2]/h4/a/cite/text()")
                    if len(bookNames) == 0:
                        continue
                bookName = bookNames[0]
                bookAuthor = li.xpath("div[2]/p[1]/a[1]/text()")[0]
                bookStatus = li.xpath("div[2]/p/span/text()")[0]
                if str(name).__contains__(bookName) and author == bookAuthor:
                    u = 'https://book.qidian.com/ajax/comment/index?_csrfToken=VyDQJGV3vLqNzMY8pduwEYAAfT1tla9d0A67VoII&bookId=' + str(
                        bookInfoUrl.split('/')[-1]) + '&pageSize=15'
                    res = requests.get(u).text
                    rate = json.loads(res)['data']['rate']
                    if not str(rate).__contains__('.'):
                        rate = float(str(rate) + '.0')
                    f['cover'] = bookImgUrl
                    f['status'] = bookStatus
                    f['rate'] = rate
                    myquery = {"_id": id}
                    newvalues = {"$set": {"cover": bookImgUrl, "status": bookStatus, "rate": rate}}
                    logging.info(name + author + str(rate))
                    book.update_one(myquery, newvalues)
                    time.sleep(3)
                else:
                    continue
        except Exception as e:
            logging.error(e)
            continue


if __name__ == '__main__':
    getScores()
