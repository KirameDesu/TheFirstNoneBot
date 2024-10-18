import re
import argparse
import shlex

from nonebot.adapters import Message
from nonebot.internal.params import ArgPlainText, Arg
from nonebot.params import CommandArg, Received, LastReceived
from nonebot.matcher import Matcher

from nonebot import on_command, logger

from plugins.BiliMart.bilimart import update_database, append_keyword, set_min_price, set_max_price, \
    set_bot_matcher, bilimart, update, get

pattern1 = r'--minprice\s+\d+(\.\d+)?\s*--maxprice\s+\d+(\.\d+)?\s*(--keyword\s+.+\s*)?$'
pattern2 = r'123123'

'''
响应信息定义
'''
mc_biliMart = on_command("bilimart")
mc_biliMart_update_db = on_command("bilimart update")
mc_biliMart_require_db = on_command("bilimart get")


#=============================================================
#                  指令-----"/bilimart"
#=============================================================
@mc_biliMart.got("keyword", prompt="给我一个关键字")
async def _(keyword: str = ArgPlainText()):
    logger.info("keyword=" + keyword)
    if not re.fullmatch(r'[\u4e00-\u9fff]+', keyword):
        await mc_biliMart_update_db.reject("只能输入中文哦")


@mc_biliMart.got("min_money", prompt="最小金额是多少呢")
async def _(min_money: str = ArgPlainText()):
    logger.info("max_money=" + min_money)
    if not re.fullmatch(r'[0-9]+', min_money):
        await mc_biliMart_update_db.reject("只能输入数字哦")


@mc_biliMart.got("max_money", prompt="最大金额是多少呢")
async def _(matcher: Matcher, max_money: str = ArgPlainText()):
    logger.info("max_money=" + max_money)
    if not re.fullmatch(r'[0-9]+', max_money):
        await mc_biliMart_update_db.reject("只能输入数字哦")
    else:
        minp = matcher.get_arg("min_money", default=0)
        maxp = matcher.get_arg("max_money", default=1500)
        kw = matcher.get_arg("keyword", default="")
        await mc_biliMart_update_db.finish(update(minp, maxp, kw))


#=============================================================
#                  指令-----"/bilimart update"
#=============================================================
@mc_biliMart_update_db.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    set_bot_matcher(matcher)
    if para := args.extract_plain_text():
        if para == "go":
            await mc_biliMart_update_db.finish(update_database())
        else:
            try:
                parse_args = parse_command_line(para)
                if parse_args.keyword:
                    # await mc_biliMart_update_db.send("开始搜索关键字为\"" + str(parse_args.keyword) + "\"的商品")
                    await mc_biliMart_update_db.finish("这种指令暂时被屏蔽了哦")
                else:
                    await mc_biliMart_update_db.send(f"准备更新数据库~金额范围为{parse_args.minprice}到{parse_args.maxprice}")
                try:
                    # BiliMart搜索主程序
                    matched_str = update(parse_args.minprice, parse_args.maxprice, parse_args.keyword)
                    await mc_biliMart_update_db.finish(matched_str)
                except ValueError as e:
                    await mc_biliMart_update_db.finish("ERROR<" + str(e) + ">")
            except ValueError:
                await mc_biliMart_update_db.finish("这是不被识别的指令格式哦")
            except AttributeError:
                await mc_biliMart_update_db.finish("参数错了哦")


#=============================================================
#                  指令-----"/bilimart get"
#=============================================================
@mc_biliMart_require_db.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    set_bot_matcher(matcher)
    try:
        parse_args = parse_command_line(args.extract_plain_text())
        if parse_args.keyword:
            await mc_biliMart_update_db.send("开始搜索关键字为\"" + str(parse_args.keyword) + "\"的商品")
        else:
            await mc_biliMart_update_db.finish(f"要给个关键字哦, 例如--keyword '关键字'")
        try:
            # BiliMart搜索主程序
            matched_str = get(parse_args.minprice, parse_args.maxprice, parse_args.keyword)
            await mc_biliMart_update_db.finish(matched_str)
        except ValueError as e:
            await mc_biliMart_update_db.finish("ERROR<" + str(e) + ">")
    except ValueError:
        await mc_biliMart_update_db.finish("这是不被识别的指令格式哦")
    except AttributeError:
        await mc_biliMart_update_db.finish("参数错了哦")


#=============================================================
#                       Handle Function
#=============================================================


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
