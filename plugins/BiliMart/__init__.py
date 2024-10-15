import re

from nonebot.adapters import Message
from nonebot.adapters import Event
from nonebot.internal.params import ArgPlainText, Arg
from nonebot.log import default_format
from nonebot.params import CommandArg, Received, LastReceived

from nonebot import on_command, logger

mc_biliMart = on_command("bilimart")

@mc_biliMart.handle()
async def _(args: Message = CommandArg()):
    if para := args.extract_plain_text():
        await mc_biliMart.finish(f"关键字{para}");


@mc_biliMart.got("keyword", prompt="给我一个关键字")
async def _(keyword: str = ArgPlainText()):
    logger.add("keyword=" + keyword, level="DEBUG", format=default_format, rotation="1 week")
    if not re.fullmatch(r'[\u4e00-\u9fff]+', keyword):
        await mc_biliMart.reject("只能输入中文哦")


@mc_biliMart.got("max_money", prompt="最大金额是多少呢")
async def _(max_money: str = ArgPlainText()):
    logger.add("max_money=" + max_money, level="DEBUG", format=default_format, rotation="1 week")
    if not re.fullmatch(r'[0-9]+', max_money):
        await mc_biliMart.reject("只能输入数字哦")


@mc_biliMart.receive()
async def receive_func(event: Event = LastReceived()):
    if event.get_type() == "message":
        await mc_biliMart.reject("戳我一下")
    await mc_biliMart.finish("Roger~")