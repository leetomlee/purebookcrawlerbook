import logging  # 引入logging模块
import time
from concurrent.futures.process import ProcessPoolExecutor

import requests
from loguru import logger
from redis import StrictRedis

ex = ProcessPoolExecutor()
logging.basicConfig(level=logging.INFO)  # 设置日志级别

redis = StrictRedis(host='134.175.83.19', port=6379, db=4, password='zx222lx')
# redis = StrictRedis(host='localhost', port=6379, db=4, password='zx222lx')


if __name__ == '__main__':
    logger.info("开始消费章节数据")
    pubsub = redis.pubsub()

    subscribe = pubsub.subscribe("cps")
    while True:
        msg = pubsub.parse_response()
        requests.get("http://localhost:7012/v1/book/chapter/" + str(msg[2]))

        time.sleep(1)
