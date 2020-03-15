# -*- coding: utf-8 -*-
import datetime
import random
import smtplib
import time
from concurrent.futures._base import FIRST_COMPLETED, wait
from concurrent.futures.thread import ThreadPoolExecutor
from email.header import Header
from email.mime.text import MIMEText

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from lxml import etree

client = pymongo.MongoClient(host='120.27.244.128')
db = client['book']
book = db['book']
chapterDB = db['chapter']
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
site = 'https://www.biquge.com.cn'

import logging  # 引入logging模块

logging.basicConfig(level=logging.INFO)  # 设置日志级别


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


def get_books_from_db():
    sort = [('_id', -1)]
    # find = book.find({}, {"_id": 1}).sort(sort)
    find = book.find({"status": "连载中"}, {"_id": 1, })
    for f in find:
        # updateBook(f["_id"], "https://www.biquge.com.cn/book/%s/" % f["_id"])
        with ThreadPoolExecutor() as t:
            all_task = [t.submit(updateBook, f["_id"], "https://www.biquge.com.cn/book/%s/" % f["_id"]) for f
                        in
                        find]
            wait(all_task, return_when=FIRST_COMPLETED)


def get_chapter_content(url):
    html = getHTML(url)
    content = "\r\n".join(html.xpath("//*[@id='content']/text()"))
    return content


def updateBook(id, url):
    logging.info("start update  " + url)
    html = getHTML(url)
    ids = []
    chps = chapterDB.find({"book_id": id}, {"chapter_id": 1})
    for chp in chps:
        ids.append(chp["chapter_id"])
    chapters = []
    for dd in html.xpath("//*[@id='list']/dl/dd"):
        if len(dd.xpath('a/@href')) > 0:
            s = dd.xpath('a/@href')[0]
            url = site + s
            name = dd.xpath('a/text()')[0]
            split = str(s).split('/')
            bid = split[2]
            cid = bid + split[3].split('.')[0]
            if ids.__contains__(cid):
                continue
            chapter = {
                'book_id': bid,
                'chapter_id': cid,
                'content': get_chapter_content(url),
                'chapter_name': name}
            chapters.append(chapter)
    # logging.info("new add  " + str(len(chapters)))
    try:
        if len(chapters) != 0:
            many = chapterDB.insert_many(chapters)
            logging.info("new add  " + str(len(many.inserted_ids)))
    except Exception as e:
        logging.error(e)
    ids = []


def send_mail(msg):
    sender = '18736262687@163.com'

    receivers = ['lx_stu@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header("18736262687@163.com", 'utf-8')  # 发送者
    message['To'] = Header("lx_stu@qq.com", 'utf-8')  # 接收者

    subject = '通知'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.163.com', 25)  # 25 为 SMTP 端口号
        smtpObj.login(sender, 'lx11427')
        smtpObj.sendmail(sender, receivers, message.as_string())
        logging.info("邮件发送成功")
    except smtplib.SMTPException as e:
        logging.error(e)
        logging.info("Error: 无法发送邮件")


if __name__ == '__main__':
    # send_mail('也许今天就可以来面试')
    stime = datetime.datetime.now()
    logging.info("all update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    get_books_from_db()
    logging.info("end update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    etime = datetime.datetime.now()
    logging.info("waste_time  " + str((etime - stime).seconds))
