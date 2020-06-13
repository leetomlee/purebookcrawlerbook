# -*- coding: utf-8 -*-
import datetime
import random
import time
from concurrent.futures.process import ProcessPoolExecutor

import pymongo
# client = pymongo.MongoClient(host='192.168.3.9')
import requests
from lxml import etree
from redis import StrictRedis

ex = ProcessPoolExecutor()
redis = StrictRedis(host='120.27.244.128', port=6379, db=0, password='zx222lx')
myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
book = mydb["xbiquge"]
accountDB = mydb["account"]
chapterDB = mydb["xchapter"]
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
site = 'http://www.xbiquge.la'

import logging  # 引入logging模块

logging.basicConfig(level=logging.INFO)  # 设置日志级别


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


def update_book_state():
    find = book.find({}, {"_id": 1, "u_time": 1})
    nowTime_str = datetime.datetime.now().strftime('%Y-%m-%d')
    e_time = time.mktime(time.strptime(nowTime_str, "%Y-%m-%d"))

    for f in find:
        u_time = f["u_time"]
        id = f["_id"]
        if str(u_time).__contains__("最后更新"):
            u_time = u_time[5:]
        u_time = u_time[:10]
        try:
            s_time = time.mktime(time.strptime(u_time, '%Y-%m-%d'))

            # 日期转化为int比较
            diff = int(e_time) - int(s_time)

            if diff >= 60 * 60 * 24 * 30 * 3:
                logging.info("相差大于三个月 %s" % u_time)
                myquery = {"_id": id}
                newvalues = {
                    "$set": {"status": "完结"}}

                book.update_one(myquery, newvalues)
            else:
                continue

        except Exception as e:
            logging.error("update error %s" % u_time)


def get_books_from_db():
    sort = [('hot', 1)]
    # find = book.find({}, {"_id": 1}).sort(sort)
    # find = book.find({"hot": 0}, {"_id": 1, "hot": 1, "link": 1})
    # find = book.find({}, {"_id": 1, "link": 1})
    find = book.find({"hot": {"$gt": 0}, "status": {"$ne": "完结"}}, {"_id": 1, "link": 1})
    # find = book.find({"hot": {"$gt": 0}}, {"_id": 1, "link": 1})
    for f in find:
        #     print(f["status"])
        # chapterDB.delete_many({"book_id": f["_id"]})

        # updateBook(f["_id"], f["link"])
        ex.submit(updateBook, f["_id"], f["link"])
    ex.shutdown(wait=True)


def get_chapter_content(url):
    html = getHTML(url)
    content = ""
    for f in html.xpath("//*[@id='content']/text()"):
        if f != "" and f != "," and f != "\r":
            content += f
    return content


def updateBook(id, url):
    logging.info("start update  " + url)
    html = getHTML(url)
    ids = []
    chps = chapterDB.find({"book_id": id}, {"chapter_id": 1})
    for chp in chps:
        ids.append(chp["chapter_id"])
    chapters = []
    newcids = []
    for dd in html.xpath("//*[@id='list']/dl/dd"):
        if len(dd.xpath('a/@href')) > 0:
            try:
                s = dd.xpath('a/@href')[0]
                name = dd.xpath('a/text()')[0]
                split = str(s).split('/')

                cid = id + split[-1].split('.')[0]
                if ids.__contains__(cid):
                    continue
                newcids.append(cid)
                chapter = {
                    'book_id': id,
                    'chapter_id': cid,
                    'content': site + s,
                    'chapter_name': name}
                chapters.append(chapter)
            except Exception as e:
                logging.error(e)
                continue
    # logging.info("new add  " + str(len(chapters)))
    try:
        if len(chapters) != 0:
            many = chapterDB.insert_many(chapters)
            for x in many.inserted_ids:
                try:
                    requests.get("https://newbook.leetomlee.xyz/v1/book/chapter/" + str(x))
                except Exception as e:
                    logging.error(e)
            logging.info("new add  " + str(len(many.inserted_ids)))

            update_time = html.xpath('//*[@id="info"]/p[3]/text()')[0]
            latest_chapter_name = html.xpath('//*[@id="info"]/p[4]/a/text()')[0]

            myquery = {"_id": id}
            newvalues = {
                "$set": {"u_time": update_time, "last_chapter": latest_chapter_name}}

            book.update_one(myquery, newvalues)
            logging.info("book info update " + str(id))
    except Exception as e:
        logging.error(e)
    # 邮件发送库


import smtplib
# 邮件的标题
# 邮件的正文
from email.mime.text import MIMEText


def send_mail(user, pwd, sender, receiver, content, title):
    # 邮箱服务器主机名
    mail_host = "smtp.163.com"
    # 创建邮件对象
    message = MIMEText(content, "plain", "utf-8")

    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = title

    # 启动ssl发送邮件
    smtp_obj = smtplib.SMTP_SSL(mail_host, 465)

    smtp_obj.login(user, pwd)  # 登录

    smtp_obj.sendmail(sender, receiver, message.as_string())

    print("发送成功！")


# if __name__ == '__main__':
#     # update_book_state()
#     get_books_from_db()
# if __name__ == "__main__":
#     user = "18736262687@163.com"  # 用户名
#     pwd = "lx11427"  # 客户端授权码
#     sender = user
#
#     fs = accountDB.find({"email": {"$regex": ".*@.*"}}, {"email": 1})
#     for f in fs:
#         recevier = f["email"]
#         content = "欢迎使用DeerBook,加交流联系群,防走失,App更新,信息公告"
#         title = "Account Ack,Do Not Reply"
#
#         send_mail(user, pwd, sender, recevier, content, title)

if __name__ == '__main__':
    # get_books_from_db()
    stime = datetime.datetime.now()
    logging.info("all update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    get_books_from_db()
    logging.info("end update  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    etime = datetime.datetime.now()
    logging.info("used_time  " + str((etime - stime).seconds))
# find = chapterDB.find({"content": {"$regex": "看最快更新无错小说.*"}}, {"content": 1, "_id": 1})
# for f in find:
#     chapterDB.delete_one({"_id": f["_id"]})
#     # print(f["content"])
# #     if str(f['content']).startswith('http'):
# get_chapter_content("http://www.xbiquge.la/26/26874/23129742.html")
