# -*- coding: utf-8 -*-

import pymongo
import scrapy
from bloom_filter import BloomFilter
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, Chapter, CommonItemLoader

address = '120.27.244.128'

site = 'https://www.biquge.com.cn'
domains = 'biquge.com.cn'
# conn = pymysql.connect(host=address, user="root",
#                        password="lx123456zx", database="book", charset="utf8")
# cursor = conn.cursor()

client = pymongo.MongoClient(host='120.27.244.128')
chapter = client['book']['chapter']
bloom_filter = BloomFilter(max_elements=100000000, error_rate=0.001)
all = chapter.find({}, {"$project": 1})
for f in all:
    bloom_filter.add(f['_id'])
print("chushihua success")


class MeiziSpider(CrawlSpider):
    name = 'yb'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/book/\d+/$'),
             callback='parse_mm', follow=True),
    )

    def parse_mm(self, response):
        id = str(response.url).split('/')[4]
        selector = Selector(response=response)
        book = CommonItemLoader(item=Book(), response=response)
        book.add_value("_id", id)
        book.add_value("link", response.url)
        book.add_value("cover", selector.xpath(
            "//*[@id='fmimg']/img/@src").extract_first())
        book.add_value("hot", 1)
        ss=selector.xpath('//*[@id="list"]/dl/dd[1]/a/@href').extract_first().split('/')[3].split('.')[0]
        book.add_value("first_chapter_id",ss)
        book.add_xpath('book_name', "//*[@id='info']/h1/text()")
        # book.add_xpath('author', "//*[@id='info']/p[1]/text()")
        book.add_value('author',selector.xpath("//*[@id='info']/p[1]/text()").extract_first().split('：')[1])
        book.add_xpath('category', "//*[@class='con_top']/a[2]/text()")
        book.add_value('status', selector.xpath(
            "//*[@id='info']/p[2]/text()").extract_first().split('：')[1][:-1])
        book.add_value('book_desc', selector.xpath(
            "//*[@id='intro']/text()").extract_first())
        x = selector.xpath("//*[@id='info']/p[3]/text()").extract_first()
        book.add_value("u_time",
                       str(x)[-19:])
        book.add_xpath('last_chapter', "//*[@id='info']/p[4]/a/text()")
        fk = selector.xpath("//*[@id='info']/p[4]/a/@href").extract_first()
        book.add_value('last_chapter_id', str(fk).split('/')[-1].split('.')[0])
        item = book.load_item()
        yield item

        for dd in selector.xpath("//*[@id='list']/dl/dd"):
            url = site + dd.xpath('a/@href').extract_first()
            name = dd.xpath('a/text()').extract_first()
            cid = str(url).split('/')[5].split('.')[0]
            if not cid in bloom_filter:
                yield scrapy.Request(url=url, callback=self.parseContent, meta={"name": name})

    def parseContent(self, response):
        selector = Selector(response=response)
        content = '\n\r'.join(selector.xpath('//*[@id="content"]/text()').getall())
        bookId = str(response.url).split('/')[4]
        chapterId = str(response.url).split('/')[5].split('.')[0]
        chapter = CommonItemLoader(item=Chapter(), response=response)
        chapter.add_value('book_id', bookId)
        chapter.add_value('_id', chapterId)
        chapter.add_value('chapter_name', response.meta['name'])
        chapter.add_value('content', content)
        item = chapter.load_item()
        yield item
