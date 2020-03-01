# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class Demo3Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Book(scrapy.Item):
    _id = scrapy.Field('')
    hot = scrapy.Field('')
    u_time = scrapy.Field('')
    category = scrapy.Field('')
    book_name = scrapy.Field('')
    author = scrapy.Field('')
    book_desc = scrapy.Field('')
    status = scrapy.Field('')
    last_chapter = scrapy.Field('')
    last_chapter_id = scrapy.Field('')
    first_chapter_id = scrapy.Field('')
    
    cover = scrapy.Field('')
    link = scrapy.Field('')
class Chapter(scrapy.Item):
    book_id=scrapy.Field()
    _id=scrapy.Field()
    chapter_name=scrapy.Field()
    content=scrapy.Field()

class MeiZi(scrapy.Item):
    imgUrl = scrapy.Field()


class CommonItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class PiaoHua(scrapy.Item):
    title=scrapy.Field()
    cover=scrapy.Field()
    time=scrapy.Field()
    nation=scrapy.Field()
    type=scrapy.Field()
    language=scrapy.Field()
    releaseDate=scrapy.Field()
    rate=scrapy.Field()
    duration=scrapy.Field()
    actor=scrapy.Field()
    summary=scrapy.Field()
    bit=scrapy.Field()
    thunder=scrapy.Field()
