from datetime import datetime
from dataclasses import dataclass

from common import var, nick_name
from . import normal_collector
from ..util import format_timedelta


@dataclass
class BotStatus:
    self_id: str
    adapter: str
    nick: str
    bot_connected: str
    msg_rec: str
    msg_sent: str


async def get_bot_status(now_time) -> BotStatus:
    nick = nick_name
    bot_connected = (
        format_timedelta(now_time - t)
        if (t := var.get("bot_connect_time"))
        else "未知"
    )

    msg_rec = var.get("msg_rec", "未知")
    msg_sent = var.get("msg_sent", "未知")

    return BotStatus(
        self_id="123",
        adapter="OneBot V11",
        nick=nick,
        bot_connected=bot_connected,
        msg_rec=msg_rec,
        msg_sent=msg_sent,
    )


@normal_collector()
async def bots():
    now_time = datetime.now().astimezone()
    return (
        [await get_bot_status(now_time)]
    )
