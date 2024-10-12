import os
import glob
import json
import random

from on import on_regex
from common import send_text, send_image, send_file


file_path = os.path.abspath(os.path.join("data", "file"))


async def get_random_file(name):
    file_list = glob.glob(os.path.join(file_path, name, "*"))
    if not file_list:
        return
    file = random.choice(file_list)
    print(name, file)

    return file


@on_regex(r"^黑丝(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("heisi_image")
    await send_image(room_id, file)


@on_regex(r"^白丝(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("baisi_image")
    await send_image(room_id, file)


@on_regex(r"^[Cc][Oo][Ss]([Pp][Ll][Aa][Yy])?(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("cosplay_image")
    await send_image(room_id, file)


@on_regex(r"^美女(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("meinv_image")
    await send_image(room_id, file)


@on_regex(r"^帅哥(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("shuaige_image")
    await send_image(room_id, file)


@on_regex(r"^腹肌(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("fuji_image")
    await send_image(room_id, file)


@on_regex(r"^动漫(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("dongman_image")
    await send_image(room_id, file)


@on_regex(r"^头像(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("avatar_image")
    await send_image(room_id, file)


@on_regex(r"^猫咪(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("maomi_image")
    await send_image(room_id, file)


@on_regex(r"^狗狗(图片)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("gougou_image")
    await send_image(room_id, file)


@on_regex(r"^白丝视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("baisi_video")
    await send_file(room_id, file)


@on_regex(r"^黑丝视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("heisi_video")
    await send_file(room_id, file)


@on_regex(r"^古风视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("gufeng_video")
    await send_file(room_id, file)


@on_regex(r"^[Cc][Oo][Ss]([Pp][Ll][Aa][Yy])?视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("cosplay_video")
    await send_file(room_id, file)


@on_regex(r"^美女视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("meinv_video")
    await send_file(room_id, file)


@on_regex(r"^热舞视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("rewu_video")
    await send_file(room_id, file)


@on_regex(r"^帅哥视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("shuaige_video")
    await send_file(room_id, file)


@on_regex(r"^动漫视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("dongman_video")
    await send_file(room_id, file)


@on_regex(r"^休闲视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("xiuxian_video")
    await send_file(room_id, file)


@on_regex(r"^萌娃视频$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("mengwa_video")
    await send_file(room_id, file)


@on_regex(r"^(舔狗|舔狗日记|情感语录)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("tiangou_txt")
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    await send_text(text, room_id)


@on_regex(r"^([Kk][Ff][Cc](语录)?|肯德基|疯狂星期四|肯德基疯狂星期四)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("kfc_txt")
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    await send_text(text, room_id)


@on_regex(r"^(随机小说|小说推荐)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    file = await get_random_file("小说")
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    dic = json.loads(text)
    text = f"书名: {dic['title']}\n作者: {dic['author']}\n类型: {dic['type']}\n简介: {dic['js'].strip()}\n👉{dic['download']}"
    await send_text(text, room_id)
