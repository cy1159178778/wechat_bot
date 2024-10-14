import schedule

from on import on_regex
from common import admin, send_image, run_async_task
from .data_source import Report


@on_regex("^(日报|查看斯卡蒂日报)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    img_path = await Report.get_report_image()
    await send_image(room_id, img_path)


@on_regex("^(重新获取日报)$")
async def _(**kwargs):
    sender = kwargs.get("sender")
    if sender != admin:
        return

    room_id = kwargs.get("room_id")
    img_path = await Report.get_report_image_afresh()
    await send_image(room_id, img_path)


async def send_daily_report_task():
    img_path = await Report.get_report_image()
    for room_id in task_group:
        await send_image(room_id, img_path)


task_group = ["xxx@chatroom"]
schedule.every().day.at("11:00").do(run_async_task(send_daily_report_task))
