from on import on_regex
from common import admin, open_groups_obj, send_text


@on_regex(r"^开启(.+)$", priority=0, block=True)
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    if sender != admin:
        return

    data = open_groups_obj.get_data(room_id)
    data_list = data.split("|") if data else []
    item = match_obj.groups()[-1]
    data_list.append(item)
    open_groups_obj.set_data(room_id, "|".join(data_list))
    await send_text("已开启", room_id)


@on_regex(r"^关闭(.+)$", priority=0, block=True)
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    if sender != admin:
        return

    data = open_groups_obj.get_data(room_id)
    data_list = data.split("|") if data else []
    item = match_obj.groups()[-1]
    if item == "所有功能":
        data_list = []
    elif item in data_list:
        data_list.remove(item)
    open_groups_obj.set_data(room_id, "|".join(data_list))
    await send_text("已关闭", room_id)


@on_regex(r"^群功能$", priority=0, block=True)
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    if sender != admin:
        return

    data = open_groups_obj.get_data(room_id)
    data_list = data.split("|") if data else []
    if not data_list:
        res = "未开启"
    elif "功能" in data_list:
        res = "全功能"
    else:
        res = data
    await send_text(res, room_id)
