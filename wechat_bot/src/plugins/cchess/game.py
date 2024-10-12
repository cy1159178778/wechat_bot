import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from common import nick_name
from .move import Move
from .board import Board
from .engine import UCCIEngine


base_path = Path(__file__).parent


class Player:
    def __init__(self, user_id: str, name: str):
        self.id = user_id
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
        self.engine = UCCIEngine(base_path / "fairy-stockfish.exe")
        time_list = [100, 400, 700, 1000, 1500, 2000, 3000, 5000]
        self.time = time_list[level - 1]
        depth_list = [5, 5, 5, 5, 8, 12, 17, 25]
        self.depth = depth_list[level - 1]

    async def get_move(self, position: str) -> Move:
        return await self.engine.bestmove(position, time=self.time, depth=self.depth)


class Game(Board):
    def __init__(self):
        super().__init__()
        self.player_red: Optional[Player] = None
        self.player_black: Optional[Player] = None
        self.id = uuid.uuid4().hex
        self.start_time = datetime.now()
        self.update_time = datetime.now()

    @property
    def player_next(self) -> Optional[Player]:
        return self.player_red if self.moveside else self.player_black

    @property
    def player_last(self) -> Optional[Player]:
        return self.player_black if self.moveside else self.player_red

    @property
    def is_battle(self) -> bool:
        return not isinstance(self.player_red, AiPlayer) and not isinstance(
            self.player_black, AiPlayer
        )

    def close_engine(self):
        if isinstance(self.player_red, AiPlayer):
            self.player_red.engine.close()
        if isinstance(self.player_black, AiPlayer):
            self.player_black.engine.close()
