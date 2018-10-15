# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sys import path
path.append('D:\\software\python\\test\\spider\\weibo\\weibo')
from items import WeiboItem,UserItem,UserRelationItem
import time
import pymongo
class WeiboPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item,WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item['created_at'])

    def parse_time(self,date):
        if re.match('刚刚',date):
            date = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        if re.match('\d+分钟前',date):
            minute = re.match(r'(\d+)',date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time() - float(minute)*60))
        if re.match('\d+小时前',date):
            hours = re.match(r'(\d+)',date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()-float(hours)*60*60))
        if re.match('昨天.*',date):
            date = re.match('昨天(.*)',date).group(1)
            date = time.strftime('%Y-%m-%d',time.localtime(time.time()-24*60*60)) + ' ' + date
        if re.match('\d{2}-\d{2}',date):
            date = time.strftime('%Y-',time.localtime()) + date + '00:00'
        return date

class TimePipeline():
    def process_item(self,item,spider):
        if isinstance(item,WeiboItem) or isinstance(item,UserItem):
            now = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
            item['crawled_at'] = now
        return item
class MongoPipeling(object):
    def __init__(self,mongo_uri,mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[UserItem.collection].create_index([('id',pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('id',pymongo.ASCENDING)])
    def close_spider(self,spider):
        self.client.close()
    def process_item(self,item,spider):
        if isinstance(item,UserItem) or isinstance(item,WeiboItem):
            self.db[item.collection].update({'id':item.get('id')},{'$set',item},True)
        if isinstance(item,UserRelationItem):
            self.db[item.collection].update(
                {'id':item.get('id')},
                {'$addToSet':
                     {
                         'follows':{'$each':item['follows']},
                         'fans':{'$each':item['fans']}
                     }
                },True)
        return item