# -*- coding: utf-8 -*-
import pymongo
from redis import StrictRedis
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, CommonItemLoader

site = 'https://www.266ks.com'
domains = '266ks.com'

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["books"]
chapterDB = mydb["chapters"]

m_domain = "m.266ks.com"

redis = StrictRedis(host='120.27.244.128', port=6379, db=0, password='zx222lx')


class BiqugeSpider(CrawlSpider):
    name = '266ks'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/\d+_\d+/$', deny_domains=m_domain),
             callback='parse_mm', follow=True, ),
        Rule(LinkExtractor(allow=r'/newclass/\d+/\d+.html$', deny_domains=m_domain),
             follow=True, ),
        Rule(LinkExtractor(allow=r'/.*?/$', deny_domains=m_domain),
             follow=True, ),
    )

    def parse_mm(self, response):

        selector = Selector(response=response)
        book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content").extract_first()
        author = selector.xpath("//meta[@property='og:novel:author']/@content").extract_first()
        key = book_name + author
        if redis.exists(key):
            return
        redis.set(key, '')
        cover = selector.xpath("//meta[@property='og:image']/@content").extract_first()
        category = selector.xpath("//meta[@property='og:novel:category']/@content").extract_first()
        update_time = selector.xpath("//meta[@property='og:novel:update_time']/@content").extract_first()
        status = selector.xpath("//meta[@property='og:novel:status']/@content").extract_first()
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
        book.add_value('type', "266ks")
        book.add_value('book_desc', book_desc)
        book.add_value("u_time", update_time)
        book.add_value('last_chapter', latest_chapter_name)
        item = book.load_item()
        book_id = str(bookDB.insert_one(dict(item)).inserted_id)

        chapters = []
        for dd in selector.xpath('/html/body/div[3]/div[2]/div/div[2]/ul//li'):
            if len(dd.xpath('a/@href')) > 0:
                name = dd.xpath('a/text()').extract_first()
                s = dd.xpath('a/@href').extract_first()
                chapter = {
                    'book_id': book_id,
                    'link': site + s,
                    'chapter_name': name}
                chapters.append(chapter)
        if len(chapters) > 0:
            chapterDB.insert_many(chapters)
