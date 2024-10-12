import uuid
import chess
import chess.svg
import chess.engine
from chess import Board, Move
from datetime import datetime
from typing import Optional
from pathlib import Path

from common import nick_name
from browser import html_to_pic


base_path = Path(__file__).parent


class Player:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __eq__(self, player: "Player") -> bool:
        return self.id == player.id

    def __str__(self) -> str:
        return self.name


class AiPlayer(Player):
    def __init__(self, level: int = 4):
        self.level = level
        self.id = 1000 + level
        self.name = f"{nick_name}lv.{level}"
        self.engine_path = base_path / "stockfish.exe"
        time_list = [50, 100, 150, 200, 300, 400, 500, 1000]
        self.time = time_list[level - 1] / 1000
        depth_list = [5, 5, 5, 5, 5, 8, 13, 22]
        self.depth = depth_list[level - 1]

    async def open_engine(self):
        if not self.engine_path.exists():
            raise FileNotFoundError("找不到UCI引擎！")
        _, engine = await chess.engine.popen_uci(str(self.engine_path))
        self.engine = engine

    async def get_move(self, board: Board) -> Optional[Move]:
        result = await self.engine.play(
            board, chess.engine.Limit(time=self.time, depth=self.depth)
        )
        return result.move

    async def close_engine(self):
        await self.engine.quit()


class Game:
    def __init__(self):
        self.board = Board()
        self.player_white: Optional[Player] = None
        self.player_black: Optional[Player] = None
        self.id = uuid.uuid4().hex
        self.start_time = datetime.now()
        self.update_time = datetime.now()

    @property
    def player_next(self) -> Optional[Player]:
        return (
            self.player_white if self.board.turn == chess.WHITE else self.player_black
        )

    @property
    def player_last(self) -> Optional[Player]:
        return (
            self.player_black if self.board.turn == chess.WHITE else self.player_white
        )

    @property
    def is_battle(self) -> bool:
        return not isinstance(self.player_white, AiPlayer) and not isinstance(
            self.player_black, AiPlayer
        )

    async def close_engine(self):
        if isinstance(self.player_white, AiPlayer):
            await self.player_white.close_engine()
        if isinstance(self.player_black, AiPlayer):
            await self.player_black.close_engine()

    async def draw(self) -> bytes:
        lastmove = self.board.move_stack[-1] if self.board.move_stack else None
        check = lastmove.to_square if lastmove and self.board.is_check() else None
        orientation = (
            self.board.turn
            if self.is_battle
            else chess.WHITE
            if isinstance(self.player_black, AiPlayer)
            else chess.BLACK
        )
        svg = chess.svg.board(
            self.board,
            orientation=orientation,
            lastmove=lastmove,
            check=check,
            size=1000,
        )
        return await html_to_pic(
            f'<html><body style="margin: 0;">{svg}</body></html>',
            viewport={"width": 100, "height": 100},
        )
