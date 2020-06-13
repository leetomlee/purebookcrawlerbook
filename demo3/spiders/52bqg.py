# -*- coding: utf-8 -*-
from redis import StrictRedis
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, CommonItemLoader

site = 'https://www.52bqg.com/'
domains = '52bqg.com'
s = 0
redis = StrictRedis(host='120.27.244.128', port=6379, db=0, password='zx222lx')


class MeiziSpider(CrawlSpider):
    name = '52bqg'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/book_\d+/$', deny_domains=['m.52bqg.com']),
             callback='parse_mm', follow=True, ),
        Rule(LinkExtractor(allow=r'/.*?/$', deny_domains=['m.52bqg.com']),
             follow=True, ),
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
        latest_chapter_url = selector.xpath("//meta[@property='og:novel:latest_chapter_url']/@content").extract_first()
        book_desc = selector.xpath("//meta[@property='og:description']/@content").extract_first()

        key = book_name + author
        if not redis.exists(key):
            id = str(response.url).split('/')[-2].split('_')[1]
            book = CommonItemLoader(item=Book(), response=response)
            book.add_value("_id", "11111111"+id)
            book.add_value("link", response.url)
            book.add_value("cover", cover)
            book.add_value("hot", 0)

            book.add_value('book_name', book_name)
            book.add_value('author', author)
            book.add_value('category', category)
            book.add_value('status', status)
            book.add_value('book_desc', book_desc)
            book.add_value("u_time", update_time)
            book.add_value('last_chapter', latest_chapter_name)
            book.add_value('last_chapter_id', str(latest_chapter_url).split('/')[-1].split('.')[0])
            item = book.load_item()
            yield item
        # if not redis.exists(key):

        # print(book_name+author)
