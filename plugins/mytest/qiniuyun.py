import os, requests
from qiniu import Auth, BucketManager, put_data, etag
from nonebot.log import logger
from datetime import datetime
import random

access_key = 'EgF6Sbkv9DYDjEn4VDCQ9xbcKP5WNsFGBaSrMCxI'
secret_key = 'dqveqGHIRONtsSQ47V1WeTtAV7jY_LcKHjN2zv9C'
bucket_domain = 'picsheet.nekoki.top'
bucket_name = 'picsheet'
prefix = 'pic/'

def getPic() :
    # 图片名称key列表
    key_name_list = []

    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)

    # 列举指定前缀的文件列表
    ret, eof, info = bucket.list(bucket_name, prefix=prefix)
    if ret is not None and len(ret['items']) > 0:
        # 打印出所有文件的key
        i = 0
        for item in ret['items']:
            # 动态列表要用append赋值
            key_name_list.append(item['key'])
            i += 1

    else:
        print('no files in the folder')

    choice_key = random.choice(key_name_list)
    random_img_url = 'http://%s/%s' % (bucket_domain, choice_key)
    logger.info('抽到的图片URL：' + random_img_url)
    return random_img_url


def pushPic(url:str) :

    q = Auth(access_key, secret_key)
    
    data = requests.get(url).content

            #文件名
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg" 
    key = f'pic/{filename}'

    token = q.upload_token(bucket_name, key)
    ret, info = put_data(token, key, data)
    upload_key = ret['key']
    logger.info(f'图片{upload_key}已上传到{bucket_name}空间中')