import os
import asyncio
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .game import Game, Player, AiPlayer
from .game import Game as BoardGame, MoveResult as BoardMoveResult, Player, Pos
from .game import AiPlayer, GomokuAi2Player, GoAiPlayer, OthelloAiPlayer
from .go import Go
from .gomoku import Gomoku
from .othello import Othello


timers = {}
board_game_dict = {}
base_path = Path(__file__).parent
img_path = os.path.join(base_path, "img")
board_dict = {"五子棋": Gomoku, "黑白棋": Othello, "围棋": Go}
board_ai_dict = {"五子棋": GomokuAi2Player, "黑白棋": OthelloAiPlayer, "围棋": GoAiPlayer}


def stop_game(room_id):
    if timer := timers.pop(room_id, None):
        timer.cancel()
    board_game_dict.pop(room_id, None)


async def stop_game_timeout(room_id):
    t_game = board_game_dict.get(room_id, None)
    stop_game(room_id)
    if t_game:
        msg = f"{t_game.name}超时，游戏结束"
        await send_text(msg, room_id)


def set_timeout(room_id, timeout=900):
    if timer := timers.get(room_id, None):
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game_timeout(room_id))
    )
    timers[room_id] = timer


@on_regex(r"^(五子棋|黑白棋|围棋)(|人机|双人)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    board_game: BoardGame | None = board_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_board.png")

    if board_game:
        color = "黑" if board_game.moveside == 1 else "白"
        img_bytes = await board_game.draw()
        with open(game_png, "wb") as f:
            f.write(img_bytes)
        await send_image(room_id, game_png)
        await send_text(f"有正在进行的{board_game.name}游戏，轮到{color}方", room_id, sender, sender_name)
        return
    board_game_name, sign = match_obj.groups()
    board_game = board_dict[board_game_name]()
    board_game_dict[room_id] = board_game
    set_timeout(room_id)
    player = Player(sender, sender_name)
    board_game.player_black = player
    if sign != "双人":
        board_game.player_white = board_ai_dict[board_game_name]()
        board_game.is_ai = True
    tiao = ""
    if board_game.name == "黑白棋":
        tiao = "\n发送“跳过”可以跳过自己的回合"
    other = ""
    if board_game.is_ai:
        other = f"\n当前为人机对战，如需双人对战可发送“{board_game.name}双人”"
    msg = f"{player} 发起了游戏 {board_game.name}！\n发送“落子 字母+数字”下棋，如“落子 A1”{tiao}{other}\n不想玩了就发送“结束{board_game.name}”"

    img_bytes = await board_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^落子\s*([A-Za-z]\d+)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    board_game: BoardGame | None = board_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_board.png")

    if not board_game:
        return

    player = Player(sender, sender_name)
    if (
        board_game.player_black
        and board_game.player_white
        and board_game.player_black != player
        and board_game.player_white != player
    ):
        await send_text("游戏已经开始，无法加入", room_id, sender, sender_name)
        return

    set_timeout(room_id)

    if (board_game.player_next and board_game.player_next != player) or (
        board_game.player_last and board_game.player_last == player
    ):
        await send_text("当前不是你的回合", room_id, sender, sender_name)
        return

    position = match_obj.groups()[-1]
    try:
        pos = Pos.from_str(position)
    except ValueError:
        await send_text("请发送正确的坐标", room_id, sender, sender_name)
        return

    if not board_game.in_range(pos):
        await send_text("落子超出边界", room_id, sender, sender_name)
        return

    if board_game.get(pos):
        await send_text("此处已有落子", room_id, sender, sender_name)
        return

    try:
        result = board_game.update(pos)
    except ValueError as e:
        await send_text(f"非法落子：{e}", room_id, sender, sender_name)
        return

    msg = ""
    last = False
    if board_game.player_last:
        last = True
        msg += f"{player} 落子于 {pos}"
    else:
        if not board_game.player_black:
            board_game.player_black = player
        elif not board_game.player_white:
            board_game.player_white = player
        msg += f"{player} 加入了游戏并落子于 {pos}"

    if result == BoardMoveResult.ILLEGAL:
        await send_text(f"非法落子", room_id, sender, sender_name)
        return
    elif result == BoardMoveResult.SKIP:
        msg += f"，下一手依然轮到 {player}\n"
    elif result:
        board_game.is_game_over = True
        if result == BoardMoveResult.BLACK_WIN:
            msg += f"，恭喜 {board_game.player_black} 获胜！\n"
        elif result == BoardMoveResult.WHITE_WIN:
            msg += f"，恭喜 {board_game.player_white} 获胜！\n"
        elif result == BoardMoveResult.DRAW:
            msg += "，本局游戏平局\n"
        board_game_dict.pop(room_id)
    else:
        if not board_game.is_ai and last and board_game.player_next:
            msg += f"，下一手轮到 {board_game.player_next}\n"
        if board_game.is_ai:
            ai_player: AiPlayer = board_game.player_white
            try:
                ai_player.move(pos.x, pos.y, True)
                # ai_pos = ai_player.pos()
                ai_pos = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, ai_player.pos), 30)
                if ai_pos is None:
                    pos = None
                else:
                    pos = Pos.from_str(ai_pos)
                # print("ai:", ai_pos)
            except:
                pos = None
                if board_game.name != "黑白棋":
                    await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                    return
            if pos is None:
                board_game.update(Pos.null())
                msg += f"\n{ai_player} 选择跳过其回合"
            else:
                if not board_game.in_range(pos) or board_game.get(pos):
                    await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                    return
                try:
                    result = board_game.update(pos)
                except ValueError:
                    await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                    return
                if result == BoardMoveResult.ILLEGAL:
                    await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                    return

                msg += f"\n{ai_player} 落子于 {pos}"
                ai_player.move(pos.x, pos.y, False)
                if result:
                    board_game.is_game_over = True
                    if result == BoardMoveResult.BLACK_WIN:
                        msg += f"，恭喜你赢了！\n"
                    elif result == BoardMoveResult.WHITE_WIN:
                        msg += f"，很遗憾你输了！\n"
                    elif result == BoardMoveResult.DRAW:
                        msg += "，本局游戏平局\n"
                    board_game_dict.pop(room_id)

    img_bytes = await board_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^跳过$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    board_game: BoardGame | None = board_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_board.png")

    if not board_game:
        return

    if not board_game.allow_skip:
        await send_text("当前游戏不允许跳过回合", room_id, sender, sender_name)
        return

    player = Player(sender, sender_name)
    if board_game.player_next and board_game.player_next != player:
        await send_text("当前不是你的回合", room_id, sender, sender_name)
        return

    set_timeout(room_id)
    board_game.update(Pos.null())
    msg = f"{player} 选择跳过其回合"
    if board_game.player_next and not board_game.is_ai:
        msg += f"，下一手轮到 {board_game.player_next}"
    if board_game.is_ai:
        ai_player: AiPlayer = board_game.player_white
        try:
            # ai_pos = ai_player.pos()
            ai_pos = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, ai_player.pos), 30)
            if ai_pos is None:
                pos = None
            else:
                pos = Pos.from_str(ai_pos)
            # print("ai:", ai_pos)
        except:
            pos = None
            if board_game.name != "黑白棋":
                await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                return
        if pos is None:
            board_game.update(Pos.null())
            msg += f"\n{ai_player} 选择跳过其回合"
        else:
            if not board_game.in_range(pos) or board_game.get(pos):
                await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                return
            try:
                result = board_game.update(pos)
            except ValueError:
                await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                return
            if result == BoardMoveResult.ILLEGAL:
                await send_text(f"{board_game.name}引擎出错，请结束游戏或稍后再试", room_id)
                return

            msg += f"\n{ai_player} 落子于 {pos}"
            ai_player.move(pos.x, pos.y, False)
            if result:
                board_game.is_game_over = True
                if result == BoardMoveResult.BLACK_WIN:
                    msg += f"，恭喜你赢了！\n"
                elif result == BoardMoveResult.WHITE_WIN:
                    msg += f"，很遗憾你输了！\n"
                elif result == BoardMoveResult.DRAW:
                    msg += "，本局游戏平局\n"
                board_game_dict.pop(room_id)

    img_bytes = await board_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^(五子棋|黑白棋|围棋)?悔棋$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    board_game: BoardGame | None = board_game_dict.get(room_id)
    game_png = os.path.join(img_path, room_id + "_board.png")

    if not board_game:
        return

    set_timeout(room_id)
    if len(board_game.history) <= 1:
        await send_text("对局尚未开始", room_id, sender, sender_name)
        return

    player = Player(sender, sender_name)
    if board_game.is_ai:
        if len(board_game.history) <= 2:
            await send_text("对局尚未开始", room_id, sender, sender_name)
            return
        board_game.pop()
        board_game.pop()
        ai_player: AiPlayer = board_game.player_white
        ai_player.pop()
    else:
        if board_game.player_last and board_game.player_last != player:
            await send_text("上一手棋不是你所下", room_id, sender, sender_name)
            return
        board_game.pop()

    msg = f"{player} 进行了悔棋"
    img_bytes = await board_game.draw()
    with open(game_png, "wb") as f:
        f.write(img_bytes)
    await send_image(room_id, game_png)
    await send_text(msg, room_id)


@on_regex(r"^(结束游戏|结束(五子棋|黑白棋|围棋)|结束(五子棋|黑白棋|围棋)游戏)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    board_game: BoardGame | None = board_game_dict.get(room_id)

    if not board_game:
        return

    if board_game.name not in match_obj.group():
        return

    player = Player(sender, sender_name)
    if board_game.player_black != player and board_game.player_white != player:
        await send_text("只有游戏参与者才能结束游戏", room_id, sender, sender_name)
        return

    stop_game(room_id)
    await send_text(f"{board_game.name}游戏已结束", room_id, sender, sender_name)
