import logging  # 引入logging模块
import random
import re
import uuid

logging.basicConfig(level=logging.INFO)  # 设置日志级别

import requests
from lxml import etree

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
import pymongo

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["xbiquge"]
chapterDB = mydb["xchapter"]
site_pre = 'https://www.xbiquge.cc/book'
domain = 'https://www.xsbiquge.com'


# bookNameAndAuthors = []
# find = bookDB.find({}, {"book_name": 1, "author": 1})


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    if get.status_code != 200:
        return
    get.encoding = "utf8"
    html = etree.HTML(get.text)
    return html


def getBook(u):
    selector = getHTML(u)
    uid = str(uuid.uuid4())
    id = ''.join(uid.split('-'))
    # if ids.__contains__(id):
    #     return

    book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content")[0]
    author = selector.xpath("//meta[@property='og:novel:author']/@content")[0]
    cover = selector.xpath("//meta[@property='og:image']/@content")[0]
    category = selector.xpath("//meta[@property='og:novel:category']/@content")[0]
    # status = selector.xpath("//meta[@property='og:novel:status']/@content")[0]
    update_time = str(selector.xpath('//*[@id="info"]/p[3]/text()')[0]).split("[")[0].strip()
    latest_chapter_name = selector.xpath(
        '//*[@id="info"]/p[4]/a/text()')[0]
    # latest_chapter_url = selector.xpath('//*[@id="info"]/p[4]/a/@href')[0]
    book_desc = selector.xpath("//meta[@property='og:description']/@content")[0]
    # key = book_name + author
    # if bookNameAndAuthors.__contains__(key):
    #     logging.info("db exist book %s" % book_name)
    #     return
    book = {"_id": id,
            "link": u,
            "cover": cover,
            "hot": 0,
            'book_name': str(book_name).strip(),
            'author': str(author).strip(),
            'category': category,
            'status': "连载中",
            'book_desc': book_desc,
            "u_time": update_time[5:],
            'last_chapter': latest_chapter_name}
    # book.add_value('last_chapter_id', str(latest_chapter_url).split('/')[-1].split('.')[0])
    try:
        bookDB.insert_one(dict(book))
    except Exception as e:
        logging.error(e)

    chapters = []
    for dd in selector.xpath("//*[@id='list']/dl/dd"):
        try:
            if len(dd.xpath('a/@href')) > 0:
                s = dd.xpath('a/@href')[0]
                name = dd.xpath('a/text()')[0]
                chapter = {
                    'book_id': id,
                    'chapter_id': id + str(s).split('/')[-1].split('.')[0],
                    'content': getContent(s),
                    'chapter_name': name}
                chapters.append(chapter)
        except Exception as e:
            logging.error(e + "dsfdsfs")
    if len(chapters) > 0:
        try:
            chapterDB.insert_many(chapters)
        except Exception as e:
            logging.error(e)
    logging.info("cc new add %s" % book_name)


def getContent(s):
    ss = []
    # zhmodel = re.compile(u'[\u4e00-\u9fa5]')
    content = getHTML(domain + s).xpath("//*[@id='content']/text()")

    for i in content:
        if str(i).strip() == "":
            continue
        # match = zhmodel.search(i)
        # if not match:
        #     print(i)
        #     continue

        ss.append(i)

    return "\n".join(ss)


if __name__ == '__main__':
    getBook("https://www.xsbiquge.com/85_85235/")

    # f = bookDB.find({"book_name": "龙族5悼亡者的归来（龙族Ⅴ：悼亡者的归来）"}, {'_id': 1})
    # for i in f:
    #     book_id = i['_id']
    #     chapterDB.delete_many({"book_id": book_id})
    #     bookDB.delete_many({"_id": book_id})
#     cps = chapterDB.find({"book_id": book_id}, {"content": 1, "chapter_name": 1, "_id": 1})
#     for cp in cps:
#         cid = cp["_id"]
#         u = cp["content"]
#         chapter_name = cp["chapter_name"]
#
#         if str(u).strip() == '':
#             continue
#         html = getHTML(u)
#         #     html=getHTML(i['content'])
#         content = "\n".join(getHTML(u).xpath("//*[@id='content']/text()"))
#         myquery = {"_id": cid}
#         newvalues = {
#             "$set": {"content": content}}
#
#         chapterDB.update_one(myquery, newvalues)
#         print(content)

# try:
#     for f in find:
#         try:
#             bookNameAndAuthors.append(f["book_name"] + f["author"])
#         except Exception as e:
#             continue
#             logging.error(e)
#     for i in range(1, 100000):
#         link = site_pre + '/%s/' % str(i)
#         getBook(link)
#         logging.info("get %s success" % link)
# except Exception as e:
#     logging.error(e)

# with ThreadPoolExecutor() as t:
#     job_list = []
#     for i in range(1, 200001):
#         link = site_pre + '/%s/' % str(i)
#         logging.info(link)
#         job_list.append(t.submit(getBook, link))
#     for future in as_completed(job_list):
#         data = future.result()
#         logging.info("get %s success" % link)
