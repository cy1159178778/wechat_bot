import os
import time
import json
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .utils import get_acg_list, get_acg_info, capture_element_screenshot, get_coordinate_url


base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")


@on_regex(r"^漫展日历\s*(.+)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    city = match_obj.groups()[-1]
    acg_list = await get_acg_list(city_name=city, count=100, order="time")
    start_time = ""
    acg_data = {}
    for acg in acg_list.get("data"):
        if acg.get("start_unix") <= time.time():
            acg["start_time"] = "进行中"
        if start_time != acg.get("start_time"):
            start_time = acg.get("start_time")
            acg_data[start_time] = []
        acg_data[start_time].append(acg)
    if not acg_data:
        await send_text("未找到相关漫展信息", room_id, sender, sender_name)
        return

    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    with open(os.path.join(script_directory, "templates/acg_list_times.html"), "r", encoding="utf-8") as fp:
        html_content = fp.read().replace("@@acg_list@@", json.dumps(acg_data))
    img_data = await capture_element_screenshot(html_content)
    img_png = os.path.join(img_path, sender + "_acg.png")
    with open(img_png, "wb") as f:
        f.write(img_data)
    await send_image(room_id, img_png)


@on_regex(r"^漫展位置\s*(\d+)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    acg_id = match_obj.groups()[-1]
    acg_info_dict = await get_acg_info(acg_id)
    if not acg_info_dict:
        await send_text("未找到相关漫展信息", room_id, sender, sender_name)
        return

    msg = ""
    msg += f"漫展名称：{acg_info_dict.get('project_name')}\n"
    msg += f"漫展地点：{acg_info_dict.get('venue_name')}\n"
    msg += f"漫展位置：{get_coordinate_url(acg_info_dict.get('coordinate'))}\n"
    await send_text(msg, room_id)


@on_regex(r"^漫展详情\s*(\d+)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    acg_id = match_obj.groups()[-1]
    acg_info_dict = await get_acg_info(acg_id)
    if not acg_info_dict:
        await send_text("未找到相关漫展信息", room_id, sender, sender_name)
        return

    msg = "".join([
        f"漫展id：{acg_info_dict.get('id')}\n",
        f"漫展名称：{acg_info_dict.get('project_name')}\n",
        f"漫展地点：{acg_info_dict.get('venue_name')}\n",
        f"漫展时间：{acg_info_dict.get('start_time')} - {acg_info_dict.get('end_time')}\n",
        f"展票价格：{acg_info_dict.get('min_price') / 100} - {acg_info_dict.get('max_price') / 100} 元\n",
        f"是否有NPC招募信息：{'是' if acg_info_dict.get('has_npc') == 1 else '否'}\n",
        f"展会链接：\nhttps://show.bilibili.com/platform/detail.html?id={acg_info_dict.get('id')}\n"
    ])
    await send_text(msg, room_id)


@on_regex(r"^漫展搜索\s*(.+)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    key = match_obj.groups()[-1]
    acg_list = await get_acg_list(key=key, count=100)
    if acg_list.get("count") == 0:
        await send_text("未找到相关漫展信息", room_id, sender, sender_name)
        return

    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    with open(os.path.join(script_directory, "templates/acg_list.html"), "r", encoding="utf-8") as fp:
        html_content = fp.read().replace("@@acg_list@@", json.dumps(acg_list.get("data")))
    img_data = await capture_element_screenshot(html_content)
    img_png = os.path.join(img_path, sender + "_acg.png")
    with open(img_png, "wb") as f:
        f.write(img_data)
    await send_image(room_id, img_png)
