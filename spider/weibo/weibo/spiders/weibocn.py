# -*- coding: utf-8 -*-
import scrapy
from sys import path
path.append('D:\\software\python\\test\\spider\\weibo\\weibo')
from scrapy import Request,Spider
import json
from items import UserItem,UserRelationItem,WeiboItem
import re
import time

class WeibocnSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['m.weibo.cn']
    user_url = 'https://m.weibo.cn/u/{uid}?uid={uid}&luicode=10000011'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&luicode=10000011&type={uid}&value={uid}&containerid=107603{uid}&page={page}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id={page}'
    start_users = ['1865901305']

    def parse(self, response):
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid),callback=self.parse_user)
    def parse_user(self,response):
        '''
        解析用户信息
        :param response: Response对象
        :return:
        '''
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id':'id',
                'name':'screen_name',
                'avatar':'profile_image_url',#头像
                'cover':'https://tva1.sinaimg.cn/crop.0.0.640.640.640/549d0121tw1egm1kjly3jj20hs0hsq4f.jpg',
                'gender':'gender',
                'description':'description',
                'fans_count':'followers_count',
                'follows_count':'follow_count',
                'weibos_count':'statuses_count',
                'verified':'verified',
                'verified_reason':'verified_reason',
                'verified_type':'verified_type'
            }
            for field,attr in field_map:
                user_item[field] = user_info.get(attr)
            yield user_item
            #关注
            uid = user_info.get('id')
            yield Request(self.follow_url.format(uid=uid,page=1),callback=self.parse_follows,
                          meta={'page':1,'uid':uid})
            #粉丝
            yield Request(self.fan_url.format(uid=uid,page=1),callback=self.parse_fans,
                          meta={'page':1,'uid':uid})
            #微博
            yield Request(self.weibo_url.format(uid=uid,page=1),callback=self.parse_weibos,
                          meta={'page':1,'uid':uid})
    def parse_follows(self,response):
        '''
        解析用户关注
        :param response:Response对象
        :return:
        '''
        result = json.loads(response.text)
        if result.get('data').get('cards')[-1].get('card_group'):
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid),callback=self.parse_user)
            uid = response.meta.get('uid')
            user_relation_item = UserItem()
            follows = [{'id':follow.get('user').get('id'),'name':follow.get('user').get('screen_name')}
                        for follow in follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item
            page = response.get('meta').get('page') + 1
            yield Request(self.follow_url.format(uid=uid,page=page),callback=self.parse_follows,meta={'page':page,'uid':uid})

    def parse_fans(self,response,user_relation_item):
        result = json.loads(response.text)
        if result.get('data').get('cards')[-1].get('card_group'):
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid),callback=self.parse_user())
            uid = response.get('meta').get('uid')
            fans = [{'id':fan.get('user').get('id'),'name':fan.get('user').get('screen_name')} for fan in fans]
            user_relation_item['fans'] = fans
            yield user_relation_item
            page = response.get('meta').get('page') + 1
            yield Request(self.fan_url.format(uid=uid,page=page),callback=self.parse_fans)
    def parse_weibos(self,response):
        result = json.loads(response.text)
        if result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id':'id',
                        'attitudes_count':'attitudes_count',
                        'comments_count':'comments_count',
                        'created_at':'created_at',
                        'reposts_count':'reposts_count',
                        'picture':'original_pic',
                        'pictures':'pics',
                        'source':'source',
                        'text':'text',
                        'raw_text':'raw_text',
                        'thumbail':'thumbnail_pic'
                    }
                    for field,attr in field_map:
                        weibo_item[field] = mblog.get(attr)
                        weibo_item['user'] = response.get('meta').get('uid')
                        yield weibo_item
        uid = response.get('meta').get('uid')
        page = response.get('meta').get('page') + 1
        yield Request(self.weibo_url.format(uid=uid,page=page),callback=self.parse_weibos,
                      meta={'uid':uid,'page':page})


