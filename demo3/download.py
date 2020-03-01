import pymysql

# def down_image(url, file_name):
#     global headers
#     req = urllib2.Request(url=url, headers=headers)
#     binary_data = urllib2.urlopen(req).read()
#     temp_file = open(file_name, 'wb')
#     temp_file.write(binary_data)
#     temp_file.close()
import requests

connect = pymysql.connect(host="193.112.113.194", user="root",
                          password="123456789", db="store", port=53306)
cursor = connect.cursor()

cursor.execute("select * from img WHERE DOMAIN ='wxt.sinaimg.cn'")

fetchall = cursor.fetchall()
images = []
# project_dir = os.path.abspath(os.path.dirname(__file__))
# IMAGES_STORE = os.path.join(project_dir, "books")
# imgdown = ImagesPipeline(IMAGES_STORE)
urls = []
for i in fetchall:
    split = str(i[0]).split('/')
    split[3]='mw1024'
    ig='/'.join(str(i) for i in split)
    urls.append(ig)
    print(ig)
i = 0


def saveImge(imgList):
    x = 1
    for imgurl in imgList:
        # 方法一
        # urllib.urlretrieve(imgurl, '%s.jpg' % x)
        # print imgurl

        # 方法二，可定义存储位置
        pic = requests.get(imgurl, timeout=10)
        string = str(x) + '.jpg'
        fp = open(string, 'wb')
        fp.write(pic.content)
        fp.close()

        # 方法三，图片名为url后面的一串
        # path1 = path + str(x)+'--'   #添加数字方便统计
        # save_img(imgurl,path1)

        x += 1


if __name__ == '__main__':
    saveImge(urls)
