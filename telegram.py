# Use your own values from my.telegram.org
import asyncio
import base64
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import requests
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.tl.types import InputMessagesFilterVideo
from telethon.tl.types import InputMessagesFilterDocument

pool = ThreadPoolExecutor(max_workers=2)
# from minio import Minio
#
# minioClient = Minio('134.175.83.19:9090',
#                     access_key='lix',
#                     secret_key='lx123456zx',
#                     secure=False)
from telethon import TelegramClient

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

to_js = True
executor = ThreadPoolExecutor()

api_id = 1074081
api_hash = 'eeb704250c14250d842d4db7cda45710'


# client = TelegramClient('123', api_id, api_hash)
client = TelegramClient('123', api_id, api_hash)
# client = TelegramClient('anon', api_id, api_hash, proxy=("socks5", 'localhost', 7890))
# client = TelegramClient('session_name', api_id, api_hash, proxy=(python_socks.ProxyType.SOCKS5, '127.0.0.1', 1080))
# client.start()
# 频道名称
keys = ["tg_1314"]

# keys = ["sourcefornew"]
message_list = []


async def fun(message):
    await client.download_media(message, local_filepath_photo)


from concurrent.futures import ThreadPoolExecutor

theard_pool = ThreadPoolExecutor(max_workers=2)
ffs = []

async def main(key):
    i = 0

    async for message in client.iter_messages(key, filter=InputMessagesFilterDocument):
        i = i + 1
        await client.download_media(message, local_filepath_txt)
        print(i)
        # await client.download_media(message, local_filepath_photo)

        # ff = await client.download_media(message, local_filepath_photo)
        # print(ff)


async def down_load(message):
    print(message.id)
    res=await client.download_media(message, local_filepath_photo)
    print(res)
    proxies = {
        #该代理服务器在免费代理网站上得到的，这样的网站有很多
        # 'http': '127.0.0.1：7891',
    }
    url = "https://api.github.com/repos/leetomlee/blogimage/contents/%s" % res.split("\\")[-1]
    # f = {"files": open(res, "rb")}
    pic=open(res,'rb')
#读取文件内容，转换为base64的编码，字符串类型
    str_pic=base64.b64encode(pic.read())
    pic.close()
    data={
        "branch":"master",
        "content":str_pic,
        "message":"upload picture via python program"
    }

    headers = {"authorization": "token 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"}
    res = requests.put(url,data=data, headers=headers, verify=False,proxies=proxies)
    print(res)


if __name__ == '__main__':
    local_filepath_photo = os.path.abspath(os.curdir) + '/r/photo/'
    if not os.path.exists(local_filepath_photo):
        os.makedirs(local_filepath_photo)
    local_filepath_video = os.path.abspath(os.curdir) + '/r/mp4/'
    if not os.path.exists(local_filepath_video):
        os.makedirs(local_filepath_video)
    local_filepath_txt = os.path.abspath(os.curdir) + '/r/txt/'
    if not os.path.exists(local_filepath_txt):
        os.makedirs(local_filepath_txt)
    client.start()

    task = [main(i) for i in keys]
    loop = asyncio.get_event_loop()
    # 在事件循环中执行task列表
    loop.run_until_complete(asyncio.wait(task))



