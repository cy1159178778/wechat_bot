import os
import asyncio
import chess
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .game import Game, Player, AiPlayer


timers = {}
chess_game_dict = {}
base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")


def stop_game(room_id):
    if timer := timers.pop(room_id, None):
        timer.cancel()
    chess_game_dict.pop(room_id, None)


async def stop_game_timeout(room_id):
    t_game = chess_game_dict.get(room_id, None)
    stop_game(room_id)
    if t_game:
        msg = "国际象棋超时，游戏结束"
        await send_text(msg, room_id)


def set_timeout(room_id, timeout=900):
    if timer := timers.get(room_id, None):
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(room_id))
    )
    timers[room_id] = timer


@on_regex(r"^(国际象棋|国际象棋人机|国际象棋单人)(lv[1-8])?$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    chess_game: Game | None = chess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")

    if chess_game:
        color = "白" if chess_game.board.turn else "黑"
        img_bytes = await chess_game.draw()
        with open(game_png, "wb") as f:
            f.write(img_bytes)
        await send_image(room_id, game_png)
        await send_text(f"有正在进行的国际象棋游戏，轮到{color}方", room_id, sender, sender_name)
        return

    _, level = match_obj.groups()
    if level:
        level = int(level[-1])
    else:
        level = 4
    chess_game = Game()
    player = Player(sender, sender_name)
    chess_game.player_white = player
    try:
        ai_player = AiPlayer(level)
        await ai_player.open_engine()
    except:
        await send_text("国际象棋引擎加载失败，请检查设置", room_id)
        return

    chess_game_dict[room_id] = chess_game
    set_timeout(room_id)
    chess_game.player_black = ai_player
    img_bytes = await chess_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    other = "\n当前为人机对战，如需双人对战可发送“国际象棋双人”"
    msg = f"{player} 发起了游戏 国际象棋！\n发送 起始坐标格式 如“e2e4”下棋，在坐标后加棋子字母表示升变，如“e7e8q”{other}\n不想玩了就发送“结束国际象棋”"
    await send_text(msg, room_id)


@on_regex(r"^(国际象棋对战|国际象棋双人)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    chess_game: Game | None = chess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")

    if chess_game:
        color = "白" if chess_game.board.turn else "黑"
        img_bytes = await chess_game.draw()
        with open(game_png, "wb") as f:
            f.write(img_bytes)
        await send_image(room_id, game_png)
        return send_text(f"有正在进行的国际象棋游戏，轮到{color}方", room_id, sender, sender_name)

    chess_game = Game()
    chess_game_dict[room_id] = chess_game
    set_timeout(room_id)
    player = Player(sender, sender_name)
    chess_game.player_white = player
    img_bytes = await chess_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    msg = f"{player} 发起了游戏 国际象棋！\n发送 起始坐标格式 如“e2e4”下棋，在坐标后加棋子字母表示升变，如“e7e8q”\n不想玩了就发送“结束国际象棋”"
    await send_text(msg, room_id)


@on_regex(r"^\s*[a-zA-Z]\d[a-zA-Z]\d[a-zA-Z]?\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    chess_game: Game | None = chess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")

    if not chess_game:
        return

    player = Player(sender, sender_name)
    if (
            chess_game.player_black
            and chess_game.player_white
            and chess_game.player_black != player
            and chess_game.player_white != player
    ):
        await send_text("游戏已经开始，无法加入", room_id, sender, sender_name)
        return

    set_timeout(room_id)

    if (chess_game.player_next and chess_game.player_next != player) or (
            chess_game.player_last and chess_game.player_last == player
    ):
        await send_text("当前不是你的回合", room_id, sender, sender_name)
        return

    move = match_obj.group()
    try:
        chess_game.board.push_uci(move.lower())
        result = chess_game.board.outcome()
    except ValueError:
        await send_text("不正确的走法", room_id, sender, sender_name)
        return

    if not chess_game.player_last:
        if not chess_game.player_white:
            chess_game.player_white = player
        elif not chess_game.player_black:
            chess_game.player_black = player
        msg = f"{player} 加入了游戏并下出 {move}"
    else:
        msg = f"{player} 下出 {move}"

    if chess_game.board.is_game_over():
        chess_game_dict.pop(room_id)
        await chess_game.close_engine()
        if result == chess.Termination.CHECKMATE:
            winner = result.winner
            assert winner is not None
            if chess_game.is_battle:
                msg += (
                    f"，恭喜 {chess_game.player_white} 获胜！"
                    if winner == chess.WHITE
                    else f"，恭喜 {chess_game.player_black} 获胜！"
                )
            else:
                msg += "，恭喜你赢了！" if chess_game.board.turn == (not winner) else "，很遗憾你输了！"
        elif result in [chess.Termination.INSUFFICIENT_MATERIAL, chess.Termination.STALEMATE]:
            msg += f"，本局游戏平局"
        else:
            msg += f"，游戏结束"
    else:
        if chess_game.player_next and chess_game.is_battle:
            msg += f"，下一手轮到 {chess_game.player_next}"

    if not chess_game.is_battle:
        if not chess_game.board.is_game_over():
            ai_player = chess_game.player_next
            assert isinstance(ai_player, AiPlayer)
            try:
                move = await ai_player.get_move(chess_game.board)
                if not move:
                    await send_text("国际象棋引擎出错，请结束游戏或稍后再试", room_id)
                    return
                chess_game.board.push_uci(move.uci())
                result = chess_game.board.outcome()
            except:
                await send_text("国际象棋引擎出错，请结束游戏或稍后再试", room_id)
                return

            msg += f"\n{ai_player} 下出 {move}"
            if chess_game.board.is_game_over():
                chess_game_dict.pop(room_id)
                await chess_game.close_engine()
                if result == chess.Termination.CHECKMATE:
                    winner = result.winner
                    assert winner is not None
                    msg += "，恭喜你赢了！" if chess_game.board.turn == (not winner) else "，很遗憾你输了！"
                elif result in [chess.Termination.INSUFFICIENT_MATERIAL, chess.Termination.STALEMATE]:
                    msg += f"，本局游戏平局"
                else:
                    msg += f"，游戏结束"

    img_bytes = await chess_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^(国际象棋)?悔棋$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    chess_game: Game | None = chess_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_chess.png")

    if not chess_game:
        return

    if len(chess_game.board.move_stack) <= 0:
        await send_text("对局尚未开始", room_id, sender, sender_name)
        return

    player = Player(sender, sender_name)
    if chess_game.is_battle:
        if chess_game.player_last and chess_game.player_last != player:
            await send_text("上一手棋不是你所下", room_id, sender, sender_name)
            return
        chess_game.board.pop()
    else:
        if len(chess_game.board.move_stack) <= 1:
            await send_text("对局尚未开始", room_id, sender, sender_name)
            return
        chess_game.board.pop()
        chess_game.board.pop()

    img_bytes = await chess_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    await send_text(f"{player} 进行了悔棋", room_id)


@on_regex(r"^(结束游戏|结束国际象棋|结束国际象棋游戏)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    chess_game: Game | None = chess_game_dict.get(room_id)

    if not chess_game:
        return

    player = Player(sender, sender_name)
    if (not chess_game.player_white or chess_game.player_white != player) and (
            not chess_game.player_black or chess_game.player_black != player
    ):
        await send_text("只有游戏参与者才能结束游戏", room_id, sender, sender_name)
        return

    stop_game(room_id)
    await chess_game.close_engine()
    await send_text("国际象棋游戏已结束", room_id, sender, sender_name)
