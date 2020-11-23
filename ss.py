import re

import requests
from lxml import etree


def getHTML(url):
    get = requests.get(url)
    get.encoding = "utf-8"
    html = etree.HTML(get.text)
    return html


if __name__ == '__main__':
    html = getHTML('https://www.yousxs.com/player/19967_2.html')
    scripts = html.xpath('//script')
    skey = scripts[1].text
    skey=str(skey).split("'")[1]
    print(skey)

    url = str(scripts[6].text)
    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2})).*?=', url)
    mp3link=urls[0]+skey



    print(mp3link)
