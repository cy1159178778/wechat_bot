from .render_pic import render
from .weather_data import Weather


api_key = ""
api_type = 0


async def get_weather_image(city):
    w_data = Weather(city_name=city, api_key=api_key, api_type=api_type)
    await w_data.load_data()
    bytes_img = await render(w_data)
    return bytes_img
