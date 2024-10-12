import os
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .templates import render_current_template
from .collectors import enable_collectors, load_collectors
from .config import ConfigModel, config
from .templates import load_template

base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
load_collectors()
try:
    _template = load_template(config.ps_template)
except ImportError as e:
    raise ImportError(f"Cannot found template `{config.ps_template}`") from e
enable_collectors(*_template.collectors)
__version__ = "2.0.0.post4"


@on_regex(r"^(运行状态|运行状况|运行信息|状态)$", priority=0, block=True)
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    try:
        img_bytes = await render_current_template()
        img_png = os.path.join(img_path, sender + "_status.png")
        with open(img_png, "wb") as f:
            f.write(img_bytes)
        await send_image(room_id, img_png)
    except Exception as ee:
        print(ee)
        import traceback
        print(traceback.format_exc())
        await send_text("获取运行状态图片失败，请检查后台输出", room_id)
