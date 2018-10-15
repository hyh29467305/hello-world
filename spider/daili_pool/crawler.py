import json
from pyquery import PyQuery as pq
import requests
def get_page(url):
    response = requests.get(url)
    return response.text
class ProxyMetaclass(type):
    def __new__(cls,name,bases,attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k,v in attrs.items():
            if 'crawl' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls,name,bases,attrs)
class Crawler(object,metaclass=ProxyMetaclass):
    def get_proxies(self,callback):
        '''
        获取代理
        :param callback:获取代理所调用的函数
        :return: 获取到的所有代理
        '''
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print("成功取到代理",proxy)
            proxies.append(proxy)
        return proxies
    def crawl_daili666(self,page_count=4):
        start_url = "http://www.66ip.cn/{}.html"
        urls = [start_url.format(page) for page in range(1,page_count+1)]
        print(urls)
        for url in urls:
            print("crawling",url)
            try:
                html = get_page(url)
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip,port])
            except Exception:
                print(url,"爬取失败")
    def crawl_proxy89(self,page_count=4):
        '''
        获取Proxy89
        :return: 代理
        '''
        start_url = 'http://www.89ip.cn/index_{}.html'
        urls = [start_url.format(page) for page in range(1,page_count+1)]
        for url in urls:
            print("crawling",url)
            try:
                html = get_page(url)
                doc = pq(html)
                trs = doc('.layui-form table tbody tr').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text().strip()
                    port = tr.find('td:nth-child(2)').text().strip()
                    yield ':'.join([ip, port])
            except Exception:
                print(url,"爬取失败")
    def crawl_goubanjia(self):
        '''
        获取goubanjia
        :return: 代理
        '''
        url = 'http://www.goubanjia.com/'
        print("crawling",url)
        try:
            html = get_page(url)
            doc = pq(html)
            trs = doc('.container-fluid table tbody tr')
            for tr in trs:
                print(tr)
                ips = tr.find('td:nth-child(1) span').text().strip()
                print(ips)
                ip = ''.join(ips)
                print(ip)
                yield ip
        except Exception:
            print(url,"爬取失败")
if __name__ == '__main__':
    crawl = Crawler()
    crawl.crawl_goubanjia()