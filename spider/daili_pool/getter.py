from db import RedisClient
from crawler import Crawler
MAX_POOL = 1000
class Getter():
    def __init__(self):
        self.redis = RedisClient()
        self.crawl = Crawler()
    def is_over_limit(self):
        if self.redis.count() > MAX_POOL:
            return True
        else:
            return False
    def run(self):
        print("获取器开始执行")
        if not self.is_over_limit():
            for name in range(self.crawl.__CrawlFuncCount__):
                proxies = self.crawl.get_proxies(self.crawl.__CrawlFunc__[name])
                for proxy in proxies:
                    self.redis.add(proxy)
if __name__ == '__main__':
    getter = Getter()
    getter.run()