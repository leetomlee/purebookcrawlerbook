import scrapy
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
class BiqugeSpider(CrawlSpider):
    name = 'x'
    allowed_domains = ['www.biquge.co']
    start_urls = ['https://www.biquge.co/']

    rules = (
        Rule(LinkExtractor(allow=r'\d+_\d+/$', ),
             callback='parse_item',follow=True),
    )

    def parse_item(self, response):
        
        book={
            'title':response.xpath('//meta[@property="og:title"]/@content').extract_first(),
            'description':response.xpath('//meta[@property="og:description"]/@content').extract_first(),
            'cover':response.xpath('//meta[@property="og:image"]/@content').extract_first(),
            'category':response.xpath('//meta[@property="og:novel:category"]/@content').extract_first(),
            'author':response.xpath('//meta[@property="og:novel:author"]/@content').extract_first(),
            'bookName':response.xpath('//meta[@property="og:novel:book_name"]/@content').extract_first(),
            'link':response.xpath('//meta[@property="og:novel:read_url"]/@content').extract_first(),
            'updateTime':response.xpath('//meta[@property="og:novel:update_time"]/@content').extract_first(),
            'lastChapterName':response.xpath('//meta[@property="og:novel:latest_chapter_name"]/@content').extract_first(),
            'lastChapterUrl':response.xpath('//meta[@property="og:novel:latest_chapter_url"]/@content').extract_first()
        }
        if book['title'] is None:
            print(book['title'])
        else:
            yield book
        
        
        # dds = response.xpath('//*[@id="list"]/dl/dt[2]/following-sibling::dd')
        # for dd in dds:
        #     print(dd.xpath("a/text()").extract_first())
