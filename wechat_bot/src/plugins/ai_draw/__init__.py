import os
import re
import time
import httpx
import base64
import asyncio
import fal_client
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .check_img import check_img, add_mosaic
from ..translate.aliyun_translate import Sample

base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
CN = re.compile(r"[\u4e00-\u9fa6]+")
TRANS = re.compile(r"[^A-Za-z_,，.。!！\"'“‘;；:：?？`~·￥@#$%^&*+\-/\\\[\]()（）<> \n\t]+")
htags = r"\b(nsfw|no\s*clothes|mucus|micturition|urethra|Urinary|Urination|climax|n\s*o\s*c\s*l\s*o\s*t\s*h\s*e\s*s|n[ -]?o[ -]?c[ -]?l[ -]?o[ -]?t[ -]?h[ -]?e[ -]?s|nudity|nude|naked|nipple|blood|censored|vagina|gag|gokkun|hairjob|tentacle|oral|fellatio|areolae|lactation|paizuri|piercing|sex|footjob|masturbation|hips|penis|testicles|ejaculation|cum|tamakeri|pussy|pubic|clitoris|mons|cameltoe|grinding|crotch|cervix|cunnilingus|insertion|penetration|fisting|fingering|peeing|buttjob|spanked|anus|anal|anilingus|enema|x-ray|wakamezake|humiliation|tally|futa|incest|twincest|pegging|porn|Orgasm|womb|femdom|ganguro|bestiality|gangbang|3P|tribadism|molestation|voyeurism|exhibitionism|rape|spitroast|cock|69|doggystyle|missionary|virgin|shibari|bondage|bdsm|rope|pillory|stocks|bound|hogtie|frogtie|suspension|anal|dildo|vibrator|hitachi|nyotaimori|vore|amputee|transformation|bloody|pornhub)\b"
H_compile = re.compile(htags)
os.environ["FAL_KEY"] = ""


def get_hui_tu_img(prompt, is_check=True):
    t1 = time.time()
    trans_list = TRANS.findall(prompt)
    if trans_list and not all(map(str.isdigit, trans_list)):
        trans_str = ",".join(trans_list)
        handle_prompt = TRANS.sub(" {} ", prompt)
        n = 3
        while n:
            try:
                trans_res_str = Sample.translate_to_en(trans_str)
                handle_prompt = handle_prompt.format(*map(str.strip, trans_res_str.split(",")))
                handle_prompt = handle_prompt.replace("  ", " ").strip()
                break
            except Exception as e:
                print(e)
            n -= 1
        else:
            return {"error": "翻译提示词失败，请稍后再试！QAQ\n建议用英文提示词，不需要翻译"}
    else:
        handle_prompt = prompt

    if not handle_prompt:
        return {"error": "绘图失败，请稍后再试！QAQ"}

    if is_check and H_compile.search(handle_prompt):
        return {"error": "不可以涩涩！>_<"}

    n = 3
    img_url = ""
    bytes_img = None
    while n:
        try:
            if not img_url:
                handler = fal_client.submit(
                    "fal-ai/flux/schnell",
                    arguments={
                        "prompt": handle_prompt,
                        "image_size": "square_hd"
                    },
                )
                result = handler.get()
                if result["has_nsfw_concepts"][0]:
                    return {"error": "包含NSFW！>_<"}
                img_url = result["images"][0]["url"]

            bytes_img = httpx.get(img_url).content
            break
        except Exception as e:
            print(e)
        n -= 1

    if not bytes_img:
        return {"error": "绘图失败，请稍后再试！QwQ"}
    base64_img = base64.b64encode(bytes_img)

    if base64_img is None:
        return {"error": "绘图失败，请稍后再试！QwQ"}

    n = 3
    while n:
        try:
            conclusion_type = 1
            if is_check:
                conclusion_type = check_img(base64_img)
            if conclusion_type == 2:
                bytes_img = add_mosaic(bytes_img)
                info = f"提示词：{handle_prompt}\n绘图成功，用时{int(time.time() - t1)}秒！"
                info += "图片似乎有点涩涩或其他不合规内容，已做打码处理，原图我就偷偷发给主人看了(*/ω＼*)"
            else:
                info = f"提示词：{handle_prompt}\n绘图成功，用时{int(time.time() - t1)}秒！"
            return {"img": bytes_img, "info": info}
        except Exception as e:
            print(e)
        n -= 1

    return {"error": "绘图失败，请稍后再试！QwQ"}


@on_regex(r"^(绘图|画图|绘画)\s*(.*)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    _, prompt = match_obj.groups()
    if not prompt:
        await send_text("没有绘图提示词", room_id, sender, sender_name)
        return

    await send_text("在画了在画了......", room_id)
    results = await asyncio.get_event_loop().run_in_executor(None, get_hui_tu_img, prompt, True)
    if "error" in results:
        message = results["error"]
        await send_text(message, room_id, sender, sender_name)
    else:
        bytes_img = results["img"]
        if not isinstance(bytes_img, bytes):
            await send_text("绘图失败，请稍后再试！QwQ", room_id, sender, sender_name)
            return
        info = results["info"]
        img_png = os.path.join(img_path, sender + "_draw.png")
        with open(img_png, "wb") as f:
            f.write(bytes_img)
        await send_image(room_id, img_png)
        await send_text(info, room_id)
