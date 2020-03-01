# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import random

import pymongo
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

# class MeiZiPipeline(ImagesPipeline):
#     pass
# class PiaoHuaPipeline(object):
#     client=MongoClient('120.27.244.128',27017)
#     db = client.pythondb
#     posts = db.posts
#     its=item
#     posts.insert(item)
#
#     pass
from demo3.items import Book

# dbparams = dict(
#     host='120.27.244.128',  # 读取settings中的配置
#     db='book',
#     user='root',
#     passwd='lx123456zx',
#     charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
#     cursorclass=pymysql.cursors.DictCursor,
#     use_unicode=False,
# )


# class Demo3Pipeline(object):
#     def process_item(self, item, spider):
#         return item
uri = 'mongodb://admin:lx123456zx@120.27.244.128:27017/admin'

client = pymongo.MongoClient(host='120.27.244.128')
db = client['book']
book = db['book']
chapter = db['chapter']


class CrawlerScrapyPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, Book):
            book.update_one({"_id":item["_id"]}, {"$set": dict(item)}, upsert=True)
        else:
            chapter.insert(dict(item))
        return item
        # 写入数据库中

    # def getids(self):
    #     return self.dbpool.runInteraction(self.get_chapterids)

    # def get_chapterids(self, tx):
    #     sql = "select chapter_id from chapter"
    #     return tx.execute(sql, ())

    # def insert_chapter(self, tx, item):
    #     sql = "insert into chapter(chapter_id,book_id,chapter_name,content) values (%s,%s,%s,%s)"
    #     params = (item['chapter_id'], item['book_id'], item['chapter_name'], item['content'])
    #     tx.execute(sql, params)

    # def insert_book(self, tx, item):
    #     tt = tx._connection._connection
    #     try:
    #         tt.ping()
    #     except Exception as e:
    #         self.dbpool.close()
    #         self.dbpool =adbapi.ConnectionPool('pymysql', **dbparams)
    #
    #     # print item['name']
    #     sql = "insert into book(id,book_name,book_desc,author,category,cover,hot,last_chapter,last_chapter_id,status,u_time,link) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update u_time=%s"
    #     params = (
    #         item["id"], item["book_name"], item["book_desc"], item["author"], item["category"], item["cover"],
    #         item["hot"],
    #         item["last_chapter"], item['last_chapter_id'], item["status"], item["u_time"], item['link'], item["u_time"])
    #     tx.execute(sql, params)

    # 错误处理方法
    # def _handle_error(self, failue, item, spider):
    #     print(failue, item)
    #
    # @classmethod
    # def from_settings(cls, settings):
    #     '''1、@classmethod声明一个类方法，而对于平常我们见到的则叫做实例方法。
    #        2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
    #        3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
    #     dbpool = adbapi.ConnectionPool('pymysql', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
    #     return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    #
    #
    # project_dir = os.path.abspath(os.path.dirname(__file__))
    # IMAGES_STORE = os.path.join(project_dir, "books")
    #
    #
    # class BookPipeline(object):
    #     def process_item(self, item, spider):
    #         with open(IMAGES_STORE + "/" + item["title"] + ".txt", "w", encoding='utf-8') as f:
    #             f.write(item["content"])
    #
    #


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            print(ua)
            request.headers.setdefault('User-Agent', ua)

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
