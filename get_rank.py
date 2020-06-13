# -*- coding: utf-8 -*-
import random

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from lxml import etree

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
book = mydb["xbiquge"]
rank = mydb["rank"]

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
maleUlr = "https://www.qidian.com/finish?action=hidden&orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=2&page="
feMaleUlr = "https://www.qidian.com/mm/all?orderId=&style=1&pageSize=20&siteid=0&pubflag=0&hiddenField=0&page="

maleRank = {}
feMaleRank = {}


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


def get_feMale_rank():
    lis = getHTML("https://www.qidian.com/mm/rank").xpath("/html/body/div[1]/div[4]/div[1]/ul[2]/li")
    for li in lis:
        url = "https:" + li.xpath("a/@href")[0]
        text = li.xpath("a/text()")[0]
        ids = []

        for i in range(1, 2):
            u = url[:-1] + "2&page=%s" % i
            trs = getHTML(u).xpath("//*[@id='rank-view-list']/div/table/tbody/tr")

            if len(lis) == 0:
                break
            for li in trs:
                try:
                    if u.__contains__("readIndex"):
                        book_name = li.xpath("td[2]/a/text()")[0]
                        author = li.xpath("td[5]/a/text()")[0]
                    else:
                        book_name = li.xpath("td[3]/a/text()")[0]
                        author = li.xpath("td[6]/a/text()")[0]
                    find = book.find_one({"book_name": book_name, "author": author}, {"_id": 1, "cover": 1})
                    ids.append({"id": find["_id"], "cover": find["cover"], "name": book_name})
                except Exception as e:
                    logging.error("link " + u + " 数据库中不存在 " + author + " 写的 " + book_name)
        feMaleRank[text] = ids
    feMaleRank["type"] = 2
    rank.insert_one(feMaleRank)


def get_male_rank():
    lis = getHTML("https://www.qidian.com/rank").xpath("/html/body/div[1]/div[5]/div[1]/ul[2]/li")
    for li in lis:
        url = "https:" + li.xpath("a/@href")[0]
        text = li.xpath("a/text()")[0]
        ids = []
        for i in range(1, 3):
            u = url[:-1] + "2&page=%s" % i
            trs = getHTML(u).xpath("//*[@id='rank-view-list']/div/table/tbody/tr")
        if len(lis) == 0:
            break
        for li in trs:
            try:
                if u.__contains__("readIndex"):
                    book_name = li.xpath("td[2]/a/text()")[0]
                    author = li.xpath("td[5]/a/text()")[0]
                else:
                    book_name = li.xpath("td[3]/a/text()")[0]
                    author = li.xpath("td[6]/a/text()")[0]
                find = book.find_one({"book_name": book_name, "author": author}, {"_id": 1, "cover": 1})
                ids.append({"id": find["_id"], "cover": find["cover"], "name": book_name})
            except Exception as e:
                logging.error(u + "  数据库中不存在 " + author + " 写的 " + book_name)
        maleRank[text] = ids
    maleRank["type"] = 1
    rank.insert_one(maleRank)


if __name__ == '__main__':
    rank.drop()
    get_feMale_rank()
    get_male_rank()
