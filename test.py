# -*- coding: utf-8 -*-
import random
import time
from concurrent.futures.process import ProcessPoolExecutor

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from bson import ObjectId
from elasticsearch import Elasticsearch
from lxml import etree
from redis import StrictRedis

ex = ProcessPoolExecutor()
# myclient = pymongo.MongoClient('mongodb://lx:Lx123456@localhost:27017/', connect=False)
redis = StrictRedis(host='23.91.100.230', port=6379, db=1, password='zx222lx')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@23.91.100.230:27017/', connect=False)
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]
accountDB = mydb["account"]
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
    get.encoding = "iso-8859"
    html = etree.HTML(get.text)
    return html


def get_books_from_db():
    find = book.find({"hot": {"$gt": 0}, "status": {"$ne": "完结"}}, {"_id": 1, "link": 1})
    for f in find:
        try:
            updateBook(str(f["_id"]), f["link"])
            # ex.submit(updateBook, str(f["_id"]), f["link"] )
        except Exception as e:
            logging.error(e)
            continue
    # ex.shutdown(wait=True)


def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False


def get_chapters(url, bookId):
    html = getHTML(url)
    chapters = []
    for li in html.xpath('//ul[@class="inner"]//li'):
        link = li.xpath('a/@href')[0]
        name = li.xpath('a/text()')[0]
        print(link + name)
        html1 = getHTML(link)
        content = ''

        for p in html1.xpath('//*[@id="BookText"]//p'):
            text = ''.join(p.xpath('span/text()'))
            if is_chinese(str(text)):
                content += "\t\t\t\t\t\t\t\t" + text + "\n"
        print(content)
        chapter = {
            'book_id': bookId,
            'link': link,
            'content': content,
            'chapter_name': name}
        chapters.append(chapter)
    chapterDB.insert_many(chapters)


def get_books():
    html1 = getHTML('http://www.yuedu88.com/longzu/')
    for book in html1.xpath('//div[@class="item-img"]'):
        cover = book.xpath('a/img/@src')[0]
        link = book.xpath('a/@href')[0]
        name = book.xpath('h2/a/text()')[0]
        author = book.xpath('text()')[1]
        desc = book.xpath('p/text()')[0]
        book_id = str(bookDB.insert_one({
            "link": link,
            "author": author,
            "book_name": name,
            "hot": 0,
            'cover': cover,
            'category': "玄幻奇幻",
            "status": "完结",
            "book_desc": desc
        }).inserted_id)
        print(book_id)
        get_chapters(link, book_id)


def updateBook(id, url):
    logging.info("start update  " + url)
    html = getHTML(url)
    ids = []
    chps = chapterDB.find({"book_id": id}, {"chapter_name": 1})
    for chp in chps:
        ids.append(chp["chapter_name"])
    chapters = []
    if str(url).__contains__("266ks"):
        flag = True
        for dd in html.xpath('/html/body/div[3]/div[2]/div/div[1]/ul//li'):
            if len(dd.xpath('a/@href')) > 0:
                name = dd.xpath('a/text()')[0]
                s = dd.xpath('a/@href')[0]
                if ids.__contains__(name):
                    flag = False
                    continue
                chapter = {
                    'book_id': id,
                    'link': 'https://www.266ks.com' + s,
                    'chapter_name': name}

                chapters.append(chapter)
        chapters.reverse()
        if flag:
            logging.info("非最新更新")
            chapters = []
            for option in html.xpath('/html/body/div[3]/div[2]/div/div[3]/span[2]/select/option'):
                chapters_url = "https://www.266ks.com" + option.xpath('@value')[0]
                ks = get_chapters_266ks(chapters_url, ids, id)
                time.sleep(3)
                if len(ks) > 0:
                    chapters = chapters + ks




    else:
        for dd in html.xpath("//*[@id='list']/dl/dd"):
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href')[0]
                name = dd.xpath('a/text()')[0]
                if ids.__contains__(name):
                    continue
                chapter = {
                    'book_id': id,
                    'link': 'http://www.xbiquge.la' + s,
                    'chapter_name': name}
                chapters.append(chapter)

    try:
        if len(chapters) != 0:
            many = chapterDB.insert_many(chapters)
            for x in many.inserted_ids:
                try:
                    requests.get("http://23.91.100.230:8081/v1/book/chapter/" + str(x))
                except Exception as e:
                    logging.error(e)
            logging.info("new add  " + str(len(many.inserted_ids)))
            update_time = ""
            latest_chapter_name = ""
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


es = Elasticsearch(
    ['23.91.100.230:8088'],
    # 认证信息
    http_auth=('elastic', 'jXqw0zF3XPOxu8PThv8H')
)


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def getHTMLzz(param):
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            requests.get(param, proxies={"http": "http://{}".format(proxy)})
            logging.info('get link ' + param)
        except Exception as e:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    return None
import datetime
import time
from concurrent.futures.process import ProcessPoolExecutor

import pymongo

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
chapterDB = mydb["chapters"]
myclient1 = pymongo.MongoClient('mongodb://lx:Lx123456@localhost:27017/')
mydb1 = myclient1["book"]

bookDB1 = mydb1["books"]
chapterDB1 = mydb1["chapters"]

import logging  # 引入logging模块

logging.basicConfig(level=logging.INFO)  # 设置日志级别
ex = ProcessPoolExecutor()


def get_books_from_db():
    find = bookDB1.find({}, {"_id": 1, "book_name": 1}, no_cursor_timeout=True)
    for f in find:
        try:
            ex.submit(updateBook, str(f["_id"]), )
            logging.error("插入" + f["book_name"])
        except Exception as e:
            logging.error(e)
            continue
    ex.shutdown(wait=True)


def updateBook(id):
    chapters = []
    chps = chapterDB.find({"book_id": id}, {"content": 0}, no_cursor_timeout=True)
    for chp in chps:
        chapters.append({
            "_id": chp["_id"],
            "book_id": chp["book_id"],
            "link": chp["link"],
            "chapter_name": chp["chapter_name"]
        })

    try:
        if len(chapters) != 0:
            chapterDB1.insert_many(chapters)

    except Exception as e:
        logging.error(e)





if __name__ == '__main__':
    book_ids = []
    for id in bookDB.find({"hot": {"$gt": 1}}, {"_id": 1}):
        book_ids.append(id['_id'])
    for book_id in book_ids:
        for cid in chapterDB.find({"book_id": str(book_id)}, {"_id": 1}):
            idx = cid["_id"]


    # idss = set()
    # acts = accountDB.find({}, {"ids": 1, "_id": 1, 'last_alive_date': 1, 'name': 1})
    # for act in acts:
    #     try:
    #         ids = act['ids']
    #         for id in ids:
    #             idss.add(id)
    #         # ids = act['last_alive_date']
    #
    #     except Exception as e:
    #         print(act['_id'] + act['name'])
    #
    #         # accountDB.delete_one({"_id":act['_id']})
    # for id in idss:
    #     for cid in chapterDB.find({'book_id': id}, {'_id': 1}):
    #         s = str(cid['_id'])
    #         getHTMLzz('http://23.91.100.230:8081/v1/book/chapter/' + s)
    # cs=[]
    # for c in chapterDB.find({"book_id":"5f8c12ba4e530000ad0023c2"}):
    #     cs.append(str(c['_id']))
    # for i in reversed(cs):
    #     requests.get('http://localhost:8081/v1/book/chapter/'+i)
    #     time.sleep(5)

    # ones = bookDB.find({“”}, {"_id": 1, "book_name": 1, "author": 1})
    # for one in ones:
    #     book_id = ''
    #     book_name = ''
    #     book_author = ''
    #     try:
    #         book_id = one['_id']
    #     except Exception as e:
    #         pass
    #     try:
    #         book_name = one['book_name']
    #
    #     except Exception as e:
    #         pass
    #     try:
    #         book_author = one['author']
    #
    #     except Exception as e:
    #         pass
    #     print(book_id, book_name, book_author)
    # index = es.index(index="book", doc_type="book", id="5f8c12ba4e530000ad0023c2",
    #                  body={"book_name": "大梦主", "book_author": "忘语"})
    # print(index)
# es.indices.create(index='book')

# get_books()
# chapterDB.update_many({}, {"$set": {"content": ""}})
# stime = datetime.datetime.now()
# logging.info("all update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# get_books_from_db()
# logging.info("end update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# etime = datetime.datetime.now()
# logging.info("used_time  " + str((etime - stime).seconds))
