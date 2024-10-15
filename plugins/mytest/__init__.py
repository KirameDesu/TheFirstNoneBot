from pathlib import Path
from nonebot import on_message, on_regex, load_plugins, on_keyword, on_command
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from nonebot.params import RegexMatched
from nonebot.typing import T_State
from nonebot.params import ArgPlainText, Arg, CommandArg

from aiohttp.client_exceptions import ClientError
import traceback, requests


from .image import image_rename, image_count
import random
from .anti_op import anti_op_list
from .reply import reply_normal_list, reply_ok_list
from .reply import data_dir, write
from . import config
import datetime
import json

from .qiniuyun import getPic, pushPic

group_id_on = config.group_id_on
upload_is_end : bool= True

_sub_plugins = set()
_sub_plugins |= load_plugins(
    str((Path(__file__).parent / "plugins").resolve())
)


mr_sendtext = on_regex(r"傻狗|狗儿子", priority=12)
mr_sendpicture_xx = on_message(rule=to_me(), priority=8, block=False)
# mk_sendpicture_setu = on_keyword({"涩图", "色图", "瑟图"}, priority=5)
mr_sendpicture_setu = on_regex(r"^来.+图$", priority=5)
mr_sendpicture_picOnCloud = on_regex(r"云图|涩图|瑟图|涩涩", priority=7)
mr_pushpicture = on_regex(r"上传", priority=7)
mr_sendmeme_antiop = on_regex(r"(差不多得了|你说的对)?(原神|原批|op|OP)", priority=9)
mr_sendreply_normal = on_keyword( {"什么", "是谁"}, rule=to_me, priority=10, block=False)

# mm_sendreply_ok = on_message(priority=8, block=False)


@mr_sendtext.handle()
async def _(event: GroupMessageEvent, args: str = RegexMatched()):
    gid = str(event.group_id)
    if gid in group_id_on:
        # await bot.send_group_msg(group_id=event.group_id, message=event.raw_message)
        await mr_sendtext.finish(event.raw_message)


@mr_sendpicture_xx.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in group_id_on:
        image_rename("xingxing")
        rand = random.randint(0, image_count("xingxing") - 1)
        logger.info(f"选择第{rand}张图片")
        await mr_sendpicture_xx.finish(MessageSegment.image(f'file:///home/project/LinuxBot/picture/xingxing/{rand}.jpg'))


# @mk_sendpicture_setu.handle()
# async def _(event: GroupMessageEvent):
#     gid = str(event.group_id)
#     if gid in group_id_on:
#         image_rename("setu")
#         rand = random.randint(0, image_count("setu") - 1)
#         logger.info(f"选择第{rand}张图片")
#         await mk_sendpicture_setu.finish(MessageSegment.image(f'file:///home/project/LinuxBot/picture/setu/{rand}.jpg'))


@mr_sendpicture_setu.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in group_id_on:
        image_rename("setu")
        rand = random.randint(0, image_count("setu") - 1)
        logger.info(f"选择第{rand}张图片")
        await mr_sendpicture_setu.finish(MessageSegment.image(f'file:///home/project/LinuxBot/picture/setu/{rand}.jpg'))

#七牛云下载图片
@mr_sendpicture_picOnCloud.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in group_id_on:
       pic_url = getPic()
       await mr_sendpicture_picOnCloud.finish(MessageSegment.image(pic_url))
    
#七牛云上传图片 
@mr_pushpicture.handle()
async def handle_pic(bot: Bot, event: GroupMessageEvent, state: T_State, msg_pic: Message = CommandArg()):
    gid = str(event.group_id)
    if gid in group_id_on:
        if msg_pic:
            state["msg"] = msg_pic
            

@mr_pushpicture.got("msg", prompt="给我图~")
async def get_url(bot: Bot, event: GroupMessageEvent, msg: Message = Arg("msg")) :
    try:
        if msg[0].type == "image":
            url = msg[0].data["url"]  # 图片链接
            pushPic(url)
            await mr_pushpicture.finish("上传成功了喵~")
    except (IndexError, ClientError):
        await bot.send(event, traceback.format_exc())
        await mr_pushpicture.finish("参数错误")
        




@mr_sendmeme_antiop.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in group_id_on and event.user_id == 2099461990:
        rand = random.randint(0, len(anti_op_list) - 1)
        await mr_sendmeme_antiop.finish(MessageSegment.text(anti_op_list[rand]))


@mr_sendreply_normal.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in group_id_on:
        rand = random.randint(0, len(reply_normal_list) - 1)
        await mr_sendreply_normal.finish(MessageSegment.text(reply_normal_list[rand]))


# @mr_sendmeme_toxingxing.handle()
# async def _(event: GroupMessageEvent):
#     gid = str(event.group_id)
#     if gid in group_id_on and event.user_id == 2099461990:
#         with open(data_dir + "cd.json", "r", encoding="utf-8") as f:
#             content = json.load(f)
#         if (not content):
#             write()
#         else:
#             CD = content["CD"]
#             old_CD = datetime.datetime.strptime(CD, "%Y-%m-%d %H:%M:%S")
#             sec = (datetime.datetime.now() - old_CD).seconds  # 剩余CD时间计算
#             if (sec >= 14400):  # CD时长(sec)
#                 write()
#                 image_rename("meme")
#                 rand = random.randint(0, image_count("meme") - 1)
#                 logger.info(f"触发醒醒，选择第{rand}张图片")
#                 await mr_sendmeme_toxingxing.finish(MessageSegment.image(f'file:///home/project/LinuxBot/picture/meme/{rand}.jpg'))
#             else:
#                 # ......
#                 pass

        # # 用到了CD，阔以参考
        # @mm_sendreply_ok.handle()
        # async def _(event: GroupMessageEvent):
        #     if event.group_id == 1095766290:
        #         with open(data_dir + "cd.json", "r", encoding="utf-8") as f:
        #             content = json.load(f)
        #         if (not content):
        #             write()
        #         else:
        #             CD = content["CD"]
        #             old_CD = datetime.datetime.strptime(CD, "%Y-%m-%d %H:%M:%S")
        #             sec = (datetime.datetime.now() - old_CD).seconds  # 剩余CD时间计算
        #             if (sec >= 7200):  # CD时长
        #                 write()
        #                 rand = random.randint(0, len(reply_ok_list) - 1)
        #                 await mm_sendreply_ok.finish(MessageSegment.text(reply_ok_list[rand]))
        #             else:
        #                 # ......
        #                 pass
