# -*- coding: utf-8 -*-
import json
import random
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from flask import Flask, request
from flask_apscheduler import APScheduler
from lxml import etree

executor = ThreadPoolExecutor(max_workers=6)

app = Flask(__name__)

logger = app.logger

user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]
headers = {"User-Agent": random.choice(user_agent_list)}


def get_c(html):
    content = ""
    try:
        for text in html.xpath('//*[@id="content"]/text()'):
            if not str(text).strip() == "":
                if not str(text).startswith("\n"):
                    if is_chinese(str(text)):
                        content += "\t\t\t\t\t\t\t\t" + str(text).strip() + "\n"
    except Exception as e:
        logger.error(e)
        return ''

    if content.__contains__('DOCTYPE'):
        return ''
    return content


def get_c1(html):
    content = ""
    try:
        for t in html.xpath('//*[@id="content"]/p'):
            text = t.xpath('text()')[0]
            if not str(text).strip() == "":
                if not str(text).startswith("\n"):
                    if is_chinese(str(text)):
                        content += "\t\t\t\t\t\t\t\t" + str(text).strip() + "\n"
    except Exception as e:
        logger.error(e)
        return ''

    if content.__contains__('DOCTYPE'):
        return ''
    return content


def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False


@app.route('/', methods=['GET'])
def health():
    result = {
        "code": 200,
        "msg": "操作成功",
        "data": ""
    }
    return json.dumps(result, ensure_ascii=False)


@app.route('/book/chapter', methods=['GET'])
def get_chapter():
    content = ""
    url = request.args.get("url")
    html = getHTMLUtf8(url)

    if url.__contains__("xbiquge"):
        content = get_c(html)
    elif url.__contains__("dwxdwx"):
        content = get_c1(html)
    else:
        while True:
            content += get_c(html)
            next_text = html.xpath('//*[@id="container"]/div/div/div[2]/div[3]/a[3]/text()')[0]
            html = getHTMLUtf8(
                "https://www.266ks.com/" + html.xpath('//*[@id="container"]/div/div/div[2]/div[3]/a[3]/@href')[0])
            if next_text != "下一页":
                break
    return content


def getHTMLUtf8(url):
    get = getHTMLzz(url)
    if get is None:
        return get
    if get.status_code == 200:
        get.encoding = "utf-8"
        html = etree.HTML(get.text)
        return html
    return None


def get_proxy():
    return requests.get("http://134.175.83.19:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://134.175.83.19:5010/delete/?proxy={}".format(proxy))


def getHTMLzz(param):
    retry_count = 2
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            get = requests.get(param, proxies={"http": "http://{}".format(proxy)},
                               headers={"User-Agent": random.choice(user_agent_list)}, timeout=20)
            logger.info("使用代理 http://{}".format(proxy))
            return get
        except Exception as e:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    logger.info("不可用代理")
    return None


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.config['JSON_AS_ASCII'] = False

    app.run(port=777, host='0.0.0.0', threaded=True)

