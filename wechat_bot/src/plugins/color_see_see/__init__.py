import os
import asyncio
from asyncio import TimerHandle

from on import on_regex
from common import send_text, send_image
from .data_source import ColorGame

img_path = os.path.join(os.path.dirname(__file__), "img")


games: dict[str, ColorGame] = {}
timers: dict[str, tuple[TimerHandle, int]] = {}
players: dict[str, dict[str, int]] = {}
default_difficulty = 2


@on_regex(r"^(猜色块|给我点颜色看看|给我点颜色瞧瞧)\s*(-t\s*\d+)?$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender_name = kwargs.get("sender_name")
    user_name = sender_name
    group_id = room_id
    if games.get(group_id):
        await send_text("猜色块正在游戏中，请对局结束后再开局", room_id)
        return
    game = ColorGame(default_difficulty)
    games[group_id] = game
    timeout = 60
    t_str = match_obj.groups()[-1]
    if t_str:
        timeout = int(t_str[2:].strip())
    timeout = min(timeout, 600)
    set_timeout(group_id, timeout)
    msg = f"{user_name}发起了猜色块！请发送“块+数字”，挑出颜色不同的色块，每小局{timeout}秒"
    img_png = os.path.join(img_path, room_id + "_color.png")
    with open(img_png, "wb") as f:
        f.write(game.get_color_img())
    await send_text(msg, room_id)
    await send_image(room_id, img_png)


@on_regex(r"^块\s*(\d+)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    user_id = sender
    group_id = room_id
    user_name = sender_name
    if not games.get(group_id):
        return

    block = int(match_obj.groups()[-1])
    game = games[group_id]
    if timeout := timers.get(group_id):
        timeout = timeout[1]
        set_timeout(group_id, timeout)
    if game.diff_block == block:
        game.add_score(user_id, user_name)
        img_png = os.path.join(img_path, room_id + "_color.png")
        with open(img_png, "wb") as f:
            f.write(game.get_next_img())
        await send_text(f"猜对啦，获得积分{game.block_column}分，现有积分{game.get_scores(user_id)}分", room_id, sender, sender_name)
        await send_image(room_id, img_png)


def stop_game(group_id: str):
    if timer := timers.pop(group_id, None):
        timer[0].cancel()
    games.pop(group_id, None)


async def stop_game_timeout(group_id: str):
    game = games.get(group_id, None)
    stop_game(group_id)
    if game:
        sorted_scores = dict(
            sorted(game.scores.items(), key=lambda item: item[1].score, reverse=True)
            )
        if not sorted_scores:
            await send_text(f"游戏已结束，没有玩家得分,本次答案为 块{game.get_diff_block()} 哦", group_id)
            return
        msg = f"本次答案为 块{game.get_diff_block()} 哦\n游戏结束，积分排行榜："
        for step, (_, scores) in enumerate(sorted_scores.items()):
            msg += f"\n{step + 1}.{scores.user_name}，{scores.score}分"
        await send_text(msg, group_id)


def set_timeout(group_id: str, timeout: int):
    if timer := timers.get(group_id, None):
        timer[0].cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(group_id))
    )
    timers[group_id] = (timer, timeout)
