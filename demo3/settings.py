# -*- coding: utf-8 -*-


BOT_NAME = 'demo3'

SPIDER_MODULES = ['demo3.spiders']
NEWSPIDER_MODULE = 'demo3.spiders'
# DEPTH_LIMIT = 5
ROBOTSTXT_OBEY = False

# DOWNLOAD_DELAY = 1.5

COOKIES_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'demo3.pipelines.RotateUserAgentMiddleware': 400

}


ITEM_PIPELINES = {
    # 'scrapy.pipelines.images.ImagesPipeline': 2,
    # 'demo3.pipelines.PiaoHuaPipeline': 1
    'demo3.pipelines.CrawlerScrapyPipeline': 1,
    # 'scrapy_redis.pipelines.RedisPipeline': 300
}
LOG_LEVEL ='ERROR'
REDIS_HOST = "120.27.244.128"
REDIS_PORT = "6379"
REDIS_PARAMS = {
    'password': 'zx222lx',
}
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER_PERSIST = True
MYSQL_HOST = '120.27.244.128'
MYSQL_DBNAME = 'book'  # 数据库名字，请修改
MYSQL_USER = 'root'  # 数据库账号，请修改
MYSQL_PASSWD = 'lx123456zx'  # 数据库密码，请修改

MYSQL_PORT = 3306  # 数据库端口，在dbhelper中使用

REDIS_PASSWD = 'zx222lx'
