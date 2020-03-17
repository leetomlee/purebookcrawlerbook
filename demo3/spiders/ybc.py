# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule

from demo3.items import CommonItemLoader, Book, Chapter

site = 'https://www.biquge.com.cn'
domains = 'biquge.com.cn'


class MeiziSpider(CrawlSpider):
    name = 'ybc'
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
        ss = selector.xpath('//*[@id="list"]/dl/dd[1]/a/@href').extract_first().split('/')[3].split('.')[0]
        book.add_value("first_chapter_id", ss)
        book.add_xpath('book_name', "//*[@id='info']/h1/text()")
        book.add_value('author', selector.xpath("//*[@id='info']/p[1]/text()").extract_first().split('：')[1])
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
        # has = 10
        #
        # for dd in selector.xpath("//*[@id='list']/dl/dd"):
        #     if len(dd.xpath('a/@href')) > 0:
        #         s = dd.xpath('a/@href').extract_first()
        #         url = site + s
        #         name = dd.xpath('a/text()').extract_first()
        #         split = str(s).split('/')
        #         bid = split[2]
        #         cid = split[3].split('.')[0]
        #         chapter = CommonItemLoader(item=Chapter(), response=response)
        #         chapter.add_value('book_id', bid)
        #         chapter.add_value('_id', cid)
        #         chapter.add_value('content', url)
        #         chapter.add_value('chapter_name', name)
        #         chapter.add_value('has_content', has)
        #
        #         has += 1
        #         yield chapter.load_item()
