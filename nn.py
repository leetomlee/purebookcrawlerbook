import time

import pymongo
import logging  # 引入logging模块

import requests
from loguru import logger

logging.basicConfig(level=logging.INFO)  # 设置日志级别
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@23.91.100.230:27017/', connect=False)
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]
if __name__ == '__main__':
    book_ids = []
    logger.info("开始定时爬取章节数据")
    for id in bookDB.find({"hot": {"$gt": 1}}, {"_id": 1}):
        book_ids.append(id['_id'])
    for book_id in book_ids:
        for cid in chapterDB.find({"book_id": str(book_id)}, {"_id": 1}):
            idx = cid["_id"]
            requests.get("http://localhost:8081/v1/book/chapter/" + str(idx))
            time.sleep(2)
    logger.info("定时爬取章节数据完成")
