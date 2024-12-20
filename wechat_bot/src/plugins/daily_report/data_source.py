import asyncio
import xml.etree.ElementTree
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import httpx
from httpx import Response
from browser import template_to_pic
from zhdate import ZhDate

from .config import (
    REPORT_PATH,
    TEMPLATE_PATH,
    Anime,
    Hitokoto,
    SixData,
    favs_arr,
    favs_list,
)


class AsyncHttpx:

    @classmethod
    async def get(cls, url: str) -> Response:
        async with httpx.AsyncClient() as client:
            return await client.get(url)


def save(data: bytes):
    file_path = REPORT_PATH / f"{datetime.now().date()}.png"
    with open(file_path, "wb") as file:
        file.write(data)


class Report:
    hitokoto_url = "https://v1.hitokoto.cn/?c=a"
    six_url = "https://60s.viki.moe/?v2=1"
    game_url = "https://www.4gamers.com.tw/rss/latest-news"
    bili_url = "https://s.search.bilibili.com/main/hotword"
    it_url = "https://www.ithome.com/rss/"
    anime_url = "https://api.bgm.tv/calendar"

    week = {  # noqa: RUF012
        0: "一",
        1: "二",
        2: "三",
        3: "四",
        4: "五",
        5: "六",
        6: "日",
    }

    @classmethod
    async def get_report_image_afresh(cls) -> str:
        now = datetime.now() - timedelta(hours=9)
        file = REPORT_PATH / f"{now.date()}.png"
        if file.exists():
            file.unlink()
        return await Report.get_report_image()

    @classmethod
    async def get_report_image(cls) -> str:
        """获取数据"""
        now = datetime.now() - timedelta(hours=9)
        file = REPORT_PATH / f"{now.date()}.png"
        if file.exists():
            return str(file)
        zhdata = ZhDate.from_datetime(now)
        result = await asyncio.gather(
            *[
                cls.get_hitokoto(),
                cls.get_bili(),
                cls.get_six(),
                cls.get_anime(),
                cls.get_it(),
            ]
        )
        data = {
            "data_festival": cls.festival_calculation(),
            "data_hitokoto": result[0],
            "data_bili": result[1],
            "data_six": result[2],
            "data_anime": result[3],
            "data_it": result[4],
            "week": cls.week[now.weekday()],
            "date": now.date(),
            "zh_date": zhdata.chinese().split()[0][5:],
        }
        image_bytes = await template_to_pic(
            template_path=str((TEMPLATE_PATH / "mahiro_report").absolute()),
            template_name="main.html",
            templates={"data": data},
            pages={
                "viewport": {"width": 578, "height": 1885},
                "base_url": f"file://{TEMPLATE_PATH}",
            },
            wait=2,
        )
        save(image_bytes)
        return str(file)

    @classmethod
    def festival_calculation(cls) -> list[tuple[str, str]]:
        """计算节日"""
        base_date = datetime(2016, 1, 1)
        n = (datetime.now() - base_date).days
        result = []

        for i in range(0, len(favs_arr), 2):
            if favs_arr[i] >= n:
                result.extend(
                    (favs_arr[i + j] - n, favs_list[favs_arr[i + j + 1]])
                    for j in range(0, 14, 2)
                )
                break
        return result

    @classmethod
    async def get_hitokoto(cls) -> str:
        """获取一言"""
        res = await AsyncHttpx.get(cls.hitokoto_url)
        data = Hitokoto(**res.json())
        return data.hitokoto

    @classmethod
    async def get_bili(cls) -> list[str]:
        """获取哔哩哔哩热搜"""
        res = await AsyncHttpx.get(cls.bili_url)
        data = res.json()
        return [item["keyword"] for item in data["list"]]

    @classmethod
    async def get_six(cls) -> list[str]:
        """获取60s看世界数据"""
        res = await AsyncHttpx.get(cls.six_url)
        data = SixData(**res.json())
        return data.data.news[:11] if len(data.data.news) > 11 else data.data.news

    @classmethod
    async def get_it(cls) -> list[str]:
        """获取it数据"""
        res = await AsyncHttpx.get(cls.it_url)
        root = xml.etree.ElementTree.fromstring(res.text)
        titles = []
        for item in root.findall("./channel/item"):
            title_element = item.find("title")
            if title_element is not None:
                titles.append(title_element.text)
        return titles[:11] if len(titles) > 11 else titles

    @classmethod
    async def get_anime(cls) -> list[tuple[str, str]]:
        """获取动漫数据"""
        res = await AsyncHttpx.get(cls.anime_url)
        data_list = []
        now = datetime.now()
        anime = Anime(**res.json()[now.weekday()])
        data_list.extend((data.name_cn or data.name, data.image) for data in anime.items if data.images)
        return data_list[:8] if len(data_list) > 8 else data_list
