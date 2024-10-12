from on import on_regex
from common import send_text


@on_regex(r"^.*\"(.*)\"加入了群聊.*$|^\"(.*)\"通过扫描.*$")
async def _(**kwargs):
    msg = kwargs.get("msg")
    if msg.type != 10000:
        return
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    wx_name1, wx_name2 = match_obj.groups()
    wx_name = wx_name1 or wx_name2
    await send_text(f"@{wx_name} 欢迎欢迎\n━(*｀∀´*)ノ亻!", room_id)

