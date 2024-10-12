import os.path
import time
import json
import glob
import random
import hashlib
from pathlib import Path

base_path = Path(__file__).parent
fortune: list[dict]
msg_of_day: list[dict]

with open(base_path / "data/fortune.json", "r", encoding="utf-8") as f:
    fortune = json.load(f)["data"]

with open(base_path / "data/msg_of_day.json", "r", encoding="utf-8") as f:
    msg_of_day = json.load(f)["data"]


def get_acg_image():
    file_path = os.path.abspath(r"data\file\sign\*")
    file_list = glob.glob(file_path)
    if not file_list:
        return "https://file.alapi.cn/image/comic/122514-15234207140623.jpg"
    file = random.choice(file_list)
    print("签到图片", file)
    return f"file://{file}"


def get_seed(user_id):
    content = str(user_id)
    sha256_obj = hashlib.md5(content.encode())
    hex_digest = sha256_obj.hexdigest()
    integer_value = int(hex_digest, 16)
    return integer_value


def get_stick(user_id):
    time_day = time.strftime("%Y%m%d", time.localtime())
    seed = int(time_day) + get_seed(user_id)
    random.seed(seed)
    result = random.choice(fortune)
    if "吉" not in result["FORTUNE_SUMMARY"]:
        random.seed(seed + 15)
        result = random.choice(fortune)
    return result


def get_msg(user_id):
    time_day = time.strftime("%Y%m%d", time.localtime())
    seed = int(time_day) + get_seed(user_id)
    random.seed(seed)
    result = random.choice(msg_of_day)
    return result


def get_greet():
    hour = int(time.strftime("%H", time.localtime()))
    if hour in range(0, 6):
        return "凌晨好"
    if hour in range(6, 12):
        return "早上好"
    if hour in range(12, 18):
        return "下午好"
    if hour in range(18, 25):
        return "晚上好"
    return ""
