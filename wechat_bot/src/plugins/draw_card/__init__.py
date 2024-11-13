import os
import asyncio
import schedule
import traceback
from pathlib import Path
from cn2an import cn2an
from dataclasses import dataclass
from typing import Optional, Set

from on import on_regex
from common import send_text, send_image, run_async_task
from .handles.azur_handle import AzurHandle
from .handles.ba_handle import BaHandle
from .handles.base_handle import BaseHandle
from .handles.fgo_handle import FgoHandle
from .handles.genshin_handle import GenshinHandle
from .handles.guardian_handle import GuardianHandle
from .handles.onmyoji_handle import OnmyojiHandle
from .handles.pcr_handle import PcrHandle
from .handles.pretty_handle import PrettyHandle
from .handles.prts_handle import PrtsHandle


base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
help_file = os.path.join(base_path, "help.png")


@on_regex("^抽卡帮助$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    await send_image(room_id, help_file)


@dataclass
class Game:
    keywords: Set[str]
    handle: BaseHandle
    flag: bool
    config_name: str
    max_count: int = 300  # 一次最大抽卡数
    reload_time: Optional[int] = None  # 重载UP池时间（小时）
    has_other_pool: bool = False


games = (
    Game(
        {"azur", "碧蓝航线"},
        AzurHandle(),
        True,
        "AZUR_FLAG",
    ),
    Game(
        {"fgo", "命运冠位指定"},
        FgoHandle(),
        True,
        "FGO_FLAG",
    ),
    Game(
        {"genshin", "原神"},
        GenshinHandle(),
        True,
        "GENSHIN_FLAG",
        max_count=300,
        reload_time=18,
        has_other_pool=True,
    ),
    Game(
        {"guardian", "坎公骑冠剑"},
        GuardianHandle(),
        True,
        "GUARDIAN_FLAG",
        reload_time=4,
    ),
    Game(
        {"onmyoji", "阴阳师"},
        OnmyojiHandle(),
        True,
        "ONMYOJI_FLAG",
    ),
    Game(
        {"pcr", "公主连结", "公主连接", "公主链接", "公主焊接"},
        PcrHandle(),
        True,
        "PCR_FLAG",
    ),
    Game(
        {"pretty", "马娘", "赛马娘"},
        PrettyHandle(),
        True,
        "PRETTY_FLAG",
        max_count=200,
        reload_time=4,
    ),
    Game(
        {"prts", "方舟", "明日方舟"},
        PrtsHandle(),
        True,
        "PRTS_FLAG",
        reload_time=4,
    ),
    Game(
        {"ba", "碧蓝档案"},
        BaHandle(),
        True,
        "BA_FLAG",
    ),
)


def draw_handler(game, draw_regex):
    @on_regex(draw_regex)
    async def _(**kwargs):
        match_obj = kwargs.get("match_obj")
        room_id = kwargs.get("room_id")
        sender = kwargs.get("sender")
        sender_name = kwargs.get("sender_name")
        pool_name, pool_type_, num, unit = match_obj.groups()
        if num == "单":
            num = 1
        else:
            try:
                num = int(cn2an(num, mode="smart"))
            except ValueError:
                await send_text("必！须！是！数！字！", room_id, sender, sender_name)
                return
        if unit == "井":
            num *= game.max_count
        if num < 1:
            await send_text("虚空抽卡？？？", room_id, sender, sender_name)
        elif num > game.max_count:
            await send_text("一井都满不足不了你嘛！快爬开！", room_id, sender, sender_name)
        pool_name = (
            pool_name.replace("池", "")
            .replace("武器", "arms")
            .replace("角色", "char")
            .replace("卡牌", "card")
            .replace("卡", "card")
        )
        try:
            if pool_type_ in ["2池", "二池"]:
                pool_name = pool_name + "1"
            img_bytes, msg = game.handle.draw(num, pool_name=pool_name, user_id=sender)
            if img_bytes:
                img_png = os.path.join(img_path, sender + "_card.png")
                with open(img_png, "wb") as f:
                    f.write(img_bytes)
                await send_image(room_id, img_png)
            await send_text(msg, room_id)
        except:
            print(traceback.format_exc())
            await send_text("出错了...", room_id, sender, sender_name)


def reset_handler(game, reset_regex):
    @on_regex(reset_regex)
    async def _(**kwargs):
        room_id = kwargs.get("room_id")
        sender = kwargs.get("sender")
        sender_name = kwargs.get("sender_name")
        if game.handle.reset_count(sender):
            await send_text("重置成功！", room_id, sender, sender_name)


def create_matchers():
    for game in games:
        pool_pattern = r"([^\s单0-9零一二三四五六七八九百十]{0,3})"
        num_pattern = r"(单|[0-9零一二三四五六七八九百十]{1,3})"
        unit_pattern = r"([抽|井|连])"
        pool_type = "()"
        if game.has_other_pool:
            pool_type = r"([2二]池)?"
        draw_regex = r".*?(?:{})\s*{}\s*{}\s*{}\s*{}".format(
            "|".join(game.keywords), pool_pattern, pool_type, num_pattern, unit_pattern
        )
        draw_handler(game, draw_regex)
        for keyword in game.keywords:
            reset_regex = f"^重置{keyword}抽卡$"
            reset_handler(game, reset_regex)


create_matchers()


async def first_collect():
    for game in games:
        if game.flag:
            game.handle.init_data()
    schedule.cancel_job(job)


job = schedule.every(1).seconds.do(run_async_task(first_collect))
