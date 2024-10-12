import json
from pathlib import Path
from typing import Optional

from httpx import ConnectError, TimeoutException
from httpx._types import ProxiesTypes
from loguru import logger

from .info import get_info
from .data import fetch


def make(table: dict, pool: dict):
    """生成卡池信息"""
    for name, rarity in table.items():
        if rarity == 6:
            if name in pool["up_six_list"]:
                continue
            pool["operators"]["六"].append(name)
        elif rarity == 5:
            if name in pool["up_five_list"]:
                continue
            pool["operators"]["五"].append(name)
        elif rarity == 4:
            if name in pool["up_four_list"]:
                continue
            pool["operators"]["四"].append(name)


async def generate(file: Path, proxy: Optional[ProxiesTypes] = None):
    try:
        response = await get_info(proxy)
    except (TimeoutException, ConnectError, ValueError) as e:
        logger.warning(f"明日方舟 获取公告出错: {type(e)}({e})\n请检查网络或代理设置")
        return
    pool = {
        "name": response.title,
        "six_per": 0.5,
        "five_per": 0.5,
        "four_per": 0.2,
        "up_limit": [],
        "up_alert_limit": [],
        "up_five_list": [],
        "up_six_list": [],
        "up_four_list": [],
        "operators": {
            "三": [
                "空爆",
                "克洛丝",
                "史都华德",
                "炎熔",
                "香草",
                "翎羽",
                "芬",
                "玫兰莎",
                "月见夜",
                "泡普卡",
                "卡缇",
                "米格鲁",
                "斑点",
                "安赛尔",
                "芙蓉",
                "梓兰",
            ],
            "四": [],
            "五": [],
            "六": [],
        },
    }
    for char in response.six_chars:
        if char.limit:
            if not pool["up_limit"]:
                pool["up_limit"].append(char.name)
            else:
                pool["up_alert_limit"].append(char.name)
                continue
        else:
            pool["up_six_list"].append(char.name)
        pool["six_per"] = char.chance
    for char in response.five_chars:
        pool["up_five_list"].append(char.name)
        pool["five_per"] = char.chance
    for char in response.four_chars:
        pool["up_four_list"].append(char.name)
        pool["four_per"] = char.chance
    try:
        table = await fetch(proxy)
    except (TimeoutException, ConnectError):
        tablefile = Path(__file__).parent.parent / "resource" / "gacha" / "rarity_table.json"
        if tablefile.exists():
            with tablefile.open("r", encoding="utf-8") as f:
                table = json.load(f)
        else:
            logger.warning("明日方舟 获取卡池干员出错\n请检查网络或代理设置")
            return
    make(table, pool)
    with file.open("w+", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    logger.info(f"明日方舟 卡池信息已更新: {response.title}")
    return response
