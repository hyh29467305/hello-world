from requests import Session,ConnectionError,ReadTimeout
from db import RedisQueue
from mysql import Mysql
import requests
from urllib.parse import urlencode
from request import WeixinRequest
from pyquery import PyQuery as pq
MAX_FAILED_TIME = 5
VALID_STATUSES = [200]
class Spider():
    base_url = 'http://weixin.sogou.com/weixin'
    keyword = 'NBA'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'SUID=329D9B273865860A598BD206000E05BC; ABTEST=0|1536152449|v1; IPLOC=CN1100; weixinIndexVisited=1; SUV=00334F7972F4B9F35B8FD385513C8523; SNUID=9111B04D3832425DCA568C3938B9B969; sct=2; JSESSIONID=aaaJrY-Zle4RBb7vUTBvw',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    session = Session()
    queue = RedisQueue()
    mysql = Mysql()
    def get_proxy(self):
        '''
        获取随机代理
        :return: 随机代理
        '''
        proxy_url = 'http://127.0.0.1:8080/random'
        try:
            response = requests.get(proxy_url)
            if response.status_code == 200:
                print("GET Proxy:",response.text)
                return response.text
            return None
        except requests.ConnectionError:
            return None
    def start(self):
        '''
        开始第一个请求
        :return:
        '''
        self.session.headers.update(self.headers)
        start_url = self.base_url + '?' + urlencode({'type':'2','query':self.keyword})
        weixin_request = WeixinRequest(start_url,self.parse_index,need_proxy=True)
        self.queue.add(weixin_request)
    def parse_index(self,response):
        '''
        解析索引页
        :param response: 响应
        :return: 新的请求
        '''
        doc = pq(response.text)
        items = doc('.news-box .news-list li txt-box h3 a').items()
        for item in items:
            url = item.attr('href')
            weixin_request = WeixinRequest(url=url,callback=self.parse_detail)
            yield weixin_request
        # next = doc('#sogou_next')
        # if next:
        #     url = self.base_url + next.attr('href')
        #     weixin_request = WeixinRequest(url=url,callback=self.parse_index,need_proxy=True)
        #     yield weixin_request
    def parse_detail(self,response):
        '''
        解析详情页
        :param response: 响应
        :return: 微信公众号文章
        '''
        doc = pq(response.text)
        data = {
            'title':doc('.rich_media_title').text(),
            # 'content':doc('.rich_media_content').text(),
            'date':doc('.rich_media_meta_list #publish_time').text(),
            'nickname':doc('.rich_media_meta_list .rich_media_meta_text').text(),
            'wechat':doc('.rich_media_meta_list .rich_media_meta_nickname').text()
        }
        print(data)
        yield data
    def request(self,weixin_request):
        '''
        执行请求
        :param weixin_request: 请求
        :return: 响应
        '''
        # try:
        if weixin_request.need_proxy:
            proxy = self.get_proxy()
            if proxy:
                proxies = {
                    'http':'http://' + proxy,
                    'https':'http://'+proxy
                }
                return self.session.send(weixin_request.prepare(),timeout=weixin_request.timeout,
                                         allow_redirects=False,proxies=proxies,verify=False)
        return self.session.send(weixin_request.prepare(),timeout=weixin_request.timeout,
                                 allow_redirects=False,verify=False)
        # except Exception as e:
        #     print(e.args)
        #     return False

    def error(self,weixin_request):
        weixin_request.fail_time += 1
        print('Request Failed',weixin_request.fail_time,'Times',weixin_request.url)
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)
    def schedule(self):
        while not self.queue.empty():
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            print("Schedule",weixin_request.url)
            response = self.request(weixin_request)
            print(response)
            if response and response.status_code in VALID_STATUSES:
                results = list(callback(response))
                if results:
                    for result in results:
                        if isinstance(result,WeixinRequest):
                            self.queue.add(result)
                        if isinstance(result,dict):
                            self.mysql.insert('articles',result)
                else:
                    self.error(weixin_request)
                    print(response)
            else:
                self.error(weixin_request)
    def run(self):
        self.start()
        self.schedule()
if __name__ == '__main__':
    spider = Spider()
    spider.run()