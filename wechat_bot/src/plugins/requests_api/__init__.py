import os
import schedule
from io import BytesIO
from PIL import Image
from pathlib import Path
from datetime import datetime, timedelta

from on import on_regex
from common import send_text, send_image, get_url_json, get_url_text, get_url_content, run_async_task

base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
daily_60s_path = os.path.join(base_path, "daily_60s")
moyuribao_path = os.path.join(base_path, "moyuribao")
cp_path = os.path.join(base_path, "cp")
task_group = ["xxx@chatroom"]
djss_txt_url = "https://dj.lbbb.cc/api.php?name={}"
ysss_txt_url = "https://www.hhlqilongzhu.cn/api/ziyuan_nanfeng.php?keysearch={}"
xsss_txt_url = "https://www.hhlqilongzhu.cn/api/novel_1.php?name={}&n={}"
wass_txt_url = "https://www.hhlqilongzhu.cn/api/wenan_sou.php?msg={}"
img_search_url = "https://www.hhlqilongzhu.cn/api/duitang_st.php?type=json&msg={}"
xzys_txt_url = "http://api.yujn.cn/api/xingzuo.php?msg={}"
cp_url = "https://www.hhlqilongzhu.cn/api/tu_lofter_cp.php?n1={}&n2={}"


@on_regex(r"^(短剧搜索|搜索短剧|搜短剧)\s*(.*?)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    _, key = match_obj.groups()
    key = key.strip()
    if not key:
        await send_text("缺少搜索关键词", room_id, sender, sender_name)
        return
    json_res = await get_url_json(djss_txt_url.format(key))
    if json_res is None:
        await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
        return
    data = json_res.get("datas", {}).get("data", [])
    if not data:
        await send_text("无搜索结果，请更换搜索关键词", room_id, sender, sender_name)
        return
    total = len(data)
    for i in range(0, total, 30):
        results = []
        for j, info in enumerate(data[i:i + 30], i + 1):
            name = info["name"]
            link = info["link"]
            results.append(f"{j}、{name}\n👉{link}")
        await send_text("\n\n".join(results), room_id)


@on_regex(r"^(影视搜索|搜索影视|搜影视|电影搜索|搜索电影|搜电影|电视剧搜索|搜索电视剧|搜电视剧)\s*(.*?)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    _, key = match_obj.groups()
    if not key:
        await send_text("缺少搜索关键词词", room_id, sender, sender_name)
        return
    json_res = await get_url_json(ysss_txt_url.format(key))
    if json_res is None:
        await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
        return
    data = json_res.get("data", [])
    if not data:
        await send_text("无搜索结果，请更换搜索关键词", room_id, sender, sender_name)
        return
    total = len(data)
    for i in range(0, total, 10):
        results = []
        for j, info in enumerate(data[i:i + 10], i + 1):
            title = info["title"]
            data_url = info["data_url"]
            data_url = "\n".join(["👉" + i for i in data_url.split("\n")])
            results.append(f"{j}、{title}\n{data_url}")
        await send_text("\n\n".join(results), room_id)


@on_regex(r"^(小说搜索|搜索小说|搜小说)\s*(\S*)\s*(\d*)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    if match_obj:
        _, key, n = match_obj.groups()
        if not key:
            await send_text("缺少搜索关键词", room_id, sender, sender_name)
            return
        if n:
            json_res = await get_url_json(xsss_txt_url.format(key, n))
            if json_res is None:
                await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
                return
            if not json_res or json_res.get("title") is None:
                await send_text("无搜索结果，请更换搜索关键词", room_id, sender, sender_name)
                return
            title = json_res.get("title", "")
            author = json_res.get("author", "")
            type_ = json_res.get("type", "")
            download = json_res.get("download", "")
            await send_text(f"书名：{title}\n作者：{author}\n类型：{type_}\n👉{download}", room_id)
            return
        text = await get_url_text(xsss_txt_url.format(key, ""))
        if text is None:
            await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
            return
        if not text:
            await send_text("无搜索结果，请更换搜索关键词", room_id, sender, sender_name)
            return
        data = text.split("\n")
        total = len(data)
        if total == 1:
            json_res = await get_url_json(xsss_txt_url.format(key, 1))
            if json_res is None:
                await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
                return
            if not json_res or json_res.get("title") is None:
                await send_text("无搜索结果，请更换搜索关键词", room_id, sender, sender_name)
                return
            title = json_res.get("title", "")
            author = json_res.get("author", "")
            type_ = json_res.get("type", "")
            download = json_res.get("download", "")
            await send_text(f"书名：{title}\n作者：{author}\n类型：{type_}\n👉{download}", room_id)
            return
        for i in range(0, total, 30):
            await send_text("\n".join([j.replace(":", "、", 1) for j in data[i:i + 30]]), room_id)
        await send_text(f'请在"小说搜索 {key}"后面加上序号选择小说，注意需要空格，如：小说搜索 剑来 9', room_id)


@on_regex(r"^(文案搜索|搜索文案|搜文案)\s*(.*?)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    _, key = match_obj.groups()
    key = key.strip()
    if not key:
        await send_text("缺少搜索关键词", room_id, sender, sender_name)
        return

    text = await get_url_text(wass_txt_url.format(key))
    if text is None:
        await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
    else:
        await send_text(text.replace("\n", " ").replace("\r", " "), room_id)


@on_regex(r"^(图片搜索|搜索图片|搜图片)\s*(.*?)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    _, key = match_obj.groups()
    key = key.strip()
    if not key:
        await send_text("缺少搜索关键词", room_id, sender, sender_name)
        return

    data = await get_url_json(img_search_url.format(key))
    if data is None:
        await send_text("搜索异常，请稍后再试", room_id, sender, sender_name)
        return

    data = data.get("data", [{}])
    if not data or not data[0].get("path"):
        await send_text("无搜索结果, 请更换关键词", room_id, sender, sender_name)
        return

    img_bytes = await get_url_content(data[0]["path"])
    if not img_bytes:
        await send_text("访问异常，请稍后再试", room_id, sender, sender_name)
        return

    img_png = os.path.join(img_path, sender + "img_search.png")
    with open(img_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, img_png)


@on_regex(r"^(.+)座.*运势.*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    xingzuo = match_obj.group(1)
    text = await get_url_text(xzys_txt_url.format(xingzuo))
    if text is None:
        await send_text("访问异常，请稍后再试", room_id, sender, sender_name)
        return
    text = text.replace("\\n", "")
    await send_text(text, room_id)


@on_regex(r"^[cC][pP]\s*(.+)\s+(.+)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    cp_list = match_obj.groups()
    content = await get_url_content(cp_url.format(*cp_list))
    if content:
        image = Image.open(BytesIO(content))
        cropped_image = image.crop((0, 0, image.width, image.height - 400))
        byte_io = BytesIO()
        cropped_image.save(byte_io, 'PNG')
        byte_data = byte_io.getvalue()
        img_png = os.path.join(cp_path, sender + "_cp.png")
        with open(img_png, "wb") as f:
            f.write(byte_data)
        await send_image(room_id, img_png)
    else:
        await send_text("访问异常，请稍后再试", room_id, sender, sender_name)


async def get_daily_60s():
    now_time = datetime.now()
    if now_time.hour < 9:
        now_time -= timedelta(days=1)
    date = now_time.strftime("%Y-%m-%d")
    path = os.path.join(daily_60s_path, f"{date}.png")
    if os.path.exists(path):
        return path

    content = await get_url_content("http://api.suxun.site/api/sixs?type=img")
    if not content:
        return ""

    with open(path, "wb") as f:
        f.write(content)
    return path


async def send_daily_60s_task():
    daily_60s_file = await get_daily_60s()
    if not daily_60s_file:
        return
    for room_id in task_group:
        await send_image(room_id, daily_60s_file)


schedule.every().day.at("09:00").do(run_async_task(send_daily_60s_task))
# schedule.every().day.at("11:00").do(run_async_task(send_daily_60s_task))


@on_regex(r"^每日?(新闻|60秒|60s|60S)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    daily_60s_file = await get_daily_60s()
    if not daily_60s_file:
        await send_text("访问异常，请稍后再试", room_id, sender, sender_name)
        return
    await send_image(room_id, daily_60s_file)


async def get_moyuribao():
    now_time = datetime.now()
    if now_time.hour < 9:
        now_time -= timedelta(days=1)
    date = now_time.strftime("%Y-%m-%d")
    path = os.path.join(moyuribao_path, f"{date}.png")
    if os.path.exists(path):
        return path

    content = await get_url_content("https://dayu.qqsuu.cn/moyuribao/apis.php?type=img")
    if not content:
        return ""

    with open(path, "wb") as f:
        f.write(content)
    return path


async def send_moyuribao_task():
    moyuribao_file = await get_moyuribao()
    if not moyuribao_file:
        return
    for roomid in task_group:
        await send_image(roomid, moyuribao_file)


schedule.every().monday.at("10:00").do(run_async_task(send_moyuribao_task))
schedule.every().tuesday.at("10:00").do(run_async_task(send_moyuribao_task))
schedule.every().wednesday.at("10:00").do(run_async_task(send_moyuribao_task))
schedule.every().thursday.at("10:00").do(run_async_task(send_moyuribao_task))
schedule.every().friday.at("10:00").do(run_async_task(send_moyuribao_task))

# schedule.every().monday.at("12:00").do(run_async_task(send_moyuribao_task))
# schedule.every().tuesday.at("12:00").do(run_async_task(send_moyuribao_task))
# schedule.every().wednesday.at("12:00").do(run_async_task(send_moyuribao_task))
# schedule.every().thursday.at("12:00").do(run_async_task(send_moyuribao_task))
# schedule.every().friday.at("12:00").do(run_async_task(send_moyuribao_task))


@on_regex(r"^摸鱼(日报|日历)?$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    moyuribao_file = await get_moyuribao()
    if not moyuribao_file:
        await send_text("访问失败，请稍后再试", room_id, sender, sender_name)
        return
    await send_image(room_id, moyuribao_file)
