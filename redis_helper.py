import redis
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, password='zx222lx')
redis = redis.Redis(connection_pool=pool)

class RedisHelper:

    def __init__(self):
        self.__conn = redis
        self.chan_sub = 'cps'
        self.chan_pub = 'cps'

    def public(self, msg):
        self.__conn.publish(self.chan_pub, msg)
        return True

    def subscribe(self):
        pub = self.__conn.pubsub()#打开收音机
        pub.subscribe(self.chan_sub)#调频道
        pub.parse_response()#准备接收
        return pub