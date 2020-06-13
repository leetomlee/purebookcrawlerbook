# -*- coding: utf-8 -*-
import pymongo
from lxml import etree
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

site = 'https://91mjw.com/'
domains = '91mjw.com'
s = 0
# client = MongoClient('mongodb://lx:Lx520zx@120.27.244.128:27017/admin')
# client = pymongo.MongoClient(host='120.27.244.128', port=27017, username='lx', password='Lx520zx', authSource='admin')
# client = MongoClient(host='120.27.244.128', port=27017)
# db = client.admin
#
# db.authenticate('lx', 'Lx123456')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
movie = mydb["movie"]


class MeiziSpider(CrawlSpider):
    name = '91mjw'
    allowed_domains = [domains]
    start_urls = [
        site
    ]

    rules = (
        Rule(LinkExtractor(allow=r'video/\d+.htm$', ),
             callback='parse_mm', follow=True, ),

    )

    def parse_mm(self, response):
        result = []
        id = str(response.url).split('/')[-1]
        html = etree.HTML(response.text)
        str = ''
        t = html.xpath('/html/body/section/div/div/div/article/div[1]/div[2]/text()')
        for i, strong in enumerate(html.xpath('/html/body/section/div/div/div/article/div[1]/div[2]/strong')):
            str += strong.xpath('text()')[0] + t[i * 2] + '\n'

        result.append(str)
        jis = []
        for i in html.xpath('//*[@id="video_list_li"]/div/a'):
            jis.append({i.xpath('@id')[0]: i.xpath('text()')[0]})
        result.append(jis)
        desc = html.xpath('/html/body/section/div/div/div/article/p[1]/span/text()')
        result.append(''.join(desc))
        imgs = []
        for i in html.xpath('/html/body/section/div/div/div/article/p[2]/img'):
            imgs.append(i.xpath('@data-original')[0])
        result.append(imgs)
        print(result)
