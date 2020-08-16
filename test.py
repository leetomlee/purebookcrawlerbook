import datetime
import logging
import random
import time

import pymongo
import requests
from lxml import etree
from scrapy import Selector

from demo3.items import CommonItemLoader, Book

myclient = pymongo.MongoClient('mongodb://lx:Lx123456@120.27.244.128:27017/')
mydb = myclient["book"]
bookDB = mydb["xbiquge"]
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


def getHTML(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    # html = etree.HTML(get.text)
    # return html
    parse_book_to_db(get)


site = 'http://www.xbiquge.la'


def parse_book_to_db(response):
    url__split = str(response.url).split('/')
    book_id = url__split[-2] + url__split[-3]

    selector = Selector(response=response)
    book_name = selector.xpath("//meta[@property='og:novel:book_name']/@content").extract_first()
    author = selector.xpath("//meta[@property='og:novel:author']/@content").extract_first()

    cover = selector.xpath("//meta[@property='og:image']/@content").extract_first()
    category = selector.xpath("//meta[@property='og:novel:category']/@content").extract_first()
    # status = selector.xpath("//meta[@property='og:novel:status']/@content").extract_first()
    update_time = selector.xpath('//*[@id="info"]/p[3]/text()').extract_first()
    latest_chapter_name = selector.xpath(
        '//*[@id="info"]/p[4]/a/text()').extract_first()
    latest_chapter_url = selector.xpath('//*[@id="info"]/p[4]/a/@href').extract_first()
    book_desc = selector.xpath("//meta[@property='og:description']/@content").extract_first()

    book = CommonItemLoader(item=Book(), response=response)
    book.add_value("_id", book_id)
    book.add_value("link", response.url)
    book.add_value("cover", cover)
    book.add_value("hot", 0)
    book.add_value('book_name', str(book_name).strip())
    book.add_value('author', str(author).strip())
    book.add_value('category', category)
    book.add_value('status', calc_book_state(update_time))
    book.add_value('book_desc', book_desc)
    book.add_value("u_time", update_time[5:])
    book.add_value('last_chapter', latest_chapter_name)
    book.add_value('last_chapter_id', str(latest_chapter_url).split('/')[-1].split('.')[0])
    item = book.load_item()
    bookDB.insert_one(dict(item))
    chapters = []
    for dd in selector.xpath("//*[@id='list']/dl/dd"):
        if len(dd.xpath('a/@href')) > 0:
            s = dd.xpath('a/@href').extract_first()
            name = dd.xpath('a/text()').extract_first()
            split = str(s).split('/')
            cid = book_id + str(split[-1]).split('.')[0]
            chapter = {
                'book_id': book_id,
                'chapter_id': cid,
                'content': site + s,
                'chapter_name': name}
            chapters.append(chapter)
    if len(chapters) > 0:
        chapterDB.insert_many(chapters)


def calc_book_state(u_time):
    nowTime_str = datetime.datetime.now().strftime('%Y-%m-%d')
    e_time = time.mktime(time.strptime(nowTime_str, "%Y-%m-%d"))
    if str(u_time).__contains__("最后更新"):
        u_time = u_time[5:]
    u_time = u_time[:10]
    try:
        s_time = time.mktime(time.strptime(u_time, '%Y-%m-%d'))

        # 日期转化为int比较
        diff = int(e_time) - int(s_time)

        if diff >= 60 * 60 * 24 * 30 * 3:
            return "完结"
        return "连载中"
    except Exception as e:
        logging.error(e)
    return "连载中"


def getHTMLUtf8(url):
    get = requests.get(url, headers={"User-Agent": random.choice(user_agent_list)})
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


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


def get_content(url):
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


def get_c(html):
    content = ""
    for text in html.xpath('//*[@id="content"]/text()'):
        if not str(text).strip() == "":
            if not str(text).startswith("\n"):
                if is_chinese(str(text)):
                    content += "\t\t\t\t\t\t\t\t" + str(text).strip() + "\n"
    return content


if __name__ == '__main__':
    # content = get_content("https://www.266ks.com/8_8975/5558978.html")
    # content = get_content("http://www.xbiquge.la/15/15977/8321996.html")
    # print(content)
    a=[1,2,3,45]
    a.reverse()
    print(a)
