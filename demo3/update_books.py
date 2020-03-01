# -*- coding: utf-8 -*-
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor

import records
import requests
from lxml import etree
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s', datefmt='%Y-%m-%d')

address = '120.27.244.128'

site = 'https://www.biquge.com.cn'
domains = 'biquge.com.cn'
conn = MongoClient(address, 27017)
dd = conn.book
my_set = dd.chapters
db = records.Database("mysql+pymysql://root:lx123456zx@" + address + "/book?charset=utf8")
executor = ThreadPoolExecutor()


def getAllBooksDB():
    futures=[]
    query = db.query("select * from book")
    query_all = query.all()
    logging.info("库中书籍合计" + str(len(query)))
    for i in query_all:
        logging.info("开始更新" + i['book_name'])
        submit = executor.submit(syncBook, i['link'], i['id'], i['book_name'])
        futures.append(submit)
    executor.shutdown(True)
    
        # syncBook(i['link'],i['id'],i['book_name'])

def syncBook(link, id, n):
    text = requests.get(link).text
    html = etree.HTML(text)
    query = db.query("select chapter_id from chapter where book_id=:id", **{'id': id})
    ids = []
    for f in query.as_dict():
        ids.append(f['chapter_id'])
    chapters = []
    for dd in html.xpath("//*[@id='list']/dl/dd"):
        url = site + dd.xpath('a/@href')[0]
        name = dd.xpath('a/text()')[0]
        chapterId = url.split('/')[5].split('.')[0]
        if not ids.__contains__(chapterId):
            get = requests.get(url)
            h = etree.HTML(get.text)
            content = ''.join(h.xpath('//*[@id="content"]/text()'))
            try:
                my_set.insert_one({"content": content, "_id": chapterId})
            except Exception as e:
                logging.info(e)
            chapters.append({"chapter_id": chapterId, "chapter_name": name, "book_id": id})

    ids = []
    db.bulk_query("insert into chapter(book_id,chapter_id,chapter_name) values (:book_id,:chapter_id,:chapter_name)",
                  chapters)


    logging.info('更新' + n + '完成')

if __name__ == '__main__':
    while True:
        logging.info('开始更新数据库,每2小时一次')
        getAllBooksDB()
        logging.info('更新数据库完成')
        time.sleep(60 * 60 * 2)
