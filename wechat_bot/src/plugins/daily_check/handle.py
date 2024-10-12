import os
import time
import random
from browser import get_browser
from .data_source import get_msg, get_greet, get_stick, get_acg_image, base_path


async def get_card(user_id, user_name):
    stick = get_stick(user_id)
    day_time = time.strftime(r"%m/%d", time.localtime())
    date = time.strftime(r"%Y-%m-%d", time.localtime())
    random.seed()
    acg_url = get_acg_image()
    with open(base_path / "data/card2.html", "r", encoding="utf-8") as f:
        template = str(f.read())

    filename = f"temp-card-{user_id}"

    if os.path.isfile(base_path / f"data/temp/{filename}.html"):
        modifiedTime = time.localtime(
            os.stat(base_path / f"data/temp/{filename}.html").st_mtime
        )
        mtime = time.strftime(r"%Y%m%d", modifiedTime)
        ntime = time.strftime(r"%Y%m%d", time.localtime(time.time()))
        if mtime != ntime:
            points = random.randint(1, 20)
            template = template.replace("[points]", str(points))
        else:
            template = template.replace("[points]", "0(已经签到过啦)")
    else:
        points = random.randint(1, 20)
        template = template.replace("[points]", str(points))

    template = template.replace("static/", "../static/")
    template = template.replace("[acg_url]", acg_url)
    template = template.replace("[greet]", get_greet())
    template = template.replace("[msg_of_the_day]", (get_msg(user_id))["SENTENCE"])
    template = template.replace("[day_time]", day_time)
    template = template.replace("[date]", date)
    template = template.replace("[user_name]", user_name)
    template = template.replace("[luck-status]", stick["FORTUNE_SUMMARY"])
    template = template.replace("[star]", stick["LUCKY_STAR"])
    template = template.replace("[comment]", stick["SIGN_TEXT"])
    template = template.replace("[resolve]", stick["UN_SIGN_TEXT"])

    with open(base_path / f"data/temp/{filename}.html", "w", encoding="utf-8") as f:
        f.write(template)

    return await generate_pic(filename)


async def generate_pic(filename: str):
    browser = await get_browser()
    page = await browser.new_page(device_scale_factor=2)
    path = os.path.abspath(base_path / f"data/temp/{filename}.html")
    await page.goto(f"file://{path}")
    card = await page.query_selector(".card")
    assert card is not None
    img = await card.screenshot(type="png")
    await page.close()
    return img
