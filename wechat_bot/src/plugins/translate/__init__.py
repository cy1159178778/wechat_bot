from on import on_regex
from common import send_text
from .aliyun_translate import async_trans


@on_regex(r"^(翻译|译(.))\s*([\s\S]*)?")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    matchgroup = match_obj.groups()

    text = matchgroup[2]
    if not text:
        return

    dd = {
        "中": "zh",
        "粤": "yue",
        "繁": "zh-tw",
        "英": "en",
        "日": "ja",
        "韩": "ko",
        "法": "fr",
        "俄": "ru",
        "德": "de",
    }

    to = "zh"
    if matchgroup[0] != "翻译":
        try:
            to = dd[matchgroup[1]]
        except KeyError:
            await send_text("不支持该语种，目前只支持：中、粤、繁、英、日、韩、法、俄、德", room_id)
            return

    n = 3
    target = ""
    while n:
        try:
            target = await async_trans(text, to)
            break
        except Exception as e:
            print(e)
        n -= 1

    if target:
        await send_text(target, room_id, sender, sender_name)
    else:
        await send_text("翻译失败，请稍后再试", room_id, sender, sender_name)
