# -*- coding: utf-8 -*-
import datetime
import time

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from requests.adapters import HTTPAdapter

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@134.175.83.19:27017/')
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]

import logging  # 引入logging模块

logging.basicConfig(level=logging.INFO)  # 设置日志级别

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def get_books_from_db():
    sort = [('hot', 1)]
    # find = book.find({}, {"_id": 1}).sort(sort)
    # find = book.find({"hot": 0}, {"_id": 1, "hot": 1, "link": 1})
    # find = book.find({}, {"_id": 1, "link": 1})
    find = bookDB.find({"hot": {"$gt": 0}}, {"_id": 1})
    # find = book.find({"hot": {"$gt": 0}}, {"_id": 1, "link": 1})
    for f in find:
        # print(f['_id'])
        try:
            for cp in chapterDB.find({"book_id": str(f["_id"])}, {"_id": 1, "content": 1}):
                #     print(f["status"])
                # chapterDB.delete_many({"book_id": f["_id"]})
                try:
                    c = cp['content']

                except Exception as e:
                    try:
                        req(cp)
                    except Exception as e:
                        logging.error(e)
                    logging.error("load chapter id is:" + str(cp['_id']))
                    continue
        except Exception as e:
            logging.error(e)
    # ex.submit(updateBook, f["_id"], f["link"])


def req(cp):
    s.get("http://127.0.0.1:8080/v1/book/chapter/" + str(cp["_id"]) + "/async", timeout=30)


# ex.shutdown(wait=True)


if __name__ == '__main__':
    # get_books_from_db()
    stime = datetime.datetime.now()
    logging.info("all update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    get_books_from_db()
    logging.info("end update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    etime = datetime.datetime.now()
    logging.info("used_time  " + str((etime - stime).seconds))
