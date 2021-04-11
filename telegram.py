# Use your own values from my.telegram.org
import asyncio
import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from xmlrpc.client import ResponseError

from minio import Minio

minioClient = Minio('134.175.83.19:9090',
                    access_key='lix',
                    secret_key='lx123456zx',
                    secure=False)
from telethon import TelegramClient

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

to_js = True
executor = ThreadPoolExecutor()

api_id = 1074081
api_hash = 'eeb704250c14250d842d4db7cda45710'

proxies = {
    "http": "socks5://127.0.0.1:1080",

    "https": "socks5://127.0.0.1:1080",
}
# client = TelegramClient('123', api_id, api_hash)
# client = TelegramClient('123', api_id, api_hash, proxy=(socks.SOCKS5, '127.0.0.1', 1080))
client = TelegramClient('anon', api_id, api_hash, proxy=("socks5", 'localhost', 1080))
# client = TelegramClient('session_name', api_id, api_hash, proxy=(python_socks.ProxyType.SOCKS5, '127.0.0.1', 1080))
# client.start()
# 频道名称
keys = ["JinPingMei"]


# keys = ["sourcefornew"]


async def main(key):
    async for message in client.iter_messages(key):
        logging.info("download ")
        fileName=message.media.document.attributes[0].file_name
        # uid = str(uuid.uuid4())
        # suid = ''.join(uid.split('-'))
        # if message.photo:
        s = await client.download_media(message, local_filepath_txt + fileName)
        logging.info(s)
        try:
            minioClient.fput_object('txt', fileName, local_filepath_txt + fileName)
        except ResponseError as err:
            print(err)
        os.remove(local_filepath_txt + fileName)
# if message.video:
# s = await client.download_media(message, local_filepath_video + suid + '.mp4')
# logging.info(s)

# if message.message:
#     print(message.message)


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
    loop.close()
    client.disconnect()
