#!flask/bin/python
# -*- coding: utf-8 -*-
import json
import os
import random
import re
import threading
import urllib
from concurrent.futures import ALL_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor

import pymongo
import records
import redis
import requests
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler
from lxml import etree

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["bks"]
chapterDB = mydb["cps"]
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


class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        {  # 第二个任务，每隔5S执行一次
            'id': 'job2',
            'func': '__main__:freshIdx',  # 方法名
            'args': (),  # 入参
            'trigger': 'cron',  # interval表示循环任务
            'hour': 1,
        }
    ]


executor = ThreadPoolExecutor(max_workers=6)
# logger.add("%s.log" % __file__.rstrip('.py'),
#            format="{time:MM-DD HH:mm:ss} {level} {message}")
app = Flask(__name__)

app.config.from_object(Config())

logger = app.logger

pool = redis.ConnectionPool(host='120.27.244.128', port=6379, decode_responses=True, password='zx222lx')
redis = redis.Redis(connection_pool=pool)
db = records.Database('mysql+pymysql://root:fKH31da8eqJHIU134ms1@120.27.244.128:3306/ph')
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}

def get_c(html):
    content = ""
    for text in html.xpath('//*[@id="content"]/text()'):
        if not str(text).strip() == "":
            if not str(text).startswith("\n"):
                if is_chinese(str(text)):
                    content += "\t\t\t\t\t\t\t\t" + str(text).strip() + "\n"
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


def getList(html):
    articles = html.xpath('//article[@class="u-movie"]')
    movies = []
    for article in articles:
        try:
            movies.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
        except Exception as err:
            logger.error(err)
    return movies[:-3]


def list_page(url):
    result = []
    all_task = []
    resp = requests.get(url, headers=headers)
    html = etree.HTML(resp.text)
    vkeys = html.xpath('//*[@class="phimage"]/div/a/@href')
    gif_keys = html.xpath('//*[@class="phimage"]/div/a/img/@src')
    gif_keys1 = html.xpath('//*[@class="phimage"]/div/a/img/@data-src')
    for i in range(len(vkeys)):
        cover = str(gif_keys[i])
        if not cover.startswith('http'):
            cover = gif_keys1[i]
            if not cover.startswith('http'):
                return
        try:
            if 'ph' in vkeys[i]:
                all_task.append(executor.submit(detail_page, 'https://www.pornhub.com' + vkeys[i], cover, result))

        except Exception as err:
            logger.error(err)
    wait(all_task, return_when=ALL_COMPLETED)
    return result


def detail_page(url, webm, result):
    s = requests.Session()
    resp = s.get(url, headers=headers)
    html = etree.HTML(resp.content)
    title = ''.join(html.xpath('//h1//text()')).strip()

    js = html.xpath('//*[@id="player"]/script/text()')[0]
    tem = re.findall(
        'var\\s+\\w+\\s+=\\s+(.*);\\s+var player_mp4_seek', js)[-1]
    con = json.loads(tem)
    filepath = '%s/%s.%s' % ('mp4', title, 'mp4')
    if os.path.exists(filepath):
        logger.info('this file had been downloaded :: %s' % filepath)
        return
    for _dict in con['mediaDefinitions']:
        if 'quality' in _dict.keys() and _dict.get('videoUrl'):
            logger.info('%s %s' %
                        (_dict.get('quality'), _dict.get('videoUrl')))
            logger.info('start download...')
            try:
                #
                # webm, _dict.get('videoUrl'), title, key
                result.append({'cover': webm, 'id': _dict.get('videoUrl'), 'name': title})
                break

            except Exception as err:
                logger.error(err)


def GetVkeyParam(firstUrl, secUrl, rule):
    res = []
    heads = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Referer": firstUrl
    }

    html = etree.HTML(requests.get(firstUrl + secUrl + '.html', headers=heads).text)
    tem = []
    a1 = ''
    a2 = ''
    all_like = []
    eve_up = []
    if rule == 1:
        js = html.xpath('/html/body/section/script')
        tem = re.findall('"(.*?)"', js[0].text)
        a1 = '/html/body/section/div/div/div[4]/div[1]/article'
        a2 = '/html/body/section/div/div/div[5]/div/article'
        for article in html.xpath(a1):
            if len(article.xpath('h2')) > 0:
                all_like.append({'cover': article.xpath('a/div/img/@data-original')[0],
                                 'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                                 'name': article.xpath('h2/a/text()')[0]})
            else:
                all_like.append({'cover': article.xpath('a/div/img/@data-original')[0],
                                 'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                                 'name': article.xpath('a/h2/text()')[0]})
        res.append(all_like)

        for article in html.xpath(a2):
            if len(article.xpath('h2')) > 0:
                eve_up.append({'cover': article.xpath('a/div/img/@data-original')[0],
                               'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                               'name': article.xpath('h2/a/text()')[0]})
            else:
                eve_up.append({'cover': article.xpath('a/div/img/@data-original')[0],
                               'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                               'name': article.xpath('a/h2/text()')[0]})
        res.append(eve_up)
        res.append(urllib.parse.unquote(str(tem[2]), encoding='utf-8', errors='replace'))
    else:
        js = html.xpath('/html/body/section/div/div/script')
        tem.append(re.findall("vid = '(.*?)';", js[0].text)[0])
        tem.append(re.findall("play_type = '(.*?)';", js[0].text)[0])

        a1 = '/html/body/section/div/div/div[4]/div[1]/div/div[2]/article'
        a2 = '/html/body/section/div/div/div[4]/div[1]/div/div[3]/article'
        for article in html.xpath(a1):
            if len(article.xpath('h2')) > 0:
                all_like.append({'cover': article.xpath('a/div/img/@src')[0],
                                 'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                                 'name': article.xpath('h2/a/text()')[0]})

            else:
                all_like.append({'cover': article.xpath('a/div/img/@data-original')[0],
                                 'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                                 'name': article.xpath('a/h2/text()')[0]})
        res.append(all_like)

        for article in html.xpath(a2):
            if len(article.xpath('h2')) > 0:
                eve_up.append({'cover': article.xpath('a/div/img/@data-original')[0],
                               'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                               'name': article.xpath('h2/a/text()')[0]})
            else:
                eve_up.append({'cover': article.xpath('a/div/img/@src')[0],
                               'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                               'name': article.xpath('a/h2/text()')[0]})
        res.append(eve_up)

        res.append(urllib.parse.unquote(str(tem[0]), encoding='utf-8', errors='replace'))
    return res


def GetDownloadUrl(payload, refereUrl):
    heads = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Host": "api.1suplayer.me",
        "Referer": refereUrl,
        "Origin": "https://api.1suplayer.me",
        "X-Requested-With": "XMLHttpRequest"
    }
    while True:
        retData = json.loads(requests.post("https://api.1suplayer.me/player/api.php", data=payload, headers=heads).text)
        if retData["code"] == 200:
            return retData["url"]
        elif retData["code"] == 404:
            payload["refres"] += 1;
            continue
        else:
            return None


def GetOtherParam(firstUrl, SecUrl, type, vKey, rule):
    heads = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",

        "Referer": firstUrl + SecUrl + '.html'
    }
    url = ''
    if rule == 1:
        url = "https://chaoren.sc2yun.com/play.php?v=%s&type=%s" % (type, vKey)
        html = etree.HTML(requests.get(url, headers=heads).text)
        content = html.xpath('//body/script/text()')[0]
        recontent = re.findall("= '(.+?)'", content)
        return recontent[1]
    else:
        if (type == 'mc'):
            head = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
                "Host": "api.1suplayer.me",
                "Referer": firstUrl + SecUrl
            }
            u = 'https://api.1suplayer.me/player/?userID=&type=%s&vkey=%s' % (type, vKey)
            res = requests.get(u, headers=head)
            html = etree.HTML(res.content)
            content = html.xpath('/html/body/script/text()')[0]
            recontent = re.findall(" = '(.+?)'", content)
            payload = {
                "type": recontent[3],
                "vkey": recontent[4],
                "ckey": 'recontent[2]',
                "userID": "",
                "userIP": recontent[0],
                "refres": 1,
                "my_url": firstUrl + SecUrl + '.html'
            }
            return GetDownloadUrl(payload, u)
        else:

            url = 'http://www.dililitv.com/player/api.php'
            res = requests.post(url, data={'type': type, 'v': vKey}, headers=heads)
            link = 'http://www.dililitv.com' + json.loads(res.content)['url']
            respon = requests.get(link)
            return respon.text.split('\n')[2]


@app.route('/hot', methods=['GET'])
def movies():
    url = 'https://91mjw.com/alltop_hit'
    if (redis.exists(url)):
        return jsonify(json.loads(redis.get(url)))
    else:
        req = requests.get(url, headers=headers).text
        html = etree.HTML(req)
        articles = html.xpath('/html/body/section/div/div/div/div/article')
        movies = []
        for article in articles:
            movies.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
        redis.set(url, json.dumps(movies), ex=60 * 120)
        return jsonify(movies)


@app.route('/moviehot', methods=['GET'])
def movie_hot():
    url = 'http://www.dililitv.com/'
    if (redis.exists(url + 'hot')):
        return jsonify(json.loads(redis.get(url)))
    else:
        req = requests.get(url, headers=headers).text
        html = etree.HTML(req)
        articles = html.xpath('/html/body/section/aside/div[3]/div/a')
        hots = []
        for article in articles:
            hots.append({'id': str(article.xpath('@href')[0]),
                         'name': article.xpath('text()')[0]})
        redis.set(url + 'hot', json.dumps(hots), ex=60 * 120)
        return jsonify(hots)


@app.route('/movies/<string:id>', methods=['GET'])
def movie(id):
    result = []
    url = ''
    if id.isdigit():
        url = 'http://www.dililitv.com/gresource/' + id
    else:
        url = 'https://91mjw.com/video/' + id
    if (redis.exists(url)):
        return jsonify(json.loads(redis.get(url)))
    else:
        req = requests.get(url, headers=headers).text
        html = etree.HTML(req)
        str = ''
        t = html.xpath('/html/body/section/div/div/div/article/div[1]/div[2]/text()')
        for i, strong in enumerate(html.xpath('/html/body/section/div/div/div/article/div[1]/div[2]/strong')):
            str += strong.xpath('text()')[0] + t[i * 2] + '\n'

        result.append(str)
        jis = []
        for i in html.xpath('//*[@id="video_list_li"]/div/a'):
            jis.append({i.xpath('@id')[0]: i.xpath('text()')[0]})
        result.append(jis)
        desc = html.xpath('/html/body/section/div/div/div/article/p[1]/span/text()')
        result.append(''.join(desc))
        imgs = []
        for i in html.xpath('/html/body/section/div/div/div/article/p[2]/img'):
            imgs.append(i.xpath('@data-original')[0])
        result.append(imgs)
        redis.set(url, json.dumps(result), ex=60 * 120)
        return jsonify(result)


@app.route('/movies/<string:type>/<string:id>', methods=['GET'])
def movieUrl(type, id):
    url = ''
    domain = ''
    rule = ''
    if (type == 'tv'):
        url = 'https://91mjw.com/vplay/' + id + '.html'
        domain = 'https://91mjw.com/vplay/'

        rule = 1
    else:
        url = 'http://www.dililitv.com/vplay/' + id
        domain = 'http://www.dililitv.com/vplay/'
        rule = 2
    if (redis.exists(url)):
        return jsonify(json.loads(redis.get(url)))
    else:
        link = GetVkeyParam(domain, id, rule)
        redis.set(url, json.dumps(link))
    return jsonify(link)


@app.route('/movies/<string:word>/search/<int:page>/<string:type>', methods=['GET'])
def movieSearch(word, page, type):
    url = ''
    if type == 'tv':
        url = 'https://91mjw.com/page/%s?s=%s' % (page, word)
    else:
        url = 'http://www.dililitv.com/page/%s?s=%s' % (page, word)
    if (redis.exists(url)):
        return jsonify(json.loads(redis.get(url)))
    else:
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            try:
                html = etree.HTML(req.text)
                articles = html.xpath('//article[@class="u-movie"]')
                movies = []
                for article in articles:
                    try:
                        movies.append({'cover': article.xpath('a/div/img/@data-original')[0],
                                       'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                                       'name': article.xpath('a/h2/text()')[0]})
                    except Exception as err:
                        logger.error(err)
                redis.set(url, json.dumps(movies[:-3]), ex=60 * 120)
                return jsonify(movies[:-3])
            except Exception as err:
                logger.error(err)


        else:
            return


@app.route('/index', methods=['GET'])
def index():
    res = []
    url = 'https://91mjw.com/'
    if redis.exists(url):
        return jsonify(json.loads(redis.get(url)))
    else:
        req = requests.get(url, headers=headers)

        if req.status_code == 200:
            html = etree.HTML(req.text)
            tj = []
            for i in html.xpath('//*[@id="slider"]/div/div'):
                tj.append({'cover': i.xpath('a/img/@src')[0],
                           'id': str(i.xpath('a/@href')[0]).split('/')[-1], 'name': i.xpath('a/span/text()')[0]})

            res.append(tj)
            ev_up = []
            for article in html.xpath('/html/body/section/div/div/div[4]/article'):
                ev_up.append({'cover': article.xpath('a/div/img/@data-original')[0],
                              'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                              'name': article.xpath('a/h2/text()')[0]})
            res.append(ev_up)
            zx = []
            for article in html.xpath('/html/body/section/div/div/div[5]/article'):
                zx.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(zx)
            kh = []
            for article in html.xpath('/html/body/section/div/div/div[6]/article'):
                kh.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(kh)
            kb = []
            for article in html.xpath('/html/body/section/div/div/div[7]/article'):
                kb.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(kb)
            xj = []
            for article in html.xpath('/html/body/section/div/div/div[8]/article'):
                xj.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(xj)
            jq = []
            for article in html.xpath('/html/body/section/div/div/div[9]/article'):
                jq.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(jq)
            redis.set(url, json.dumps(res), ex=60 * 60 * 24)
            return jsonify(res)
        else:
            return


@app.route('/movies/category/<string:cate>/page/<int:page>', methods=['GET'])
def get_by_cate(cate, page):
    url = ''
    if (str(cate).startswith('list')):
        url = 'http://www.dililitv.com/film/'
    else:
        url = 'https://91mjw.com/category/all_mj/'
    if page == 0:
        url += cate
    else:
        url = 'https://91mjw.com/category/all_mj/%s/page/%s' % (cate, page + 1)
    if redis.exists(url):
        return jsonify(json.loads(redis.get(url)))
    else:
        res = requests.get(url)
        html = etree.HTML(res.content)
        res = getList(html)
        redis.set(url, json.dumps(res), ex=60 * 60 * 24)
        return jsonify(res)


@app.route('/index/movie', methods=['GET'])
def idx_movie():
    res = []
    url = 'http://www.dililitv.com/'
    if redis.exists(url):
        return jsonify(json.loads(redis.get(url)))
    else:
        req = requests.get(url, headers=headers)

        if req.status_code == 200:
            html = etree.HTML(req.text)
            tj = []

            for i in html.xpath('//*[@id="slider"]/div/div'):
                tj.append({'cover': i.xpath('a/img/@src')[0],
                           'id': str(i.xpath('a/@href')[0]).split('/')[-1], 'name': i.xpath('a/span/text()')[0]})

            res.append(tj)
            rank = []
            for i in html.xpath('/html/body/section/div/div/div[3]/div/div[4]/article'):
                rank.append({'cover': i.xpath('a/div/img/@src')[0],
                             'id': str(i.xpath('a/@href')[0]).split('/')[-1], 'name': i.xpath('a/h2/text()')[0]})
            res.append(rank)
            rb = []

            for i in html.xpath('/html/body/section/div/div/div[4]/div/div[3]/article'):
                rb.append({'cover': i.xpath('a/div/img/@src')[0],
                           'id': str(i.xpath('a/@href')[0]).split('/')[-1], 'name': i.xpath('a/h2/text()')[0]})
            res.append(rb)
            res.append(rank)
            ev_up = []

            for article in html.xpath('/html/body/section/div/div/div[5]/article'):
                ev_up.append({'cover': article.xpath('a/div/img/@data-original')[0],
                              'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                              'name': article.xpath('a/h2/text()')[0]})
            res.append(ev_up)
            zx = []
            for article in html.xpath('/html/body/section/div/div/div[6]/article'):
                zx.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(zx)
            kh = []
            for article in html.xpath('/html/body/section/div/div/div[7]/article'):
                kh.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(kh)
            kb = []
            for article in html.xpath('/html/body/section/div/div/div[8]/article'):
                kb.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(kb)
            xj = []
            for article in html.xpath('/html/body/section/div/div/div[9]/article'):
                xj.append({'cover': article.xpath('a/div/img/@data-original')[0],
                           'id': str(article.xpath('a/@href')[0]).split('/')[-1],
                           'name': article.xpath('a/h2/text()')[0]})
            res.append(xj)
            redis.set(url, json.dumps(res), ex=60 * 60 * 24)
            return jsonify(res)
        else:
            return


@app.route('/book/search/<string:word>/<string:page>', methods=['GET'])
def book_search(word, page):
    domain = 'https://www.biquge.com'
    url = "https://www.biquge.com/searchbook.php?keyword=%s&page=%s" % (word, page)
    html = getHTML(url)
    divs = html.xpath('//*[@id="hotcontent"]/div/div')
    books = []
    for div in divs:
        books.append({
            "Id": str(div.xpath('div/a/@href')[0]).split('/')[1],
            "Img": domain + div.xpath('div/a/img/@src')[0],
            "Author": str(div.xpath('dl/dt/span/text()')[0]).strip(),
            "Name": str(div.xpath('dl/dt/a/text()')[0]).strip(),
            "Desc": str(div.xpath('dl/dd/text()')[0]).strip()
        })
    result = {
        "code": 200,
        "msg": "操作成功",
        "data": books
    }
    return json.dumps(result, ensure_ascii=False)


@app.route('/book/detail/<string:word>', methods=['GET'])
def get_detail(word):
    parse_book_detail(word)
    return ""



@app.route('/book/chapter', methods=['GET'])
def get_chapter():
    url = request.args.get("url")
    html = getHTMLUtf8(url)
    content = ""
    if url.__contains__("xbiquge"):
        return get_c(html)
    else:
        while True:
            content += get_c(html)
            next_text = html.xpath('//*[@id="container"]/div/div/div[2]/div[3]/a[3]/text()')[0]
            html = getHTMLUtf8(
                "https://www.266ks.com/" + html.xpath('//*[@id="container"]/div/div/div[2]/div[3]/a[3]/@href')[0])
            if next_text != "下一页":
                break

    return content


def freshIdx():
    cates = [
        'kehuanpian',
        'juqingpian',
        'dongzuopian',
        'xijupian',
        'donghuapian',
        'qihuanpian',
        'kongbupian',
        'xuanyipian',
        'jilupian',
        'zhenrenxiu'
    ]
    for cate in cates:
        url = 'https://91mjw.com/category/all_mj/' + cate
        if redis.exists(url):
            redis.delete(url)

        res = requests.get(url)
        html = etree.HTML(res.content)
        res = getList(html)
        redis.set(url, json.dumps(res), ex=60 * 60 * 24)
    cate1 = [
        'list01',
        'list02',
        'list03',
        'list04',
        'list05',
        'list06',
    ]
    for i in cate1:
        url = 'http://www.dililitv.com/film/' + i
        if redis.exists(url):
            redis.delete(url)
        res = requests.get(url)
        html = etree.HTML(res.content)
        res = getList(html)
        redis.set(url, json.dumps(res), ex=60 * 60 * 24)


def parse_book_detail(id):
    url = "https://www.biquge.com/" + id + "/"
    selector = getHTML(url)
    book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content")[0]
    author = selector.xpath("//meta[@property='og:novel:author']/@content")[0]
    cover = selector.xpath("//meta[@property='og:image']/@content")[0]
    category = selector.xpath("//meta[@property='og:novel:category']/@content")[0]
    update_time = selector.xpath("//meta[@property='og:novel:update_time']/@content")[0]
    status = selector.xpath("//meta[@property='og:novel:status']/@content")[0]

    # latest_chapter_url = selector.xpath('//*[@id="info"]/p[4]/a/@href')[0]
    book_desc = selector.xpath("//meta[@property='og:description']/@content")[0]
    latest_chapter_name = selector.xpath(
        "//meta[@property='og:novel:latest_chapter_name']/@content")[0]

    book = {"link": url,
            "_id": id,
            "cover": cover,
            "hot": 0,
            'book_name': str(book_name).strip(),
            'author': str(author).strip(),
            'category': category,
            'status': status,
            'book_desc': book_desc,
            "u_time": update_time,
            'last_chapter': latest_chapter_name}
    bookDB.insert_one(dict(book))
    t1 = threading.Thread(target=gert_score, args=(book_name, id, author))

    t1.start()
    chapters = []
    for dd in selector.xpath('//*[@id="list"]/dl/dt[2]/following-sibling::*'):
        if len(dd.xpath('a/@href')) > 0:
            name = dd.xpath('a/text()')[0]
            s = dd.xpath('a/@href')[0]
            chapter = {
                'book_id': id,
                'link': 'https://www.biquge.com' + s,
                'chapter_name': name}
            chapters.append(chapter)
    if len(chapters) > 0:
        chapterDB.insert_many(chapters)
    return requests.get("https://book.leetomlee.xyz/v1/book/detail/" + id).text

def getHTMLUtf8(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html
def gert_score(name, id, author):
    url = "https://www.qidian.com/search?kw=%s" % name

    html = getHTMLUtf8(url)
    lis = html.xpath("//*[@id='result-list']/div/ul/li")
    for li in lis:
        bookInfoUrl = "https:" + li.xpath("div/a/@href")[0]
        bookImgUrl = "https:" + li.xpath('div/a/img/@src')[0]
        bookNames = li.xpath("div[2]/h4/a/text()")
        if len(bookNames) == 0:
            bookNames = li.xpath("div[2]/h4/a/cite/text()")
            if len(bookNames) == 0:
                continue
        bookName = bookNames[0]
        bookAuthor = li.xpath("div[2]/p[1]/a[1]/text()")[0]
        bookStatus = li.xpath("div[2]/p/span/text()")[0]
        if str(name).__contains__(bookName) and author == bookAuthor:
            u = 'https://book.qidian.com/ajax/comment/index?_csrfToken=VyDQJGV3vLqNzMY8pduwEYAAfT1tla9d0A67VoII&bookId=' + str(
                bookInfoUrl.split('/')[-1]) + '&pageSize=15'
            res = requests.get(u).text
            rate = json.loads(res)['data']['rate']
            if not str(rate).__contains__('.'):
                rate = float(str(rate) + '.0')

            myquery = {"_id": id}
            newvalues = {"$set": {"cover": bookImgUrl, "status": bookStatus, "rate": rate}}
            bookDB.update_one(myquery, newvalues)


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    # get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(port=8082, host='0.0.0.0')
