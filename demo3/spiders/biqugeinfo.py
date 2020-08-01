# -*- coding: utf-8 -*-

import pymongo
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import Book, CommonItemLoader

site = 'http://www.biquge.info/'
domains = 'biquge.info'
s = 0
# client = MongoClient('mongodb://lx:Lx520zx@120.27.244.128:27017/admin')
# client = pymongo.MongoClient(host='120.27.244.128', port=27017, username='lx', password='Lx520zx', authSource='admin')
# client = MongoClient(host='120.27.244.128', port=27017)
# db = client.admin
#
# db.authenticate('lx', 'Lx123456')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["xbiquge"]
chapterDB = mydb["xchapter"]

keys = []
for f in bookDB.find({}, {"book_name": 1, "author": 1}):
    bname = ''
    au = ''
    try:
        bname = f["book_name"]
        au = f["author"]
    except Exception as e:
        pass
    keys.append(bname + au)


class BiqugeSpider(CrawlSpider):
    name = 'biqugeinfo'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'/\d+_\d+./$', deny_domains='m.biquge.info'),
             callback='parse_mm', follow=True, ),
        Rule(LinkExtractor(allow=r'/list/\d+_\d+.html/$', deny_domains='m.biquge.info'),
             follow=True, ),

        Rule(LinkExtractor(allow=r'/paihangbang_.*?/\d+.html$', deny_domains='m.biquge.info'),
             follow=True, ),
    )

    def parse_mm(self, response):
        id = 'info' + ''.join(str(str(response.url).split('/')[-2]).split('_'))

        selector = Selector(response=response)
        book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content").extract_first()
        author = selector.xpath("//meta[@property='og:novel:author']/@content").extract_first()
        if keys.__contains__(book_name + author):
            return
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
        for dd in selector.xpath("//*[@id='list']/dl/dd"):
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href').extract_first()
                name = dd.xpath('a/text()').extract_first()
                cid = id + str(s).split('.')[0]
                chapter = {
                    'book_id': id,
                    'chapter_id': cid,
                    'content': response.url + s,
                    'chapter_name': name}
                chapters.append(chapter)
        if len(chapters) > 0:
            chapterDB.insert_many(chapters)
