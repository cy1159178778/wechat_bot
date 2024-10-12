import os
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .heweather import get_weather_image

base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")


@on_regex(r"^.*?(.*)天气(.*).*?$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    city = match_obj.group(1).strip() or match_obj.group(2).strip()
    if not city:
        await send_text("地点是...空气吗?? >_<", room_id)
        return
    img_bytes = await get_weather_image(city)
    weather_image = os.path.join(img_path, room_id + sender + "_weather.png")
    with open(weather_image, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, weather_image)
