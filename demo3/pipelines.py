# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import pymongo
from redis import StrictRedis

# class Demo3Pipeline(object):
#     def process_item(self, item, spider):
#         return item

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
# dbparams = dict(
#     host='120.27.244.128',  # 读取settings中的配置
#     db='book',
#     user='root',
#     passwd='lx123456zx',
#     charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
#     cursorclass=pymysql.cursors.DictCursor,
#     use_unicode=False,
# )


        # try:
        #     if isinstance(item, Book):
        #         book.update_one({"_id": item["_id"]}, {"$set": dict(item)}, upsert=True)
        #     else:
        #         chapter.insert_one(dict(item))
        # except Exception as e:
        #     pass
        # return item
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
