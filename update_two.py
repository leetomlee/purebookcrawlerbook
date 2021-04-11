# -*- coding: utf-8 -*-
import datetime
import random
import time
from concurrent.futures import ThreadPoolExecutor

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from bson import ObjectId
from lxml import etree

ex = ThreadPoolExecutor()
# ex = ProcessPoolExecutor()
myclient1 = pymongo.MongoClient('mongodb://lx:Lx123456@localhost:27017/')
# myclient1 = pymongo.MongoClient('mongodb://lx:Lx123456@134.175.83.19:27017/', connect=False)
mydbDB = myclient1["book"]
bookDB = mydbDB["books"]
chapterDB = mydbDB["chapters"]
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
    retry_count = 5
    while retry_count > 0:
        try:
            # proxy = requests.get("http://134.175.83.19:5010/get/").json().get("proxy")
            proxy = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
            logging.info("get proxy is:" + proxy)
            get = requests.get(url, proxies={"http": "http://{}".format(proxy)},
                               headers={"User-Agent": random.choice(user_agent_list)}, timeout=5)
            get.encoding = "utf-8"
            status = get.status_code
            if status != 200:
                raise Exception("request resource failed")
            html = etree.HTML(get.text)
            logging.info("request ok")
            return html
        except Exception as e:
            logging.error(e)
            logging.info("retry " + str(retry_count))
            retry_count -= 1
            # requests.get("http://134.175.83.19:5010/delete/?proxy={}".format(proxy))
            requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
            logging.error("delete proxy is:" + proxy)
    return None


def get_books_from_db():
    find = bookDB.find({"hot": {"$gt": 0}, "status": {"$ne": "完结"}}, {"_id": 1, "link": 1})
    cnt = 1
    for f in find:
        try:
            # result = updateBook(str(f["_id"]), f["link"])
            # logging.info(result)
            ex.submit(updateBook, str(f["_id"]), f["link"])
        except Exception as e:
            logging.error(e)
            continue
        cnt += 1
    ex.shutdown(wait=True)
    logging.info("update %s books" % str(cnt))


def updateBook(id, url):
    logging.info("start update  " + url)
    html = getHTML(url)
    if html is None:
        return "empty html"

    ids = []
    chps = chapterDB.find({"book_id": id}, {"chapter_name": 1})
    for chp in chps:
        ids.append(chp["chapter_name"])
    chapters = []
    # if str(url).__contains__("266ks"):
    #     for dd in html.xpath('/html/body/div[3]/div[2]/div/div[1]/ul//li'):
    #         if len(dd.xpath('a/@href')) > 0:
    #             name = dd.xpath('a/text()')[0]
    #             s = dd.xpath('a/@href')[0]
    #             if ids.__contains__(name):
    #                 flag = False
    #                 continue
    #             chapter = {
    #                 'book_id': id,
    #                 'link': 'https://www.266ks.com' + s,
    #                 'chapter_name': name}
    #
    #             chapters.append(chapter)
    #     chapters.reverse()
    #     if flag:
    #         logging.info("非最新更新")
    #         chapters = []
    #         for option in html.xpath('/html/body/div[3]/div[2]/div/div[3]/span[2]/select/option'):
    #             chapters_url = "https://www.266ks.com" + option.xpath('@value')[0]
    #             ks = get_chapters_266ks(chapters_url, ids, id)
    #             time.sleep(3)
    #             if len(ks) > 0:
    #                 chapters = chapters + ks
    if str(url).__contains__("dwxdwx"):
        for dd in html.xpath('//*[@id="list"]/dl/dt[2]/following-sibling::*'):
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href')[0]
                name = dd.xpath('a/text()')[0]
                if ids.__contains__(name):
                    continue
                chapter = {
                    'book_id': id,
                    'link': 'https://www.dwxdwx.net' + s,
                    'chapter_name': name}
                chapters.append(chapter)

    else:
        for dd in html.xpath("//*[@id='list']/dl/dd"):
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href')[0]
                name = dd.xpath('a/text()')[0]
                if ids.__contains__(name):
                    continue
                chapter = {
                    'book_id': id,
                    'link': 'http://www.paoshuzw.com/' + s,
                    'chapter_name': name}
                chapters.append(chapter)
    logging.info("parse chapters ok")
    try:
        if len(chapters) != 0:
            many = chapterDB.insert_many(chapters)

            for x in many.inserted_ids:
                try:
                    pass
                    # requests.get("http://localhost:8080/v1/book/chapter/" + str(x) + "async")
                except Exception as e:
                    logging.error(e)
            logging.info("new add  " + str(len(many.inserted_ids)))
            logging.info("insert ok")
            if str(url).__contains__("266ks"):
                update_time = html.xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div/p[5]/text()')[0]
                latest_chapter_name = html.xpath('/html/body/div[3]/div[2]/div/div[1]/ul/li[1]/a/text()')[0]
            else:
                update_time = html.xpath('//*[@id="info"]/p[3]/text()')[0]
                latest_chapter_name = html.xpath('//*[@id="info"]/p[4]/a/text()')[0]

            myquery = {"_id": ObjectId(id)}
            newvalues = {
                "$set": {"u_time": update_time, "last_chapter": latest_chapter_name}}

            bookDB.update_one(myquery, newvalues)
            logging.info("book info update " + str(id))
    except Exception as e:
        logging.error(e)
    return "ok"


def get_chapters_266ks(url, ids, id):
    html = getHTML(url)
    temp = []
    for dd in html.xpath('/html/body/div[3]/div[2]/div/div[2]/ul//li'):
        if len(dd.xpath('a/@href')) > 0:
            name = dd.xpath('a/text()')[0]
            s = dd.xpath('a/@href')[0]
            if ids.__contains__(name):
                continue
            chapter = {
                'book_id': id,
                'link': 'https://www.266ks.com' + s,
                'chapter_name': name}
            temp.append(chapter)
    return temp


if __name__ == '__main__':
    stime = datetime.datetime.now()
    logging.info("all update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    get_books_from_db()
    logging.info("end update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    etime = datetime.datetime.now()
    logging.info("used_time  " + str((etime - stime).seconds))
    myclient1.close()