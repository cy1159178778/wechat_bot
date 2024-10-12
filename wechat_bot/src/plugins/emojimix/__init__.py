import os
import re
import emoji
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .config import Config
from .data_source import mix_emoji

base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
emojis = filter(lambda e: len(e) == 1, emoji.EMOJI_DATA.keys())
pattern = "(" + "|".join(re.escape(e) for e in emojis) + ")"


@on_regex(rf"^\s*(?P<code1>{pattern})\s*\+?\s*(?P<code2>{pattern})\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    emoji_code1 = match_obj["code1"]
    emoji_code2 = match_obj["code2"]
    result = await mix_emoji(emoji_code1, emoji_code2)
    if isinstance(result, str):
        await send_text(result, room_id, sender, sender_name)
    else:
        img_png = os.path.join(img_path, sender + "_emoji.png")
        with open(img_png, "wb") as f:
            f.write(result)
        await send_image(room_id, img_png)
