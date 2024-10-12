import os
import random
from pathlib import Path
from pypinyin import lazy_pinyin

from on import on_regex
from common import nick_name, send_text, send_image


Bot_NICKNAME = nick_name
img_path = os.path.join(os.path.dirname(__file__), "img")
img_eat_path = Path(os.path.join(os.path.dirname(__file__), "eat_pic"))
all_file_eat_name = os.listdir(str(img_eat_path))
img_drink_path = Path(os.path.join(os.path.dirname(__file__), "drink_pic"))
all_file_drink_name = os.listdir(str(img_drink_path))


@on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|下|晚)?(上|午|餐|饭|夜宵|宵夜)?吃(什么|啥|点啥)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    img_name = random.choice(all_file_eat_name)
    img = img_eat_path / img_name
    name = img.stem
    img_png = os.path.join(img_path, " ".join(lazy_pinyin(img.stem)) + ".png")
    await send_image(room_id, img_png)
    await send_text(f"{Bot_NICKNAME}建议你吃: \n⭐{name}⭐", room_id)


@on_regex(r"^(/)?[今|明|后]?[天|日]?(早|中|下|晚)?(上|午|餐|饭|夜宵|宵夜)?喝(什么|啥|点啥)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    img_name = random.choice(all_file_drink_name)
    img = img_drink_path / img_name
    name = img.stem
    img_png = os.path.join(img_path, " ".join(lazy_pinyin(img.stem)) + ".png")
    await send_image(room_id, img_png)
    await send_text(f"{Bot_NICKNAME}建议你喝: \n⭐{name}⭐", room_id)
