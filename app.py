#!flask/bin/python
import json
import os
import re
import urllib
from concurrent.futures import ALL_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor

import records
import redis
import requests
from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from lxml import etree


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
        url = 'https://91mjw.com/vplay/' + id+'.html'
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


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(port=8082, host='0.0.0.0')
