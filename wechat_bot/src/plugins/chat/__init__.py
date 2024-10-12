import asyncio
from on import on_regex
from .chat import chat
from common import nick_name, send_text


@on_regex(r"^(.*)@{}\u2005(.*)$".format(nick_name), priority=2)
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    msg = "".join(match_obj.groups()).strip()
    resp = await asyncio.get_event_loop().run_in_executor(None, chat, sender, msg)
    await send_text(resp, room_id, sender, sender_name)
