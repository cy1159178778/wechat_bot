import os

from on import on_regex
from common import send_image
from .utils import get_og_info

img_path = os.path.join(os.path.dirname(__file__), "img")


@on_regex(r'^.*https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.*$')
async def _(**kwargs):
    msg = kwargs.get("msg")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    og_info = await get_og_info(msg.content, room_id)
    if not og_info:
        return

    img_png = os.path.join(img_path, sender + "_og.png")
    with open(img_png, "wb") as f:
        f.write(og_info["img"])
    await send_image(room_id, img_png)
