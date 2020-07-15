import requests
import re
from PIL import Image
import urllib
import configparser
import base64
import json

config=configparser.ConfigParser()
config.read('config.ini')
user = config['account']['User']
password = config['account']['Password']

while True:
    # 海淀教堂公众号的每日灵听或者主日礼拜链接地址
    url = input("请输入文章链接：")
    # 要作为封面图片的图片链接
    imgurl = input("请输入图片链接：")

    # 获取文章整个html
    response = requests.get(url)
    html=str(response.content,'utf-8')

    # 获取公众号文章名字
    title = re.findall('<meta property="og:title" content="(.*?)"', html, re.DOTALL)[0]

    # 获取牧师名字和证道题目
    if('每日灵听' in title):
        biaoti = re.findall(r'牧师\ ?：(.*?)\| 每日灵听', title)[0]

        if('】' in title):
            mushi = re.findall('】(.*?)牧师', title)[0]
        else:
            mushi = re.findall('(.*?)牧师', title)[0]
        
    elif('主日礼拜' in title):
        title = title.replace(' ', '')
        biaoti = re.findall(r'牧师\：(.*)', title)[0]
        mushi = re.findall(r'音视频\|(.*?)牧师', title)[0]
        
    print(mushi)
    
    
    
    riqi = re.findall('",s="(.*?)";', html)[0][2:]

    zhengdaotimu = riqi + '|' + mushi +'：' + biaoti
    print(zhengdaotimu)  

    # 把远程图片存到本地，命名为test.png
    urllib.request.urlretrieve(imgurl, "test.png")

    # 把本地图片resize为375*250，并以日期命名
    im = Image.open("test.png")
    im_resized = im.resize((375, 250))
    filename = riqi + ".png"
    im_resized.save(filename)
    with open(filename, "rb") as image_file:
        filestring = base64.b64encode(image_file.read())
    filepath = "public://sermon/202007/" + filename
    url_file = 'http://www.hdchurch.org/hds/file.json'
    fileimg = {'file[filepath]': filepath, 'file[file]': filestring, 'file[filename]': filename}
    r_file = requests.post(url_file, data=fileimg, auth=(user, password))
    result = json.loads(r_file.text)
    fid = result['fid']

    preacher = input("如果牧师名字错误，请重新输入：")
    if preacher == '':
        preacher = mushi
    title_zhengdao = input("如果证道题目错误，请重新输入：")
    if title_zhengdao == '':
        title_zhengdao = zhengdaotimu
    body = input("请输入body内容：")
    audio_link = input("请输入audio_link：")
    video_link = input("请输入video_link：")

    url_node = 'http://www.hdchurch.org/hds/node'
    node = {'type':'sermon', 'title': title_zhengdao, "body":{"und":{"0":{"value": body}}}, "field_preacher":{"und": preacher}, "field_audio_link":{"und":{"0":{"url": audio_link}}}, "field_video_link":{"und":{"0":{"url": video_link}}}, "field_cover_image":{"und":{"0":{"fid": fid}}}, 'status': None, 'promote': '1'}
    r = requests.post(url_node, json=node, auth=(user, password))
    print(r.text)
