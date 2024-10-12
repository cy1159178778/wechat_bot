import os
import re
import asyncio
from pathlib import Path
from arclet.alconna import TextFormatter
from meme_generator import Meme

from on import on_regex
from common import send_text, send_image, send_emotion, get_head_img_by_wx_id, get_meme_user_info, get_url_content, \
    get_chatroom_member
from .manager import meme_manager

base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
menes_list_png = os.path.join(base_path, "menes_list.png")
at_compile = re.compile(r"@.*?\u2005")


@on_regex("^(头像表情包|文字表情包|表情帮助|表情包制作|表情列表)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    msg = ("触发方式：“关键词 + @某人/文字”(中间需要空格)\n"
           "发送 “表情详情 + 关键词” 查看表情参数和预览\n"
           "目前支持的表情列表：")
    await send_text(msg, room_id)
    await send_image(room_id, menes_list_png)


def find_meme(meme_name: str) -> Meme | str:
    found_memes = meme_manager.find(meme_name)
    found_num = len(found_memes)

    if found_num == 0:
        if searched_memes := meme_manager.search(meme_name, limit=5):
            return (
                f"表情 {meme_name} 不存在，你可能在找：\n"
                + "\n".join(
                    f"* {meme.key} ({'/'.join(meme.keywords)})"
                    for meme in searched_memes
                )
            )
        else:
            return f"表情 {meme_name} 不存在！"

    return found_memes[0]


def check_image_gif(image_data):
    if image_data.startswith(b'GIF89a') or image_data.startswith(b'GIF87a'):
        return True
    else:
        return False


@on_regex(r"^表情详情\s*(.+)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    meme_name = match_obj.groups()[0]
    meme = find_meme(meme_name)
    if isinstance(meme, str):
        await send_text(meme, room_id)
        return

    keywords = "、".join([f'"{keyword}"' for keyword in meme.keywords])
    shortcuts = "、".join(
        [f'"{shortcut.humanized or shortcut.key}"' for shortcut in meme.shortcuts]
    )
    tags = "、".join([f'"{tag}"' for tag in meme.tags])

    image_num = f"{meme.params_type.min_images}"
    if meme.params_type.max_images > meme.params_type.min_images:
        image_num += f" ~ {meme.params_type.max_images}"

    text_num = f"{meme.params_type.min_texts}"
    if meme.params_type.max_texts > meme.params_type.min_texts:
        text_num += f" ~ {meme.params_type.max_texts}"

    default_texts = ", ".join([f'"{text}"' for text in meme.params_type.default_texts])

    args_info = ""
    if args_type := meme.params_type.args_type:
        formater = TextFormatter()
        for option in args_type.parser_options:
            opt = option.option()
            alias_text = (
                    " ".join(opt.requires)
                    + (" " if opt.requires else "")
                    + "│".join(sorted(opt.aliases, key=len))
            )
            args_info += (
                f"\n  * {alias_text}{opt.separators[0]}"
                f"{formater.parameters(opt.args)} {opt.help_text}"
            )

    info = (
            f"表情名：{meme.key}"
            + f"\n关键词：{keywords}"
            + (f"\n快捷指令：{shortcuts}" if shortcuts else "")
            + (f"\n标签：{tags}" if tags else "")
            + f"\n需要图片数目：{image_num}"
            + f"\n需要文字数目：{text_num}"
            + (f"\n默认文字：[{default_texts}]" if default_texts else "")
            + (f"\n可选参数：{args_info}" if args_info else "")
    )
    info += "\n表情预览：\n"
    img_io = await asyncio.get_event_loop().run_in_executor(None, meme.generate_preview)
    img_bytes = img_io.getvalue()
    is_gif = check_image_gif(img_bytes)
    img_png = os.path.join(img_path, room_id + sender + "_meme.png")
    with open(img_png, "wb") as f:
        f.write(img_bytes)
    await send_text(info, room_id)
    if is_gif:
        await send_emotion(room_id, img_png)
    else:
        await send_image(room_id, img_png)


def meme_call(meme, image_list, text_list, args):
    return meme(images=image_list, texts=text_list, args=args)


def handle_matchers(meme: Meme):
    keywords = "|".join(meme.keywords)
    pattern = f"^({keywords})(.*)$"

    @on_regex(pattern, block=True)
    async def _(**kwargs):
        match_obj = kwargs.get("match_obj")
        room_id = kwargs.get("room_id")
        sender = kwargs.get("sender")
        sender_name = kwargs.get("sender_name")
        at_list = kwargs.get("at_list")
        groups = match_obj.groups()
        text = groups[-1]
        wx_name_list = []
        if text:
            if text[0] not in " @":
                return
            wx_name_list = at_compile.findall(text)
            text = at_compile.sub("", text)
            temp_list = text.strip().split()
        else:
            temp_list = []
        if meme.params_type.args_type is None:
            parser_options = []
        else:
            parser_options = meme.params_type.args_type.parser_options or []

        i = 0
        args = {}
        text_list = []
        while i < len(temp_list):
            text = temp_list[i]
            i += 1
            for parser_option in parser_options:
                if text not in parser_option.names:
                    continue
                parser_args = parser_option.args or []
                parser_dest = parser_option.dest or ""
                if parser_dest:
                    args[parser_dest] = parser_option.action.value
                elif parser_args and i < len(temp_list):
                    for parser_arg in parser_args:
                        args[parser_arg.name] = temp_list[i]
                        if parser_arg.value == "int":
                            try:
                                args[parser_arg.name] = int(temp_list[i])
                            except ValueError:
                                await send_text(f"{temp_list[i]}应为整数", room_id, sender, sender_name)
                                return
                    i += 1
                break
            text_list.append(text)

        if len(at_list) != len(wx_name_list):
            members = await get_chatroom_member(room_id)
            members_info = {v.strip(): k for k, v in members.items()} if members else {}
            for wx_name in wx_name_list:
                wx_name = wx_name[1:-1]
                if wx_name not in members_info:
                    continue
                at_list.append(members_info[wx_name])

        if meme.params_type.min_texts > 0 and not text_list:
            text_list = meme.params_type.default_texts
        if meme.params_type.min_images == 1 and not at_list:
            at_list.append(sender)
        elif meme.params_type.min_images == 2 and len(at_list) == 1:
            at_list.insert(0, sender)

        if len(at_list) < meme.params_type.min_images:
            return
        if len(text_list) < meme.params_type.min_texts:
            return

        text_list = text_list[:meme.params_type.max_texts]
        at_list = at_list[:meme.params_type.max_images]
        image_list = []
        args_user_infos = []
        if len(at_list) == 1 and at_list[0] == sender:
            head_img_url = await get_head_img_by_wx_id(sender)
            head_img_bytes = await get_url_content(head_img_url)
            if head_img_bytes is None:
                await send_text("获取头像失败", room_id, sender, sender_name)
                return
            image_list.append(head_img_bytes)
            args_user_infos.append({"name": sender_name, "gender": "unknown"})
        elif at_list:
            meme_user_info = await get_meme_user_info(room_id, at_list)
            for wx_id in at_list:
                head_img_url = meme_user_info[wx_id].get("head_img")
                head_img_bytes = await get_url_content(head_img_url)
                if head_img_bytes is None:
                    await send_text("获取头像失败", room_id, sender, sender_name)
                    return
                name = meme_user_info[wx_id].get("name", "")
                image_list.append(head_img_bytes)
                args_user_infos.append({"name": name, "gender": "unknown"})
        args["user_infos"] = args_user_infos

        try:
            img_io = await asyncio.get_event_loop().run_in_executor(None, meme_call, meme, image_list, text_list, args)
        except Exception as e:
            await send_text(str(e), room_id, sender, sender_name)
            return

        img_bytes = img_io.getvalue()
        is_gif = check_image_gif(img_bytes)
        img_png = os.path.join(img_path, room_id + sender + "_meme.png")
        with open(img_png, "wb") as f:
            f.write(img_bytes)
        if is_gif:
            await send_emotion(room_id, img_png)
        else:
            await send_image(room_id, img_png)


def create_matchers():
    for meme in meme_manager.get_memes():
        handle_matchers(meme)


create_matchers()
