import os
import asyncio
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .game import Game, Player, AiPlayer
from .engine import EngineError
from .move import Move
from .board import MoveResult

timers = {}
cchess_game_dict = {}
base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")


def stop_game(room_id):
    if timer := timers.pop(room_id, None):
        timer.cancel()
    cchess_game_dict.pop(room_id, None)


async def stop_game_timeout(room_id):
    t_game = cchess_game_dict.get(room_id, None)
    stop_game(room_id)
    if t_game:
        msg = "象棋超时，游戏结束"
        await send_text(msg, room_id)


def set_timeout(room_id, timeout=900):
    if timer := timers.get(room_id, None):
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(room_id))
    )
    timers[room_id] = timer


@on_regex(r"^(象棋|象棋人机|象棋单人)(lv[1-8])?$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    cchess_game: Game | None = cchess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_cchess.png")
    if cchess_game:
        color = "红" if cchess_game.moveside else "黑"
        game_img = cchess_game.draw()
        game_img.save(game_png)
        await send_image(room_id, game_png)
        await send_text(f"有正在进行的象棋游戏，轮到{color}方", room_id, sender, sender_name)
        return

    _, level = match_obj.groups()
    if level:
        level = int(level[-1])
    else:
        level = 4
    cchess_game = Game()
    player = Player(sender, sender_name)
    cchess_game.player_red = player
    try:
        ai_player = AiPlayer(level)
        await ai_player.engine.open()
    except EngineError:
        await send_text("象棋引擎加载失败，请检查设置", room_id)
        return

    cchess_game_dict[room_id] = cchess_game
    set_timeout(room_id)
    cchess_game.player_black = ai_player
    game_img = cchess_game.draw()
    game_img.save(game_png)
    await send_image(room_id, game_png)
    other = "\n当前为人机对战，如需双人对战可发送“象棋双人”"
    msg = f"{player} 发起了游戏 象棋！\n发送 中文纵线格式如“炮二平五” 或 起始坐标格式如“h2e2” 下棋{other}\n不想玩了就发送“结束象棋“"
    await send_text(msg, room_id)


@on_regex(r"^(象棋对战|象棋双人)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    cchess_game: Game | None = cchess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")
    if cchess_game:
        color = "红" if cchess_game.moveside else "黑"
        game_img = cchess_game.draw()
        game_img.save(game_png)
        await send_image(room_id, game_png)
        await send_text(f"有正在进行的象棋游戏，轮到{color}方", room_id, sender, sender_name)
        return

    cchess_game = Game()
    cchess_game_dict[room_id] = cchess_game
    set_timeout(room_id)
    player = Player(sender, sender_name)
    cchess_game.player_red = player
    game_img = cchess_game.draw()
    game_img.save(game_png)
    await send_image(room_id, game_png)
    msg = f"{player} 发起了游戏 象棋！\n发送 中文纵线格式如“炮二平五” 或 起始坐标格式如“h2e2” 下棋\n不想玩了就发送“结束象棋“"
    await send_text(msg, room_id)


@on_regex(r"^\s*\S\S[a-zA-Z平进退上下][\d一二三四五六七八九]\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    cchess_game: Game | None = cchess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")

    if not cchess_game:
        return

    player = Player(sender, sender_name)
    if (
            cchess_game.player_black
            and cchess_game.player_red
            and cchess_game.player_black != player
            and cchess_game.player_red != player
    ):
        await send_text("游戏已经开始，无法加入", room_id, sender, sender_name)
        return

    set_timeout(room_id)

    if (cchess_game.player_next and cchess_game.player_next != player) or (
            cchess_game.player_last and cchess_game.player_last == player
    ):
        await send_text("当前不是你的回合", room_id, sender, sender_name)
        return

    move_obj = match_obj.group()
    try:
        move_obj = Move.from_ucci(move_obj)
    except ValueError:
        try:
            move_obj = Move.from_chinese(cchess_game, move_obj)
        except ValueError:
            await send_text("请发送正确的走法，如 “炮二平五” 或 “h2e2”", room_id, sender, sender_name)
            return

    try:
        move_str = move_obj.chinese(cchess_game)
    except ValueError:
        await send_text("不正确的走法", room_id, sender, sender_name)
        return

    result = cchess_game.push(move_obj)
    if result == MoveResult.ILLEAGAL:
        await send_text("不正确的走法", room_id, sender, sender_name)
        return
    elif result == MoveResult.CHECKED:
        await send_text("该走法将导致被将军或白脸将", room_id, sender, sender_name)
        return

    if not cchess_game.player_last:
        if not cchess_game.player_red:
            cchess_game.player_red = player
        elif not cchess_game.player_black:
            cchess_game.player_black = player
        msg = f"{player} 加入了游戏并下出 {move_str}"
    else:
        player.id = sender
        player.name = sender_name
        msg = f"{player} 下出 {move_str}"

    if result == MoveResult.RED_WIN:
        if cchess_game.is_battle:
            msg += f"，恭喜 {cchess_game.player_red} 获胜！"
        else:
            msg += "，恭喜你赢了！" if player == cchess_game.player_red else "，很遗憾你输了！"
        cchess_game.close_engine()
        cchess_game_dict.pop(room_id)
    elif result == MoveResult.BLACK_WIN:
        if cchess_game.is_battle:
            msg += f"，恭喜 {cchess_game.player_black} 获胜！"
        else:
            msg += "，恭喜你赢了！" if player == cchess_game.player_black else "，很遗憾你输了！"
        cchess_game.close_engine()
        cchess_game_dict.pop(room_id)
    elif result == MoveResult.DRAW:
        msg += f"，本局游戏平局"
    else:
        if cchess_game.player_next and cchess_game.is_battle:
            msg += f"，下一手轮到 {cchess_game.player_next}"

    if not cchess_game:
        pass
    elif cchess_game.is_battle:
        pass
    else:
        if not result:
            ai_player = cchess_game.player_next
            assert isinstance(ai_player, AiPlayer)
            move_obj = await ai_player.get_move(cchess_game.position())
            move_chi = move_obj.chinese(cchess_game)
            result = cchess_game.push(move_obj)

            msg += f"\n{ai_player} 下出 {move_chi}"
            if result == MoveResult.ILLEAGAL:
                cchess_game.close_engine()
                cchess_game_dict.pop(room_id)
                await send_text("象棋引擎出错，请结束游戏或稍后再试", room_id)
                return
            elif result:
                if result == MoveResult.CHECKED:
                    msg += "，恭喜你赢了！"
                elif result == MoveResult.RED_WIN:
                    msg += "，恭喜你赢了！" if player == cchess_game.player_red else "，很遗憾你输了！"
                elif result == MoveResult.BLACK_WIN:
                    msg += "，恭喜你赢了！" if player == cchess_game.player_black else "，很遗憾你输了！"
                elif result == MoveResult.DRAW:
                    msg += f"，本局游戏平局"
                cchess_game.close_engine()
                cchess_game_dict.pop(room_id)

    game_img = cchess_game.draw()
    game_img.save(game_png)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^(象棋)?悔棋$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    cchess_game: Game | None = cchess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")

    if not cchess_game:
        return

    set_timeout(room_id)

    if len(cchess_game.history) <= 1:
        await send_text("对局尚未开始", room_id, sender, sender_name)
        return

    player = Player(sender, sender_name)
    if cchess_game.is_battle:
        if cchess_game.player_last and cchess_game.player_last != player:
            await send_text("上一手棋不是你所下", room_id, sender, sender_name)
            return
        cchess_game.pop()
    else:
        if len(cchess_game.history) <= 2:
            await send_text("对局尚未开始", room_id, sender, sender_name)
            return
        cchess_game.pop()
        cchess_game.pop()

    game_img = cchess_game.draw()
    game_img.save(game_png)
    await send_image(room_id, game_png)
    await send_text(f"{player} 进行了悔棋", room_id)


@on_regex(r"^(结束游戏|结束象棋|结束象棋游戏)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    cchess_game: Game | None = cchess_game_dict.get(room_id)

    if not cchess_game:
        return

    player = Player(sender, sender_name)
    if (not cchess_game.player_red or cchess_game.player_red != player) and (
            not cchess_game.player_black or cchess_game.player_black != player
    ):
        await send_text("只有游戏参与者才能结束游戏", room_id, sender, sender_name)
        return

    stop_game(room_id)
    cchess_game.close_engine()
    await send_text("象棋游戏已结束", room_id, sender, sender_name)
