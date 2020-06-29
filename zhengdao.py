import requests
import re
from PIL import Image
import urllib

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
        biaoti = re.findall(r'牧师 .*?：(.*?)\| 每日灵听', title)[0]

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
    im_resized.save(riqi + ".png")