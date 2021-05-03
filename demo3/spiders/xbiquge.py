# -*- coding: utf-8 -*-

import pymongo
from elasticsearch import Elasticsearch
from redis import StrictRedis
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, CommonItemLoader

site = 'http://www.xbiquge.la'
domains = 'www.xbiquge.la'
s = 0
# client = MongoClient('mongodb://lx:Lx520zx@120.27.244.128:27017/admin')
# client = pymongo.MongoClient(host='120.27.244.128', port=27017, username='lx', password='Lx520zx', authSource='admin')
# client = MongoClient(host='120.27.244.128', port=27017)
# db = client.admin
#
# db.authenticate('lx', 'Lx123456')
#myclient = pymongo.MongoClient('mongodb://lx:Lx123456@localhost:27017/', connect=False)
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@23.91.100.230:27017/')
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]
es = Elasticsearch(
     ['23.91.100.230:8088'],
     # 认证信息
     http_auth=('elastic', 'jXqw0zF3XPOxu8PThv8H')
 )
#es = Elasticsearch(
#    ['localhost:8088'],
# 
#    http_auth=('elastic', 'Z2jJ2sZWGPy0bulSf4dZ')
#)
redis = StrictRedis(host='23.91.100.230', port=6379, db=1, password='zx222lx')
#redis = StrictRedis(host='localhost', port=6379, db=1, password='zx222lx')


class MeiziSpider(CrawlSpider):
    name = 'xbiquge'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/\d+/\d+/$', ),
             callback='parse_mm', follow=True, ),
        Rule(LinkExtractor(allow=r'/.*?/$', ),
             follow=True, ),
        Rule(LinkExtractor(allow=r'/.*?/\d+_\d+.html$', ),
             follow=True, ),
    )

    def parse_mm(self, response):

        selector = Selector(response=response)
        book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content").extract_first()
        author = selector.xpath("//meta[@property='og:novel:author']/@content").extract_first()
        key = book_name + author
        if redis.exists(key):
            return
            # one = bookDB.find_one({'book_name': book_name, 'author': author})
            # bookDB.delete_one({'book_name': book_name, 'author': author})
            # book_id = str(one['_id'])
            # chapterDB.delete_many({'book_id': book_id})

        redis.set(key, '')
        cover = selector.xpath("//meta[@property='og:image']/@content").extract_first()
        category = selector.xpath("//meta[@property='og:novel:category']/@content").extract_first()
        status = selector.xpath("//meta[@property='og:novel:status']/@content").extract_first()
        update_time = selector.xpath('//*[@id="info"]/p[3]/text()').extract_first()
        latest_chapter_name = selector.xpath(
            '//*[@id="info"]/p[4]/a/text()').extract_first()
        book_desc = selector.xpath("//meta[@property='og:description']/@content").extract_first()

        book = CommonItemLoader(item=Book(), response=response)
        book.add_value("link", response.url)
        book.add_value("cover", cover)
        book.add_value("hot", 0)
        book.add_value('book_name', str(book_name).strip())
        book.add_value('author', str(author).strip())
        book.add_value('category', category)
        book.add_value('status', status)
        book.add_value('type', "xbiquge")
        book.add_value('book_desc', book_desc)
        book.add_value("u_time", update_time[5:])
        book.add_value('last_chapter', latest_chapter_name)
        item = book.load_item()
        book_id = str(bookDB.insert_one(dict(item)).inserted_id)
        index = es.index(index="book",  id=book_id,
                         body={"book_name": book_name, "book_author": author})
        chapters = []
        for dd in selector.xpath("//*[@id='list']/dl/dd"):
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href').extract_first()
                name = dd.xpath('a/text()').extract_first()
                chapter = {
                    'book_id': book_id,
                    'link': site + s,
                    'chapter_name': name}
                chapters.append(chapter)
        if len(chapters) > 0:
            chapterDB.insert_many(chapters)
