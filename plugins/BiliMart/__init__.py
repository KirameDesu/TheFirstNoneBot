import re
import argparse
import shlex
from logging import lastResort

from nonebot.adapters import Message
from nonebot.adapters import Event
from nonebot.internal.params import ArgPlainText, Arg
from nonebot.log import default_format
from nonebot.params import CommandArg, Received, LastReceived
from nonebot.matcher import Matcher

from nonebot import on_command, logger
from starlette.config import undefined

from plugins.BiliMart.bilimart import get_match_items_str, append_keyword, set_min_price, set_max_price, set_bot_matcher

pattern1 = r'--minprice\s+\d+(\.\d+)?\s*--maxprice\s+\d+(\.\d+)?\s*(--keyword\s+.+\s*)?$'
pattern2 = r'123123'

'''
响应信息定义
'''
mc_biliMart = on_command("bilimart")


@mc_biliMart.handle()
async def _(marcher: Matcher, args: Message = CommandArg()):
    set_bot_matcher(marcher)
    if para := args.extract_plain_text():
        if para == "go":
            # await mc_biliMart.finish(f"关键字{para}");
            await mc_biliMart.finish(get_match_items_str())
        else:
            try:
                args = parse_command_line(para)
                if args.keyword:
                    await mc_biliMart.send("开始搜索~关键字为\"" + str(args.keyword) + "\"")
                else:
                    await mc_biliMart.send(f"准备更新数据库~金额范围为{args.minprice}到{args.maxprice}")
                # BiliMart搜索主程序
                matched_str = do_bilimart(args.minprice, args.maxprice, args.keyword)
                if matched_str != "":
                    await mc_biliMart.finish(matched_str)
                else:
                    await mc_biliMart.finish("什么都没有找到哦")
            except ValueError:
                await mc_biliMart.finish("这是不被识别的指令格式哦")
            except AttributeError:
                await mc_biliMart.finish("参数错了哦")


@mc_biliMart.got("keyword", prompt="给我一个关键字")
async def _(keyword: str = ArgPlainText()):
    logger.info("keyword=" + keyword)
    if not re.fullmatch(r'[\u4e00-\u9fff]+', keyword):
        await mc_biliMart.reject("只能输入中文哦")


@mc_biliMart.got("min_money", prompt="最小金额是多少呢")
async def _(min_money: str = ArgPlainText()):
    logger.info("max_money=" + min_money)
    if not re.fullmatch(r'[0-9]+', min_money):
        await mc_biliMart.reject("只能输入数字哦")


@mc_biliMart.got("max_money", prompt="最大金额是多少呢")
async def _(matcher: Matcher, max_money: str = ArgPlainText()):
    logger.info("max_money=" + max_money)
    if not re.fullmatch(r'[0-9]+', max_money):
        await mc_biliMart.reject("只能输入数字哦")
    else:
        minp = matcher.get_arg("min_money", default=0)
        maxp = matcher.get_arg("max_money", default=1500)
        kw = matcher.get_arg("keyword", default="")
        await mc_biliMart.finish(await do_bilimart(minp, maxp, kw))


def do_bilimart(min_price: float, max_price: float, keyword: str) -> str:
    set_min_price(min_price)
    set_max_price(max_price)
    append_keyword(keyword)
    logger.info(f"开始查询最小金额{min_price},最大金额{max_price},关键词\"{keyword}\"的商品...")
    try:
        item_str = get_match_items_str()
        return item_str
    except ValueError as e:
        logger.error(f"爬取函数执行出错--{e}")
        return ""


# @mc_biliMart.receive()
# async def receive_func(event: Event = LastReceived()):
#     if event.get_type() == "message":
#         await mc_biliMart.reject("戳我一下")
#     await mc_biliMart.finish("Roger~")


def normal_search(input_str):
    # 将输入字符串转换为适合 argparse 的格式
    args_list = shlex.split(input_str)

    parser = argparse.ArgumentParser(description='Parse command line arguments for min price, max price, and keyword.')
    parser.add_argument('--minprice', type=float, help='Minimum price', required=True)
    parser.add_argument('--maxprice', type=float, help='Maximum price', required=True)
    parser.add_argument('--keyword', type=str, help='Keyword', required=False)

    # 解析参数
    args = parser.parse_args(args_list)
    return args



def parse_command_line(input_str):
    # 检查输入字符串是否包含所需的参数
    if re.match(pattern1, input_str.strip()):
        args = normal_search(input_str)
    # if re.match(pattern2, input_str.strip()):
    #     arg = undefined_search(input_str)
    else:
        raise ValueError("Wrong Command Input.")

    return args
