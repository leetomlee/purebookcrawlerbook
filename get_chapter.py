import logging  # 引入logging模块
from concurrent.futures._base import as_completed
from concurrent.futures.process import ProcessPoolExecutor
import pymongo
import requests
from loguru import logger
ex = ProcessPoolExecutor()
logging.basicConfig(level=logging.INFO)  # 设置日志级别
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@localhost:27017/', connect=False)
# myclient = pymongo.MongoClient('mongodb://lx:Lx123456@23.91.100.230:27017/', connect=False)

mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]


def get_chapters_by_book_id(book_id):
    for cid in chapterDB.find({"book_id": book_id}, {"_id": 1, "content": 1}):
        flag = False
        try:
            if cid['content'] == '':
                flag = True
        except Exception as e:
            logger.error(e)
            flag = True

        try:
            if flag:
                idx = cid["_id"]
                requests.get("http://localhost:8083/v1/book/chapter/" + str(idx))
                # requests.get("http://23.91.100.230:8081/v1/book/chapter/" + str(idx))
                logger.info('爬取章节' + str(idx) + "success")
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    logger.info("开始定时爬取章节数据")
    book_ids=[]
    for id in bookDB.find({"hot": {"$gt": 1}}, {"_id": 1, "book_name": 1}):
        logger.info("开始爬取" + id['book_name'])
        book_ids.append(str(id["_id"]))
        # ex.submit(get_chapters_by_book_id, str(id["_id"]))
    # ex.shutdown(wait=True)
    all_task = [ex.submit(get_chapters_by_book_id, book_id) for book_id in book_ids]
    for future in as_completed(all_task):
        data = future.result()
    print("in main: get page {}s success".format(data))
    logger.info("定时爬取章节数据完成")
