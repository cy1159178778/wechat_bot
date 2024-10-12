import os
import re
import random
import asyncio
import traceback
import itertools
from io import BytesIO
from typing import List, Optional, Tuple
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .drawer import draw_life, save_jpg
from .life import Life, PerAgeProperty, PerAgeResult
from .property import Summary
from .talent import Talent


base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
sender_state_dict = {}


@on_regex(r"^(人生重开|人生重来|人生重开模拟器)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    life_ = Life()
    life_.load()
    talents = life_.rand_talents(10)
    state = dict()
    sender_state_dict[sender] = state
    state["life"] = life_
    state["talents"] = talents
    msg = "请发送天赋+3个编号选择天赋，如“天赋 0 1 2”，或发送“天赋随机”随机选择"
    des = "\n".join([f"[{t.color}]{i}.{t}" for i, t in enumerate(talents)])
    await send_text(f"{msg}\n\n{des}", room_id, sender, sender_name)


def conflict_talents(talents: List[Talent]) -> Optional[Tuple[Talent, Talent]]:
    for t1, t2 in itertools.combinations(talents, 2):
        if t1.exclusive_with(t2):
            return t1, t2
    return None


@on_regex(r"^天赋\s*(.+)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    state = sender_state_dict.get(sender)
    if not state:
        return

    life_: Life = state["life"]
    talents: List[Talent] = state["talents"]

    reply = match_obj.groups()[-1]
    match = re.fullmatch(r"\s*(\d)\s*(\d)\s*(\d)\s*", reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        nums.sort()
        if nums[-1] >= 10:
            await send_text("请发送正确的编号", room_id, sender, sender_name)
            return

        talents_selected = [talents[n] for n in nums]
        ts = conflict_talents(talents_selected)
        if ts:
            await send_text(f"你选择的天赋“{ts[0].name}”和“{ts[1].name}”不能同时拥有，请重新选择", room_id, sender, sender_name)
            return
    elif "随机" in reply:
        while True:
            nums = random.sample(range(10), 3)
            nums.sort()
            talents_selected = [talents[n] for n in nums]
            if not conflict_talents(talents_selected):
                break
    elif re.fullmatch(r"[\d\s]+", reply):
        await send_text("请发送正确的编号，如“0 1 2”", room_id, sender, sender_name)
        return
    else:
        sender_state_dict.pop(sender)
        await send_text("天赋编号错误，人生重开已取消", room_id, sender, sender_name)
        return

    life_.set_talents(talents_selected)
    state["talents_selected"] = talents_selected

    msg = (
        "请发送属性+4个数字分配“颜值、智力、体质、家境”4个属性，"
        "如“属性 5 5 5 5”，或发送“属性随机”随机选择；"
        f"可用属性点为{life_.total_property()}，每个属性不能超过10"
    )
    await send_text(msg, room_id, sender, sender_name)


@on_regex(r"^属性\s*(.+)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    state = sender_state_dict.get(sender)
    if not state:
        return

    life_: Life = state["life"]
    talents: List[Talent] = state["talents_selected"]
    total_prop = life_.total_property()

    reply = match_obj.groups()[-1]
    match = re.fullmatch(r"\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*", reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        if sum(nums) != total_prop:
            await send_text(f"属性之和需为{total_prop}，请重新发送", room_id, sender, sender_name)
            return
        elif max(nums) > 10:
            await send_text("每个属性不能超过10，请重新发送", room_id, sender, sender_name)
            return
    elif "随机" in reply:
        half_prop1 = int(total_prop / 2)
        half_prop2 = total_prop - half_prop1
        num1 = random.randint(0, half_prop1)
        num2 = random.randint(0, half_prop2)
        nums = [num1, num2, half_prop1 - num1, half_prop2 - num2]
        random.shuffle(nums)
    elif re.fullmatch(r"[\d\s]+", reply):
        await send_text("请发送正确的数字，如“5 5 5 5”", room_id, sender, sender_name)
        return
    else:
        sender_state_dict.pop(sender)
        await send_text("属性点错误，人生重开已取消", room_id, sender, sender_name)
        return

    prop = {"CHR": nums[0], "INT": nums[1], "STR": nums[2], "MNY": nums[3]}
    life_.apply_property(prop)

    # await send_text("你的人生正在重开...", room_id, sender, sender_name)

    init_prop = life_.get_property()
    results = list(life_.run())
    summary = life_.gen_summary()

    try:
        img_io = await asyncio.get_event_loop().run_in_executor(None, get_life_img, talents, init_prop, results, summary)
        img_png = os.path.join(img_path, sender + "_remake.png")
        with open(img_png, "wb") as f:
            f.write(img_io.getvalue())
        await send_image(room_id, img_png)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        await send_text("出现未知错误，你的人生重开失败（", room_id, sender, sender_name)
    sender_state_dict.pop(sender)


def get_life_img(
    talents: List[Talent],
    init_prop: PerAgeProperty,
    results: List[PerAgeResult],
    summary: Summary,
) -> BytesIO:
    return save_jpg(draw_life(talents, init_prop, results, summary))
