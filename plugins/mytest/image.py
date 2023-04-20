import os
from . import config
from .config import image_config
from nonebot.log import logger


def image_rename(image_sort: str):
    path = image_config.image_path / image_sort
    # print(image_config.image_path / image_sort)

    filelist = os.listdir(path)
    filelist.sort(key=lambda x: int(x[:-4]))
    # total_num = len(filelist)
    i = 0
    for item in filelist:
        if item.endswith('.jpg'):
            src = os.path.join(os.path.abspath(path), item)
            dst = os.path.join(os.path.abspath(path), str(i)+'.jpg')
            try:
                os.rename(src, dst)
                i += 1
            except:
                i += 1
                continue
        # if item.endswith('.png'):
        #     src = os.path.join(os.path.abspath(path), item)
        #     dst = os.path.join(os.path.abspath(path), ''+str(i)+'.jpg')
        #     try:
        #         os.rename(src, dst)
        #         i += 1
        #     except:
        #         continue

        # if item.endswith('.jpg'):
        #     src = os.path.join(os.path.abspath(path), item)
        #     dst = os.path.join(os.path.abspath(path), ''+str(i)+'.jpg')
        #     try:
        #         os.rename(src, dst)
        #         i += 1
        #     except:
        #         continue

        # if item.endswith('.bpm'):
        #     src = os.path.join(os.path.abspath(path), item)
        #     dst = os.path.join(os.path.abspath(path), ''+str(i)+'.jpg')
        #     try:
        #         os.rename(src, dst)
        #         i += 1
        #     except:
        #         continue
    logger.success("排序命名完成")


# 返回image_sort类图片文件夹的图片数目
def image_count(image_sort: str):
    filenum = 0
    for file in os.listdir(image_config.image_path / image_sort):
        if file.endswith((".jpg", ".bpm", ".png")):
            filenum += 1
    logger.info(image_sort + "有" + f"{filenum}" + "张图片")

    return filenum
