import json
from pathlib import Path
from typing import List, Optional

import httpx
from httpx._types import ProxiesTypes
from loguru import logger
from lxml import etree


async def get_prts_pool_info(pinfo: dict, proxy: Optional[ProxiesTypes] = None):
    """获取prts中的卡池信息"""
    prts_url = "https://prts.wiki/w/%E5%8D%A1%E6%B1%A0%E4%B8%80%E8%A7%88/%E9%99%90%E6%97%B6%E5%AF%BB%E8%AE%BF"
    async with httpx.AsyncClient(verify=False, proxies=proxy) as client:
        prts_res = (await client.get(prts_url)).text
        root = etree.HTML(prts_res, etree.HTMLParser())
        # 限定
        group_type_tables: List[etree._Element] = root.xpath(
            "//table[@class='wikitable mw-collapsible fullline logo']"
        )
        group_types = [1, 0]  # is_exclusive
        for g_type, type_div in zip(group_types, group_type_tables):
            trs: List[etree._Element] = type_div.getchildren()[0].getchildren()
            for tr in trs[1:]:
                if not (td := tr.getchildren()):
                    continue
                td0: etree._Element = td[0]
                if (a_elem := td0.find("a", None)) is not None:
                    pname = a_elem.get("title").strip().strip("寻访模拟/")
                    pinfo[pname] = {"is_exclusive": bool(g_type)}
        return pinfo


async def generate(file: Path, proxy: Optional[ProxiesTypes] = None):
    """更新卡池信息"""
    pool_info = {
        "all": {"is_exclusive": False},
        "常驻标准寻访": {"is_exclusive": False},
        "专属推荐干员寻访": {"is_exclusive": True},
        "专属推荐干员": {"is_exclusive": True},
        "中坚寻访": {"is_exclusive": True},
        "中坚甄选": {"is_exclusive": True},
    }
    if file.exists():
        with file.open("r", encoding="utf-8") as fj:
            pool_info.update(json.load(fj))
    # 从prts获取卡池信息
    try:
        await get_prts_pool_info(pool_info, proxy)
    except (httpx.ConnectError, httpx.TimeoutException):
        logger.warning("明日方舟 拉取卡池列表出错\n请检查网络或代理设置")
    with file.open("w+", encoding="utf-8") as fj:
        json.dump(pool_info, fj, ensure_ascii=False, indent=2)
    logger.info("卡池信息更新完成")
