import os
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .minesweeper import MineSweeperManager

msm = MineSweeperManager()
base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")


@on_regex(r"^扫雷\s*(初级|中级|高级)?$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    level = match_obj.group(1) or "初级"
    game_img, msg = msm.start_game(room_id, level)
    game_png = os.path.join(img_path, room_id + "_mine.png")
    game_img.save(game_png)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^挖开\s*(.*)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    open_positions_str = match_obj.group(1).strip()
    game_img, msgs = msm.open_mine(room_id, open_positions_str)
    if not game_img:
        return
    for i in range(0, len(msgs), 30):
        await send_text("\n".join(msgs[i:i+30]), room_id)
    game_png = room_id + "_mine.png"
    game_png = os.path.join(img_path, game_png)
    game_img.save(game_png)
    await send_image(room_id, game_png)


@on_regex(r"^标记\s*(.*)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    mark_positions_str = match_obj.group(1).strip()
    game_img, msgs = msm.sign_mine(room_id, mark_positions_str)
    if not game_img:
        return
    for i in range(0, len(msgs), 30):
        await send_text("\n".join(msgs[i:i+30]), room_id)
    game_png = room_id + "_mine.png"
    game_png = os.path.join(img_path, game_png)
    game_img.save(game_png)
    await send_image(room_id, game_png)


@on_regex(r"^(结束游戏|结束扫雷|结束扫雷游戏)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    if not msm.games.get(room_id):
        return
    msg = msm.stop_game(room_id)
    await send_text(msg, room_id, sender, sender_name)
