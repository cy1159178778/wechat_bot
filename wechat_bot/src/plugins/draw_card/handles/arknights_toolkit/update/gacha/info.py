import re
from datetime import datetime
from typing import List, Optional

import ujson
from httpx import AsyncClient, TimeoutException
from httpx._types import ProxiesTypes
from loguru import logger
import lxml.etree as etree

from .model import UpdateChar, UpdateInfo


pat = re.compile(r"(.*)(复刻|活动).*?开启")
pat1 = re.compile(r"(.*)寻访.*?开启")
pat2 = re.compile(r"[【】]")
pat3 = re.compile(r"[（：]")
pat4 = re.compile(r"（|）：")
pat5 = re.compile(r"（在.*?以.*?(\d+).*?倍.*?）")
pat6 = re.compile(r"（占.*?的.*?(\d+).*?%）")
pat7 = re.compile(r"(?P<start_m>\d{2})月(?P<start_d>\d{2})日( )?(?P<start_H>\d{2}):(?P<start_M>\d{2}) - (?P<end_m>\d{2})月(?P<end_d>\d{2})日( )?(?P<end_H>\d{2}):(?P<end_M>\d{2})")


def fetch_chars(dom):
    contents = dom.xpath(
        '//p/text() | //p/*/text() | //img[@data-width="1560"]/@src | //img[@class="media-wrap image-wrap"]/@src'
    )
    title = ""
    start = 0
    end = 0
    pool_img = ""
    chars: List[str] = []
    up_chars: List[List[UpdateChar]] = [[], [], []]
    for index, content in enumerate(contents):
        if not start and (match := pat7.search(content)):
            start = int(datetime.now().replace(
                month=int(match["start_m"]),
                day=int(match["start_d"]),
                hour=int(match["start_H"]),
                minute=int(match["start_M"]),
            ).timestamp())
            end = int(datetime.now().replace(
                month=int(match["end_m"]),
                day=int(match["end_d"]),
                hour=int(match["end_H"]),
                minute=int(match["end_M"]),
            ).timestamp())
        if not pat1.search(content):
            continue
        title = pat2.split(content)
        title = f"{title[1]}-{title[-2]}" if len(title) > 3 else title[1]
        lines = [contents[index + _] for _ in range(8)] + [""]
        for idx, line in enumerate(lines):
            """因为 <p> 的诡异排版，所以有了下面的一段"""
            if "★★" in line and "%" in line:
                chars.append(line)
            elif "★★" in line and "%" in lines[idx + 1]:
                chars.append(line + lines[idx + 1])
        pool_img = contents[index - 1]
        r"""两类格式：用/分割，用\分割；★+(概率)+名字，★+名字+(概率)"""
        for char in chars:
            star = char.split("（")[0].count("★")
            name = pat3.split(char)[1] if "★（" not in char else pat4.split(char)[2]
            names = name.replace("\\", "/").split("/")
            for name in names:
                limit = False
                if "[限定]" in name:
                    limit = True
                name = name.replace("[限定]", "").strip()
                zoom = 1.0
                if match := pat5.search(char) or pat6.search(char):
                    zoom = float(match[1])
                    zoom = zoom / 100 if zoom > 10 else zoom
                up_chars[6 - star].append(UpdateChar(name, limit, zoom))
        break  # 这里break会导致个问题：如果一个公告里有两个池子，会漏掉下面的池子，比如 5.19 的定向寻访。但目前我也没啥好想法解决
    return title, start, end, pool_img, up_chars


async def get_info(proxy: Optional[ProxiesTypes] = None):
    async with AsyncClient(verify=False, proxies=proxy) as client:
        result = (await client.get("https://ak.hypergryph.com/news")).text
        if not result:
            logger.warning("明日方舟 获取公告出错")
            raise TimeoutException("未找到明日方舟公告")
        dom = etree.HTML(result.replace("><", ">\n<"), etree.HTMLParser())
        scripts = dom.xpath("//script")
        data = [elem for elem in scripts if elem.text.startswith("self.__next_f.push(")][-1].text[
           len('self.__next_f.push([1,"c:[\\"$\\",\\"$L16\\",null,'):-len(']\n"])') - 1
        ]
        index = ujson.loads(data.replace('\\"', '"'))["initialData"]["ACTIVITY"]["list"]
        infos = []
        for article in index:
            if pat.match(article["title"]):
                activity_url = f"https://ak.hypergryph.com/news/{article['cid']}"
                result = (await client.get(activity_url)).text
                if not result:
                    logger.warning(f"明日方舟 获取公告 {activity_url} 出错")
                    continue

                """因为鹰角的前端太自由了，这里重写了匹配规则以尽可能避免因为前端乱七八糟而导致的重载失败"""
                dom = etree.HTML(result, etree.HTMLParser())
                title, start, end, pool_img, up_chars = fetch_chars(dom)
                if not title or title.startswith("跨年欢庆"):
                    continue
                logger.debug(f"成功获取 当前up信息; 当前up池: {title}")
                infos.append(
                    UpdateInfo(
                        title, start, end, up_chars[2], up_chars[1], up_chars[0], pool_img
                    )
                )
        if infos:
            return sorted(infos, key=lambda x: x.start, reverse=True)[0]
        raise ValueError("未找到明日方舟公告")
