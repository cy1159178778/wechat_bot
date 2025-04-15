import os
import re

from on import current_plugins
from common import var, admin, open_groups_obj, get_alias_in_chatroom, get_at_list

plugins_path = os.path.join("src", "plugins")
for plugin in os.listdir(plugins_path):
    plugin_package = ".".join(["src", "plugins", plugin])
    __import__(plugin_package)
current_plugins.sort(key=lambda x: x[0])
# print(current_plugins)


async def handle(msg):
    try:
        var["msg_rec"] += 1
        await handle_msg(msg)
    except Exception as e:
        print("handle_msg error:", e)
        import traceback
        print(traceback.format_exc())


async def handle_msg(msg):
    if not msg.is_group:
        return

    sender = msg.sender
    room_id = msg.roomid

    if msg.type == 49:
        text = re.findall(r"<title>(.*?)</title>", msg.content)[0].lstrip()
        svrid = re.findall(r"<svrid>(.*?)</svrid>", msg.content)[0]
    else:
        text = msg.content.lstrip()
        svrid = None
    if text.endswith("\u2005"):
        pass
    else:
        text = text.rstrip()
    data = open_groups_obj.get_data(room_id)
    data_list = data.split("|") if data else []
    if "功能" in data_list or sender == admin:
        pass
    elif data and re.match(f"^({data}).*$", text):
        pass
    else:
        return

    block_priority = None
    sender_name = None
    at_list = get_at_list(msg.xml)

    for item in current_plugins:
        priority, func, on_type, pattern, block, chat_level = item
        if block_priority is not None and block_priority < priority:
            break
        if on_type == "on_regex":
            match_obj = re.match(pattern, text)
            if not match_obj:
                continue
            if sender_name is None:
                sender_name = await get_alias_in_chatroom(room_id, sender)
            kwargs = {
                "msg": msg,
                "match_obj": match_obj,
                "room_id": room_id,
                "sender": sender,
                "sender_name": sender_name,
                "at_list": at_list,
                "svrid": svrid
            }
            await func(**kwargs)
            if block:
                block_priority = priority
        elif on_type == "on_full_match":
            pass
