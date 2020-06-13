# -*- coding: utf-8 -*-
import datetime
import logging
import time

import pymongo
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, CommonItemLoader

site = 'https://www.xinxs.la'
domains = 'www.xinxs.la'
s = 0
# client = MongoClient('mongodb://lx:Lx520zx@120.27.244.128:27017/admin')
# client = pymongo.MongoClient(host='120.27.244.128', port=27017, username='lx', password='Lx520zx', authSource='admin')
# client = MongoClient(host='120.27.244.128', port=27017)
# db = client.admin
#
# db.authenticate('lx', 'Lx123456')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["bks"]
chapterDB = mydb["cps"]

ids = [f["_id"] for f in bookDB.find({}, {"_id": 1})]


class MeiziSpider(CrawlSpider):
    name = 'biqugetw'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/\d+_\d+/$', deny_domains='m.xinxs.la'),
             callback='parse_mm', follow=True, ),
        Rule(LinkExtractor(allow=r'/newclass/\d+/\d+.html$', deny_domains='m.xinxs.la'),
             follow=True, ),

        Rule(LinkExtractor(allow=r'/.*?/$', deny_domains='m.xinxs.la'),
             follow=True, ),
    )

    def parse_mm(self, response):
        id = ''.join(str(str(response.url).split('/')[-2]).split('_'))
        if ids.__contains__(id):
            return

        selector = Selector(response=response)
        book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content").extract_first()
        author = selector.xpath("//meta[@property='og:novel:author']/@content").extract_first()
        cover = selector.xpath("//meta[@property='og:image']/@content").extract_first()
        category = selector.xpath("//meta[@property='og:novel:category']/@content").extract_first()
        update_time = selector.xpath("//meta[@property='og:novel:update_time']/@content").extract_first()
        status = selector.xpath("//meta[@property='og:novel:status']/@content").extract_first()

        # latest_chapter_url = selector.xpath('//*[@id="info"]/p[4]/a/@href').extract_first()
        book_desc = selector.xpath("//meta[@property='og:description']/@content").extract_first()
        latest_chapter_name = selector.xpath(
            "//meta[@property='og:novel:latest_chapter_name']/@content").extract_first()

        book = CommonItemLoader(item=Book(), response=response)
        book.add_value("_id", id)
        book.add_value("link", response.url)
        book.add_value("cover", cover)
        book.add_value("hot", 0)
        book.add_value('book_name', str(book_name).strip())
        book.add_value('author', str(author).strip())
        book.add_value('category', category)
        book.add_value('status', status)
        book.add_value('book_desc', book_desc)
        book.add_value("u_time", update_time)
        book.add_value('last_chapter', latest_chapter_name)
        # book.add_value('last_chapter_id', str(latest_chapter_url).split('/')[-1].split('.')[0])
        item = book.load_item()
        bookDB.insert_one(dict(item))
        chapters = []
        for dd in selector.xpath("/html/body/div[3]/div[2]/div/div[2]//li"):
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href').extract_first()
                name = dd.xpath('a/text()').extract_first()
                cid = id + str(str(s).split('/')[2]).split('.')[0]
                chapter = {
                    'book_id': id,
                    'chapter_id': cid,
                    'content': site + s,
                    'chapter_name': name}
                chapters.append(chapter)
        if len(chapters) > 0:
            chapterDB.insert_many(chapters)

    def calc_book_state(selfs, u_time):

        try:
            nowTime_str = datetime.datetime.now().strftime('%Y-%m-%d')
            e_time = time.mktime(time.strptime(nowTime_str, "%Y-%m-%d"))
            if str(u_time).__contains__("最后更新"):
                u_time = u_time[5:]
            u_time = u_time[:10]
            s_time = time.mktime(time.strptime(u_time, '%Y-%m-%d'))
            # 日期转化为int比较
            diff = int(e_time) - int(s_time)
            if diff >= 60 * 60 * 24 * 30 * 3:
                return "完结"
            return "连载中"
        except Exception as e:
            logging.error(e)
        return "连载中"
