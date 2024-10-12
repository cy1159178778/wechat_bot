from on import on_regex
from common import send_text
from .run import run


@on_regex(r"^(code|运行代码)\s+(.+?)\n([\s\S]+)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    text = match_obj.group().strip()
    flag, res = await run(text)
    if flag:
        await send_text(res, room_id)
    else:
        await send_text(res, room_id, sender, sender_name)
