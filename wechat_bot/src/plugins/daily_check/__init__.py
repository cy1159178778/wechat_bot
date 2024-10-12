import os

from on import on_regex
from common import send_image
from .handle import get_card, base_path


daily_img_path = os.path.join(base_path, "img")


@on_regex(r"^(签到|抽签|打卡)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    img_bytes = await get_card(sender, sender_name)
    daily_check_file = os.path.join(daily_img_path, room_id + sender + "_daily.png")
    with open(daily_check_file, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, daily_check_file)
