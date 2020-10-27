import requests
import re
from PIL import Image
import urllib
import configparser
import base64
import json
from bs4 import BeautifulSoup
import xerox

# config.ini content
# [account]
# User = username
# Password = password
# UrlFile = file_upload_api
# UrlNode = node_update_api

config=configparser.ConfigParser()
config.read('config.ini')
user = config['account']['User']
password = config['account']['Password']
# 文件上传接口
url_file = config['account']['UrlFile']
# 文章上传接口
url_node = config['account']['UrlNode']

while True:
    # 海淀教堂公众号的每日灵听或者主日礼拜链接地址
    url = input("请输入文章链接：")
    
    # 获取文章整个html
    response = requests.get(url)
    html=str(response.content,'utf-8')

    # 获取公众号文章名字
    title = re.findall('<meta property="og:title" content="(.*?)"', html, re.DOTALL)[0]

    # 获取牧师名字和证道题目
    if('每日灵听' in title):
        try:
            biaoti = re.findall(r'[牧师|传道|同工]\ ?：(.*?)\| 每日灵听', title)[0]
        except:
            biaoti = input("证道题目：")

        try:
            if('】' in title):
                mushi = re.findall('】(.*?)[牧师|传道|同工]', title)[0]
            else:
                mushi = re.findall('(.*?)[牧师|传道|同工]', title)[0]
        except:
            mushi = input("证道人名字：")
        
    elif('主日礼拜' in title):
        title = title.replace(' ', '')
        biaoti = re.findall(r'牧师\：(.*)', title)[0]
        mushi = re.findall(r'音视频\|(.*?)牧师', title)[0]
        
    print(mushi)

    # 日期和日期所在的月
    riqi = re.findall('",s="(.*?)";', html)[0][2:]
    day = '20' + riqi
    month = day[0:4]+day[5:7]

    zhengdaotimu = riqi + '|' + mushi +'：' + biaoti
    print(zhengdaotimu)  

    # 从文章中提取所有图片并存成数组
    soup = BeautifulSoup(html, 'html.parser')
    imgs = soup.find_all("img", class_="rich_pages")
    images = []
    for img in imgs:
        images.append(img['data-src'])

    for i in range(len(images)):
        filename = "test" + str(i) + ".png"
        urllib.request.urlretrieve(images[i], filename)
        image = Image.open(filename)
        image.show("title")

    img_no = input("Please choose a image:[0, 1, 2]")
    im = Image.open("test" + img_no + ".png")
    im_resized = im.resize((375, 250))
    filename = riqi + ".png"
    im_resized.save(filename)

    # 通过接口上传图片并获得图片id
    with open(filename, "rb") as image_file:
        filestring = base64.b64encode(image_file.read())
    filepath = "public://sermon/" + month + "/" + filename
    
    fileimg = {'file[filepath]': filepath, 'file[file]': filestring, 'file[filename]': filename}
    r_file = requests.post(url_file, data=fileimg, auth=(user, password))
    result = json.loads(r_file.text)
    fid = result['fid']

    # 证道的各个字段
    preacher = input("如果证道人名字错误，请重新输入：")
    if preacher == '':
        preacher = mushi
    title_zhengdao = input("如果证道题目错误，请重新输入：")
    if title_zhengdao == '':
        title_zhengdao = zhengdaotimu
    
    # 从剪贴板获得证道经文
    body_true = 1
    while body_true:
        body_true = input("如果body内容已经复制，请直接回车，否则请输入0:")
    body = xerox.paste()

    audio_link = input("请输入audio_link：")
    video_link = input("请输入video_link：")

    # 如果状态要设为未发布，则status设成None
    node = {'type':'sermon', 'title': title_zhengdao, "body":{"und":{"0":{"value": body}}}, "field_preacher":{"und": preacher}, "field_audio_link":{"und":{"0":{"url": audio_link}}}, "field_video_link":{"und":{"0":{"url": video_link}}}, "field_cover_image":{"und":{"0":{"fid": fid}}}, 'status': 1, 'promote': '1'}
    r = requests.post(url_node, json=node, auth=(user, password))
    print(r.text)