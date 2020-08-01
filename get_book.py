# -*- coding: utf-8 -*-
import random
from concurrent.futures.process import ProcessPoolExecutor

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from lxml import etree
from redis import StrictRedis

ex = ProcessPoolExecutor()
redis = StrictRedis(host='120.27.244.128', port=6379, db=0, password='zx222lx')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["bks"]
accountDB = mydb["account"]
chapterDB = mydb["cps"]
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


def get_bks(url):
    id = "xbiqugela642"
    selector = getHTML(url)
    book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content")[0]
    author = selector.xpath("//meta[@property='og:novel:author']/@content")[0]
    cover = selector.xpath("//meta[@property='og:image']/@content")[0]
    category = selector.xpath("//meta[@property='og:novel:category']/@content")[0]
    # update_time = selector.xpath("//meta[@property='og:novel:update_time']/@content")[0]
    # status = selector.xpath("//meta[@property='og:novel:status']/@content")[0]

    book_desc = selector.xpath("//meta[@property='og:description']/@content")[0]
    latest_chapter_name = selector.xpath(
        '//*[@id="info"]/p[4]/a/text()')[0]

    book = {"link": url,
            "_id": id,
            "cover": cover,
            "hot": 0,
            'book_name': str(book_name).strip(),
            'author': str(author).strip(),
            'category': category,
            'status': "完本",
            'book_desc': book_desc,
            # "u_time": update_time,
            "type": 2,
            'last_chapter': latest_chapter_name}
    bookDB.insert_one(dict(book))
    chapters = []

    for dd in selector.xpath("//*[@id='list']/dl/dd"):
        if len(dd.xpath('a/@href')) > 0:
            name = dd.xpath('a/text()')[0]
            s = dd.xpath('a/@href')[0]
            chapter = {
                'book_id': id,
                'link': 'http://www.xbiquge.la' + s,
                'chapter_name': name}
            chapters.append(chapter)
    if len(chapters) > 0:
        chapterDB.insert_many(chapters)


if __name__ == '__main__':
    get_bks("http://www.xbiquge.la/0/642/")
    # chapterDB.delete_many({"book_id":"xbiqugela642"})