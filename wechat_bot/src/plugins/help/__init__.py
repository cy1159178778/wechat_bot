import os
from pathlib import Path
from on import on_regex
from common import send_image

base_path = Path(__file__).parent
help_file = os.path.join(base_path, "help.png")


@on_regex(r"^(帮助|菜单|说明)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    receiver = room_id
    await send_image(receiver, help_file)
