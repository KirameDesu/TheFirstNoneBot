import datetime
import json

reply_normal_list = [
    "我不到呀",
    "希娜奶",
    "我不知道",
    "无可奉告"
]

reply_ok_list = [
    "雀食",
    "是嘛",
    "真的嘛",
    "阔以",
    "确实",
    "可以"
]


data_dir = "./linuxbot/plugins/mytest/time_data/"


def write():  # 写入CD时间
    with open(data_dir + "cd.json", "w", encoding="utf-8") as f:
        CD = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dict = {
            "CD": str(CD)
        }
        json.dump(dict, f, indent=4)
