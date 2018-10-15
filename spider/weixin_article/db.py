from pickle import dumps,loads
from request import WeixinRequest
from redis import StrictRedis
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_PASSWORD = None
REDIS_KEY = 'queue'
class RedisQueue():
    def __init__(self,host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD):
        '''
        初始化 Redis
        '''
        self.db = StrictRedis(host=host,port=port,password=password)
    def add(self,request):
        if isinstance(request,WeixinRequest):
            return self.db.rpush(REDIS_KEY,dumps(request))
        else:
            return False
    def pop(self):
        '''
        取出下一个Request并反序列化
        :return: Request or None
        '''
        if self.db.llen(REDIS_KEY):
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False
    def empty(self):
        return self.db.llen(REDIS_KEY) == 0