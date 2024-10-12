import re
from .data_source import MineSweeper, GameState, OpenResult, MarkResult
from typing import Dict, Tuple, Optional
from asyncio import TimerHandle


class MineSweeperManager:
    level_info = {"初级": (8, 8, 10), "中级": (16, 16, 40), "高级": (16, 30, 99)}
    games: Dict[str, MineSweeper] = {}
    timers: Dict[str, TimerHandle] = {}
    help_msg = "使用 “挖开”+位置 挖开方块，使用 “标记”+位置 标记方块，可同时加多个位置，如：“挖开 A1 B2”\n不想玩了就发送“结束游戏”"

    def start_game(self, roomid, level):
        game = self.games.get(roomid)
        if game:
            return game.draw(), self.help_msg

        game = MineSweeper(*self.level_info.get(level))
        self.games[roomid] = game
        return game.draw(), self.help_msg

    def stop_game(self, roomid):
        game = self.games.get(roomid)
        if not game:
            return "没有正在进行的扫雷游戏"

        self.games.pop(roomid)
        return "扫雷游戏已结束"

    @staticmethod
    def check_position(position: str) -> Optional[Tuple[int, int]]:
        match_obj = re.match(r"^([a-z])(\d+)$", position, re.IGNORECASE)
        if match_obj:
            x = (ord(match_obj.group(1).lower()) - ord("a")) % 32
            y = int(match_obj.group(2)) - 1
            return x, y

    def open_mine(self, roomid, open_positions_str):
        open_positions_str = open_positions_str.strip()
        if not open_positions_str:
            return None, [self.help_msg]

        open_positions = open_positions_str.split()
        game = self.games.get(roomid)
        if not game:
            return None, ["没有正在进行的游戏"]

        msgs = []
        for position in open_positions:
            pos = self.check_position(position)
            if not pos:
                msgs.append(f"位置 {position} 不合法，须为 字母+数字 的组合")
                continue
            res = game.open(pos[0], pos[1])
            if res in [OpenResult.WIN, OpenResult.FAIL]:
                msg = ""
                if game.state == GameState.WIN:
                    msg = "恭喜你获得游戏胜利！"
                elif game.state == GameState.FAIL:
                    msg = "很遗憾，游戏失败"
                self.games.pop(roomid)
                return game.draw(), [msg]
            elif res == OpenResult.OUT:
                msgs.append(f"位置 {position} 超出边界")
            elif res == OpenResult.DUP:
                msgs.append(f"位置 {position} 已经被挖过了")

        return game.draw(), msgs

    def sign_mine(self, roomid, mark_positions_str):
        mark_positions_str = mark_positions_str.strip()
        mark_positions = mark_positions_str.split()
        if not mark_positions:
            return None, [self.help_msg]

        game = self.games.get(roomid)
        if not game:
            return None, ["没有正在进行的游戏"]

        msgs = []
        for position in mark_positions:
            pos = self.check_position(position)
            if not pos:
                msgs.append(f"位置 {position} 不合法，须为 字母+数字 的组合")
                continue
            res = game.mark(pos[0], pos[1])
            if res == MarkResult.WIN:
                self.games.pop(roomid)
                msg = "恭喜你获得游戏胜利！"
                return game.draw(), [msg]
            elif res == MarkResult.OUT:
                msgs.append(f"位置 {position} 超出边界")
            elif res == MarkResult.OPENED:
                msgs.append(f"位置 {position} 已经被挖开了，不能标记")

        return game.draw(), msgs
