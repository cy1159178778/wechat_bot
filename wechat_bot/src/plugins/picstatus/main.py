import os
import asyncio

os.chdir("../../../")

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

img_bytes = asyncio.run(render_current_template())
img_png = os.path.join(img_path, "123" + "_status.png")
with open(img_png, "wb") as f:
    f.write(img_bytes)
