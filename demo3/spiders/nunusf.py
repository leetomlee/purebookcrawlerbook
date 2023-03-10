# -*- coding: utf-8 -*-
import logging

import pymongo
import requests
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, CommonItemLoader

type = "nunusf"
site = 'https://www.nunusf.com/'
domains = 'www.nunusf.com'
s = 0
# client = MongoClient('mongodb://lx:Lx520zx@120.27.244.128:27017/admin')
# client = pymongo.MongoClient(host='120.27.244.128', port=27017, username='lx', password='Lx520zx', authSource='admin')
# client = MongoClient(host='120.27.244.128', port=27017)
# db = client.admin
#
# db.authenticate('lx', 'Lx123456')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@121.37.139.13:27017/', connect=False)
# myclient = pymongo.MongoClient('mongodb://lx:Lx123456@23.91.100.230:27017/')
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]
# es = Elasticsearch(
#     ['23.91.100.230:8088'],
#     # 认证信息
#     http_auth=('elastic', 'jXqw0zF3XPOxu8PThv8H')
# )


# redis = StrictRedis(host='23.91.100.230', port=6379, db=0, password='zx222lx')
# redis = StrictRedis(host='localhost', port=6379, db=1, password='zx222lx')

# https://www.biquge.co/0_410/

class NunusfSpider(CrawlSpider):
    name = type
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/\w+/\w+/$', ),
             callback='parse_mm', follow=True, ),
        # Rule(LinkExtractor(allow=r'/.*?/$', ),
        #      follow=True, ),
        # Rule(LinkExtractor(allow=r'/.*?/\d+_\d+.html$', ),
        #      follow=True, ),
    )

    def parse_mm(self, response):

        selector = Selector(response=response)
        book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content").extract_first()
        author = selector.xpath("//meta[@property='og:novel:author']/@content").extract_first()

        cover = selector.xpath("//meta[@property='og:image']/@content").extract_first()
        category = selector.xpath("//meta[@property='og:novel:category']/@content").extract_first()
        status = selector.xpath("//meta[@property='og:novel:status']/@content").extract_first()
        update_time = selector.xpath("//meta[@property='og:novel:update_time']/@content").extract_first()

        latest_chapter_name = selector.xpath(
            "//meta[@property='og:novel:latest_chapter_name']/@content").extract_first()
        book_desc = selector.xpath("//meta[@property='og:description']/@content").extract_first()

        book = CommonItemLoader(item=Book(), response=response)
        book.add_value("link", response.url)
        book.add_value("cover", cover)
        book.add_value("hot", 0)
        book.add_value('book_name', str(book_name).strip())
        book.add_value('author', str(author).strip())
        book.add_value('category', category)
        book.add_value('status', status)
        book.add_value('type', type)
        book.add_value('book_desc', book_desc)
        book.add_value("u_time", update_time)
        book.add_value('last_chapter', latest_chapter_name)
        item = book.load_item()
        book_id = str(bookDB.insert_one(dict(item)).inserted_id)

        chapters = []
        page_nums = selector.xpath('//*[@id="pageNum"]/div/span[2]/text()').extract_first()
        bookid = selector.xpath('//*[@id="bookDetails"]/@data-bookid').extract_first()
        for page in range(int(page_nums)):
            uks = "https://www.nunusf.com/e/extend/bookpage/pages.php?id=" + bookid + "&pageNum=" + str(
                int(page)) + "&dz=asc"

            json = requests.get(uks).json()
            if 'list' in json:
                for item in json['list']:
                    chapter = {
                        'book_id': "",
                        'link': item['pic'],
                        'chapter_name': item['title']}
                    chapters.append(chapter)
        if len(chapters) > 0:
            chapterDB.insert_many(chapters)
