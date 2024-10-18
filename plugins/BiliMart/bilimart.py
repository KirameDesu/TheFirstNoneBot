# ------------------------- Configuration Modification -------------------------

import asyncio
import re
import random
import sqlite3
from typing import Optional

from nonebot import logger
from nonebot.matcher import Matcher
from plugins.BiliMart import database

db = database

db_lock = asyncio.Lock()

# 请填写 Bilibili Cookie 至下方引号内
BILIBILI_COOKIE = "buvid4=5B6A3A11-7A2B-D09D-3DD2-1D8C3DD3F36630667-022120611-hVn2U35PvWhS3UuTmAFR1g%3D%3D; header_theme_version=CLOSE; CURRENT_FNVAL=4048; is-2022-channel=1; buvid_fp_plain=undefined; enable_web_push=DISABLE; hit-dyn-v2=1; PVID=1; CURRENT_QUALITY=64; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; buvid3=C3D2E1D5-0BF2-9DF7-F330-96214E9CC11F60521infoc; b_nut=1725433360; _uuid=E28E1CD4-D6E4-9AB3-9F99-8889B1D65EF760750infoc; fingerprint=7c60a2c8264c8cb61673c5b6fe173a59; buvid_fp=7c60a2c8264c8cb61673c5b6fe173a59; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkyMjYyMDMsImlhdCI6MTcyODk2Njk0MywicGx0IjotMX0.FMlb17C6NkexEfM5FbkWdk0ApgT7iqdxw1EZIWIzERo; bili_ticket_expires=1729226143; SESSDATA=3ef6035b%2C1744519138%2C36012%2Aa2CjAJCHreOILUWylqvjh6Mc8xo__ZQve5Pd0NUgYZ3rj0hLX6kGFUxA6Ds_fz8aXby7YSVnU5SWJxT0h1cFc1QW5uUkx2NHVBdzI3WGFreFdkMzI3R3ZHQ2RfUGxyTEJBdVBtc2lleGlCc1ptUV95UjAtekdoMDRQWjNxdU1kenFIVGozXzA0U0hBIIEC; bili_jct=40ffb5a3a8ba590d957e91d03a73f6c2; DedeUserID=3546779823900918; DedeUserID__ckMd5=3a5547f69f307f08; sid=8fp3bwaf; bsource=search_bing; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; rpdid=0zbfVGpAUa|hSgk3Z8E|1IA|3w1T0ZeJ; deviceFingerprint=4e6d0e71273b181658ce76b5d483db72; kfcFrom=mall_search_mall; from=mall_search_mall; b_lsid=E4E6CD82_19294DCAAB7; bp_t_offset_3546779823900918=988855849843687424; home_feed_column=4; browser_resolution=1060-2329"
# ------------------------------------------------------------------------------

# 魔力赏商品详情网站模板
ITEM_URL = "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId={}&from=market_index"


import colorama
from colorama import Fore, Style
import time
import json
import requests
from datetime import datetime
import os
import pandas as pd

MAX_SEARCH_TIME = 2000

g_cost_min, g_cost_sec = (0, 0)
g_item_cnt = 0
g_min_price = 0
g_max_price = 5000
min_discount = 0
max_discount = 90
category_entry_value = "手办"


class Item:
    def __init__(self, name: str = None, price: float = None, id: str = None):
        self.name = name
        self.price = price
        self.id = id

    def __str__(self):
        return f"Item(Name: {self.name}, Price: {self.price}, ID: {self.id})"


class BiliMart:
    def __init__(self):
        self.min_price = None
        self.max_price = None
        self.min_discount = None
        self.max_discount = None
        self.category = None

        self.keywords: list[str] = []

        self.max_match_time = 4
        self.curr_match_time = 0
        self.match_items: list[Item] = []

        self.curr_search_time = 0

    def add_match_item(self, item: Item):
        self.match_items.append(item)

    def print(self) -> str:
        item_strings = []
        for item in self.match_items:
            item_name, item_id, price, update_time = item
            item_strings.append("{}, 金额{}, url:\"".format(item_name, price) + ITEM_URL.format(item_id) + "\", 更新时间:{}".format(update_time))
        self.match_items.clear()

        return "\n".join(item_strings)

    def reset(self):
        self.curr_search_time = 0
        self.curr_match_time = 0
        self.keywords.clear()


bilimart = BiliMart()
matcher: Optional[Matcher] = None

def crawler():
    global category_eatry, output_dir, showPrice, start_time, g_item_cnt, pause_count, retry_count
    global g_min_price, g_max_price

    mall_url = "https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list"

    # g_min_price = min_price_entry.get() if min_price_entry.get() else "0"
    # g_max_price = max_price_entry.get() if max_price_entry.get() else "5000"
    # min_discount = min_discount_entry.get() if min_discount_entry.get() else "0"
    # max_discount = max_discount_entry.get() if max_discount_entry.get() else "100"

    # 将最低价格和最高价格乘以 100 并格式化为字符串
    setprice = "{}-{}".format(int(float(g_min_price) * 100), int(float(g_max_price) * 100 + 1))
    # 将最低折扣和最高折扣格式化为字符串
    discount = "{}-{}".format(int(min_discount), int(max_discount) + 1)

    # 搜索类别: 手办-2312, 模型-2066, 周边-2331, 3C-2273, 福袋-fudai_cate_id
    id_mapping = {
        "手办": "2312",
        "模型": "2066",
        "周边": "2331",
        "3C": "2273",
        "福袋": "fudai_cate_id"
    }

    # category_entry_value = category_entry.get()
    category_entry_real = category_entry_value.replace("c", "C")
    ID = id_mapping.get(category_entry_real, "")
    item_list = []
    g_item_cnt = pause_count = retry_count = 0
    showPrice = g_min_price
    nextId = None
    start_time = time.perf_counter()

    while True:
        # 结束爬取条件
        if is_to_end_crawler():
            break

        payload = json.dumps({
            "sortType": "PRICE_ASC",
            "priceFilters": [
                str(setprice)
            ],
            "discountFilters": [
                str(discount)
            ],
            "categoryFilter": str(ID),
            "nextId": nextId
        })

        headers = {
            "authority": "mall.bilibili.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "application/json",
            "cookie": f'{BILIBILI_COOKIE}',
            "origin": "https://mall.bilibili.com",
            "referer": "https://mall.bilibili.com/neul-next/index.html?page=magic-market_index",
            "sec-ch-ua": "'Microsoft Edge';v='129', 'Not_A Brand';v='8', 'Chromium';v='129'",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "'Windows'",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

        try:
            response = requests.request("POST", mall_url, headers = headers, data = payload)
            print(response.text)
            response = response.json()
            data = response["data"]["data"]  # 提取一页内的商品信息
            nextId = response["data"]["nextId"]  # 提取进入下一页所需的密钥

            for item in data:
                c2cItemsId = item["c2cItemsId"]
                c2cItemsName = item["c2cItemsName"]
                showPrice = item["showPrice"]
                showMarketPrice = item["showMarketPrice"]
                uname = item["uname"]
                uid = item["uid"]
                item_list.append({
                    "商品编号": c2cItemsId,
                    "商品名称": c2cItemsName,
                    "当前价格": showPrice,
                    "市场价格": showMarketPrice,
                    "卖家名称": uname,
                    "卖家UID": uid
                })
                # 检查商品名称中是否包含关键字
                if bilimart.keywords == [] and is_match_keywords(c2cItemsName):
                    bilimart.add_match_item(Item(c2cItemsName, showPrice, c2cItemsId))
                # 插入数据库
                try:
                    db.insert_item_data(item)
                except sqlite3.IntegrityError as e:
                    logger.log("重复ID" + str(e))

                g_item_cnt += 1
                retry_count = 0

            # if item_count % 300 == 0:
            #     await matcher.send(f"刷新到了{item_count}个商品，正在查找符合关键字的商品中...")

            bilimart.curr_search_time += 1
            time.sleep(random.randint(1,6))
            if nextId is None:
                break
        except (TypeError, KeyError) as e:
            try:
                if response["code"]:
                    if response["code"] == 429:
                        pause_count += 1
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        print(f'{Fore.YELLOW}[Error {response["code"]}] 检测到爬取器触发操作频繁提示, 暂停 30 秒后重试...(¥{showPrice}){Style.RESET_ALL}')
                        # await matcher.send("被检测到频繁操作，只能30s后再拉取了...")
                        information_values_output(0)
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        time_sleep_10ns(3)
                    elif response["code"] == -412:
                        try:
                            print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                            print(f'{Fore.RED}[Error {response["code"]}] 检测到账号已被风控! 请更换 IP 后重试...{Style.RESET_ALL}')
                            print(f'{Fore.YELLOW}[WARN] 从现在起, 爬取器每暂停 60 秒都将重试, 连续失败 5 次后认定爬取失败, 程序自动退出{Style.RESET_ALL}') if retry_count == 0 else ""
                            # await matcher.send("切换为60s拉取一次...")
                            information_values_output(1)
                            print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                            if retry_count < 5:
                                retry_count += 1
                                pause_count += 1
                                time_sleep_10ns(6)
                            else:
                                print(f'{Fore.RED}[WARN] 程序退出时存在未解决的异常, 爬取的商品信息可能不完整!{Style.RESET_ALL}')
                                break
                        except KeyboardInterrupt:
                            except_user_interrupt()
                            break
                    elif response["code"] == 83000004:
                        pause_count += 1
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        print(f'{Fore.YELLOW}[Error {response["code"]}] 检测到在执行 POST 时读取超时, 暂停 5 秒后重试...{Style.RESET_ALL}')
                        information_values_output(0)
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        time_sleep_5s()
                    elif response["code"] == 83001002:
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        print(f'{Fore.RED}[Error {response["code"]}] 检测到 Bilibili Cookie 配置不正确! 请检查后重试...{Style.RESET_ALL}')
                        # await matcher.send("cookie配置有问题了哦")
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        exit()
                    else:
                        except_error_null(response["code"])
                        break
                else:
                    except_error_null(e)
                    break
            except KeyboardInterrupt:
                except_user_interrupt()
                break

        except (requests.exceptions.ProxyError, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            try:
                pause_count += 1
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                print(f'{Fore.YELLOW}[Error Network] 检测到网络环境不稳定, 暂停 5 秒后重试...{Style.RESET_ALL}')
                # await matcher.send("网络环境不稳定, 5秒后再试试...")
                information_values_output(0)
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                time_sleep_5s()
            except KeyboardInterrupt:
                except_user_interrupt()
                break

        except requests.exceptions.JSONDecodeError:
            try:
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                print(f'{Fore.RED}[Error 412] 检测到账号已被风控! 请更换 IP 后重试...{Style.RESET_ALL}')
                # await matcher.send("哦豁!检测到账号已被风控")
                print(f'{Fore.YELLOW}[WARN] 从现在起, 爬取器每暂停 60 秒都将重试, 连续失败 5 次后认定爬取失败, 程序自动退出{Style.RESET_ALL}') if retry_count == 0 else ""
                information_values_output(1)
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                if retry_count < 5:
                    retry_count += 1
                    pause_count += 1
                    time_sleep_10ns(6)
                else:
                    print(f'{Fore.RED}[WARN] 程序退出时存在未解决的异常, 爬取的商品信息可能不完整!{Style.RESET_ALL}')
                    break
            except KeyboardInterrupt:
                except_user_interrupt()
                break

        except KeyboardInterrupt:
            except_user_interrupt()
            break

        except Exception as e:
            except_error_null(e)
            break

    '''
    information_values_output(3)

    # if not os.path.isdir(output_dir):
    #     print(f'{Fore.CYAN}[INFO] 商品信息的保存被取消!{Style.RESET_ALL}')
    #     return

    current_time = datetime.now().strftime("%Y-%m-%d_%H时%M分%S秒")
    file_name = f'{current_time}_{g_min_price}-{g_max_price}元_{int(min_discount) // 10}-{int(max_discount) // 10}折{category_entry_real}.xlsx'
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "xml")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.normpath(os.path.join(output_dir, file_name))

    df = pd.DataFrame(item_list, columns = ["商品编号", "商品名称", "当前价格", "市场价格", "卖家名称", "卖家UID"])
    writer = pd.ExcelWriter(output_file, engine = "xlsxwriter")
    df.to_excel(writer, index = False)
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    worksheet.freeze_panes(1, 0)

    # 标题行格式: 居中对齐, 仿宋, 加粗, 字号12
    header_format = workbook.add_format({"align": "center"})
    header_format.set_font_name("仿宋")
    header_format.set_bold()
    header_format.set_font_size(12)
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # 商品编号列格式: 居中对齐, 列宽15, Times New Roman
    col_format = workbook.add_format()
    col_format.set_align("center")
    col_format.set_font_name("Times New Roman")
    worksheet.set_column("A:A", 15, col_format)

    # 商品名称列格式: 左对齐, 列宽80, 楷体
    col_format = workbook.add_format()
    col_format.set_align("left")
    col_format.set_font_name("楷体")
    worksheet.set_column("B:B", 80, col_format)

    # 卖家名称列格式: 居中对齐, 列宽10, 楷体
    col_format = workbook.add_format()
    col_format.set_align("center")
    col_format.set_font_name("楷体")
    worksheet.set_column("E:E", 10, col_format)

    # 其余列格式: 居中对齐, 列宽10, Times New Roman
    col_format = workbook.add_format()
    col_format.set_align("center")
    col_format.set_font_name("Times New Roman")
    worksheet.set_column("C:D", 10, col_format)
    worksheet.set_column("F:F", 10, col_format)

    writer.close()
    print(f'{Fore.CYAN}[INFO] 商品信息已保存至 {output_file}{Style.RESET_ALL}')
    '''
    pass


def extract_minutes_seconds(interval_time):
    min = int(interval_time // 60)
    sec = int(interval_time % 60)
    return min, sec

def calculate_weighted_progress(showPrice):
    price_distribution = {
        (0, 50): 0.2,
        (50, 100): 0.4,
        (100, 500): 0.25,
        (500, 5000): 0.15
    }
    total_weight = 0

    for price_range, price_weight in price_distribution.items():
        min_price_range, max_price_range = price_range
        if float(showPrice) > max_price_range:
            total_weight += price_weight
        elif min_price_range < float(showPrice) <= max_price_range:
            progress = (float(showPrice) - min_price_range) / (max_price_range - min_price_range)
            return total_weight + progress * price_weight

    return 1.0  # 如果价格超过最高区间，则进度为100%

def information_values_output(tag):
    global g_max_price, showPrice

    g_max_price = str(float(g_max_price) + 1) if g_max_price == g_min_price else g_max_price
    showPrice = str(float(showPrice) + 1) if showPrice == g_min_price else showPrice

    if g_min_price == "0" and g_max_price == "5000":
        progress = calculate_weighted_progress(showPrice)
    else:
        progress = (float(showPrice) - float(g_min_price)) / (float(g_max_price) - float(g_min_price))

    interval_time = time.perf_counter() - start_time
    g_cost_min, g_cost_sec = extract_minutes_seconds(interval_time)
    # remain_min, remain_sec = extract_minutes_seconds(interval_time / progress - interval_time)

    if tag == 0 and g_item_cnt != 0:  # Default 输出
        print(f'{Fore.CYAN}[INFO] 当前为第 {pause_count} 次暂停, 已爬取 {g_item_cnt} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}')
        # print(f'{Fore.GREEN}[INFO] 程序已运行 {min} 分 {sec} 秒, 预计还将运行 {remain_min} 分 {remain_sec} 秒{Style.RESET_ALL}')
    elif tag == 1 and g_item_cnt != 0:  # Error 412 输出
        print(f'{Fore.CYAN}[INFO] 当前为第 {pause_count} 次暂停, 已爬取 {g_item_cnt} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}') if retry_count == 0 else print(f'{Fore.CYAN}[INFO] 当前为第 {retry_count} 次重试, 第 {pause_count} 次暂停, 已爬取 {g_item_cnt} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}')
        # print(f'{Fore.GREEN}[INFO] 程序已运行 {min} 分 {sec} 秒, 预计还将运行 {remain_min} 分 {remain_sec} 秒{Style.RESET_ALL}')
    elif tag == 2 and g_item_cnt != 0:  # KeyboardInterrupt 输出
        print(f'{Fore.CYAN}[INFO] 当前已爬取 {g_item_cnt} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}')
    elif tag == 3:  # DONE 输出
        print(f'{Fore.GREEN}[DONE] 爬取进程结束, 本次在 {g_min_price}-{g_max_price} 元的区间内共爬取到 {g_item_cnt} 件商品, 耗时 {g_cost_min} 分 {g_cost_sec} 秒!{Style.RESET_ALL}')
        exit() if g_item_cnt == 0 else ""

def time_sleep_5s():
    for i in range(5, 0, -1):
        print(f'{Fore.RED}[INFO] 距离重试还剩 {i} 秒...{Style.RESET_ALL}')
        time.sleep(1)
    print(f'{Fore.MAGENTA}[INFO] 开始重新爬取!{Style.RESET_ALL}')

def time_sleep_10ns(n):
    for i in range(n, 0, -1):
        print(f'{Fore.YELLOW}[INFO] 距离重试还剩 {i * 10} 秒...{Style.RESET_ALL}')
        time.sleep(10) if i != 1 else time.sleep(5)
    time_sleep_5s()

def except_user_interrupt():
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
    print(f'{Fore.YELLOW}[WARN] 检测到程序运行被手动中断...{Style.RESET_ALL}')
    information_values_output(2)
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')

def except_error_null(e):
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
    print(f'{Fore.RED}[Error {e}] 检测到未知异常, 程序自动退出...{Style.RESET_ALL}')
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
    print(f'{Fore.RED}[WARN] 程序退出时存在未解决的异常, 爬取的商品信息可能不完整!{Style.RESET_ALL}')


# 跳出爬取数据条件
def is_to_end_crawler()-> bool:
    if bilimart.curr_match_time > bilimart.max_match_time or bilimart.curr_search_time > MAX_SEARCH_TIME :
        return True
    return False

# 判断是否匹配关键字
def is_match_keywords(item_name: str)-> bool:
    for keyword in bilimart.keywords:
        if re.search(keyword, item_name):
            bilimart.curr_match_time += 1
            return True
    return False


def set_bot_matcher(mc: Matcher):
    global matcher
    matcher = mc

def set_min_price(min_price: float):
    bilimart.min_price = min_price

def set_max_price(max_price: float):
    bilimart.max_price = max_price

def append_keyword(keyword: str):
    if keyword != "":
        bilimart.keywords.append(keyword)


def _print_end_tips() -> str:
    if not bilimart.keywords:
        return f"在{bilimart.min_price}到{bilimart.max_price}价格区间共刷新到{g_item_cnt}个商品, 耗时 {g_cost_min} 分 {g_cost_sec} 秒!{Style.RESET_ALL}"

    if not bilimart.match_items:
        return "没有找到关键词为\"" + str("/".join(bilimart.keywords)) + "\"的商品哦"

    return bilimart.print() or "似乎发生了未预见的错误..."


#返回更新数据库的商品信息字符串
def update_database()-> str:
    global g_min_price, g_max_price, min_discount, max_discount, min_discount
    colorama.init(autoreset=True)
    if bilimart.min_price is not None:
        g_min_price = bilimart.min_price
    if bilimart.max_price is not None:
        g_max_price = bilimart.max_price
    if bilimart.min_discount is not None:
        min_discount = bilimart.min_discount
    if bilimart.max_discount is not None:
        max_discount = bilimart.max_discount

    if matcher is None:
        bilimart.reset()
        raise ValueError("matcher 不能为空")

    # 数据库初始化
    db.init()
    # 爬取主函数
    crawler()
    # 程序重置
    bilimart.reset()
    colorama.deinit()

    return _print_end_tips()


def update(min_price: float, max_price: float, keyword: str) -> str:
    set_min_price(min_price)
    set_max_price(max_price)
    append_keyword(keyword)
    logger.info(f"开始查询最小金额{min_price},最大金额{max_price},关键词\"{keyword}\"的商品...")
    try:
        ret_str = update_database()
        return ret_str
    except ValueError as e:
        logger.error(f"更新数据库函数执行出错--{e}")
        raise e


#返回搜索数据库得到的字符串
def require_data_from_db(min_price: float = None, max_price: float = None, keyword: str = "")-> str:
    # 从数据库查找
    bilimart.match_items = db.search_items_by_keyword(min_price, max_price, keyword)
    # 获取结果字符串
    print_end_tips = _print_end_tips()
    # 重置
    bilimart.reset()

    return print_end_tips


def get(min_price: float = None, max_price: float = None, keyword: str = "") -> str:
    if keyword == "":
        return "需要填写关键字哦"
    append_keyword(keyword)

    if min_price is None:
        min_price = db.get_min_show_price()
    if max_price is None:
        max_price = db.get_max_show_price()
    # 根据关键字查询元素
    try:
        ret_str = require_data_from_db(min_price, max_price, keyword)
        return ret_str
    except ValueError as e:
        logger.error(f"查询数据库函数执行出错--{e}")