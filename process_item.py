# -*- coding: utf-8 -*-
import datetime
import time
from concurrent.futures.process import ProcessPoolExecutor

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from requests.adapters import HTTPAdapter

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@127.0.0.1:27017/')
# myclient = pymongo.MongoClient('mongodb://lx:Lx123456@134.175.83.19:27017/')
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]

import logging  # 引入logging模块
ex = ProcessPoolExecutor(max_workers=10)
logging.basicConfig(level=logging.INFO)  # 设置日志级别

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def get_books_from_db():
    find = bookDB.find({"hot": {"$gt": 0}}, {"_id": 1})
    for f in find:
        try:
            for cp in chapterDB.find({"book_id": str(f["_id"])}, {"_id": 1, "content": 1}):
                try:
                    c = cp['content']
                except Exception as e:
                    try:
                        # ex.submit(req, cp)
                        s=req(cp)
                    except Exception as e:
                        logging.error(e)
                    logging.error("load chapter id is:" + str(cp['_id']))
                    continue
        except Exception as e:
            logging.error(e)
    # ex.shutdown(wait=True)


def req(cp):
    s.get("http://127.0.0.1:8080/v1/book/chapter/" + str(cp["_id"]) + "/async", timeout=10)


# ex.shutdown(wait=True)


if __name__ == '__main__':
    stime = datetime.datetime.now()
    logging.info("all update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    get_books_from_db()
    logging.info("end update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    etime = datetime.datetime.now()
    logging.info("used_time  " + str((etime - stime).seconds))
