# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class XiachufangsPipeline:
    def open_spider(self, spider):
        host = spider.settings['MONGODB_HOST']
        port = spider.settings['MONGODB_PORT']
        db_name = spider.settings['MONGODB_NAME']
        self.myclient = pymongo.MongoClient('mongodb://lx:Lx123456@%s:27017/'%host, connect=False)
        self.mydb = self.myclient["book"]
        self.bookDB = self.mydb["books"]
        self.item_list =0

    def process_item(self, item, spider):
        print(item)
        self.bookDB.insert_one(dict(item))
        
        return item
    
    def close_spider(self,spider):
        print('{}条数据已存入数据库'.format(self.item_list))
        self.myclient.close()
        print('数据库已关闭')
