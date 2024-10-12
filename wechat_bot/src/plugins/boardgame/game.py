import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from common import nick_name
from browser import html_to_pic
from .svg import Svg, SvgOptions
from .gomoku_ai2 import GomokuAi2
from .go_ai import GoAi
from .othello_ai import OthelloAi


class MoveResult(Enum):
    BLACK_WIN = 1
    WHITE_WIN = -1
    DRAW = -2
    SKIP = 2
    ILLEGAL = 3


class Placement(Enum):
    CROSS = 0
    GRID = 1


class Player:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __eq__(self, player: "Player") -> bool:
        return self.id == player.id

    def __str__(self) -> str:
        return self.name


class AiPlayer(Player):
    def __init__(self):
        pass

    def move(self, x, y, player):
        pass

    def pos(self):
        pass

    def pop(self):
        pass


class GomokuAi2Player(AiPlayer):
    def __init__(self):
        self.id = "123"
        self.name = nick_name
        self.ai = GomokuAi2()

    def move(self, x, y, player):
        if player:
            self.ai.move(x, y, 2)
        else:
            self.ai.move(x, y, 1)

    def pos(self):
        _, x, y = self.ai.search(1, 1)
        return chr(ord("A") + x) + str(y + 1)

    def pop(self):
        self.ai.pop()
        self.ai.pop()


class GoAiPlayer(AiPlayer):
    def __init__(self):
        self.id = "123"
        self.name = nick_name
        self.ai = GoAi()

    def move(self, x, y, player):
        self.ai.move(y+1, x+1)

    def pos(self):
        pos_tuple = self.ai.auto()
        return chr(ord("A") + pos_tuple[1] - 1) + str(pos_tuple[0])

    def pop(self):
        self.ai.pop()
        self.ai.pop()


class OthelloAiPlayer(AiPlayer):
    def __init__(self):
        self.id = "123"
        self.name = nick_name
        self.ai = OthelloAi("O")

    def move(self, x, y, player):
        if player:
            self.ai.board.move((y, x), "X")
        else:
            self.ai.board.move((y, x), "O")
        # self.ai.board.display()

    def pos(self):
        if not list(self.ai.board.get_legal_actions("O")):
            return
        pos_tuple = self.ai.get_move(self.ai.board)
        return pos_tuple

    def pop(self):
        self.ai.board.pop()
        self.ai.board.pop()


@dataclass
class Pos:
    x: int
    y: int

    @classmethod
    def from_str(cls, s: str) -> "Pos":
        if s == "null":
            return cls.null()
        match_obj = re.fullmatch(r"([a-z])(\d+)", s, re.IGNORECASE)
        if match_obj:
            x = (ord(match_obj.group(1).lower()) - ord("a")) % 32
            y = int(match_obj.group(2)) - 1
            return cls(x, y)
        raise ValueError("坐标格式不合法！")

    @classmethod
    def null(cls) -> "Pos":
        return cls(-1, -1)

    def __str__(self) -> str:
        if self.x < 0 or self.y < 0:
            return "null"
        return chr(self.x + ord("A")) + str(self.y + 1)


@dataclass
class History:
    b_board: int
    w_board: int
    moveside: int


class Game:
    name: str = ""

    def __init__(
        self,
        size: int = 0,
        placement: Placement = Placement.CROSS,
        allow_skip: bool = False,
        allow_repent: bool = True,
    ):
        self.size: int = size
        self.placement: Placement = placement
        self.allow_skip: bool = allow_skip
        self.allow_repent: bool = allow_repent

        self.id: str = uuid.uuid4().hex
        self.start_time = datetime.now()
        self.update_time = datetime.now()
        self.is_game_over: bool = False
        self.player_white: Optional[Player] = None
        self.player_black: Optional[Player] = None
        self.is_ai: bool = False

        self.moveside: int = 1
        """1 代表黑方，-1 代表白方"""
        self.positions: List[Pos] = []
        self.history: List[History] = []
        self.b_board: int = 0
        self.w_board: int = 0
        self.area: int = self.size * self.size
        self.full: int = (1 << self.area) - 1
        self.save()

    def update(self, pos: Pos) -> Optional[MoveResult]:
        raise NotImplementedError

    @property
    def player_next(self) -> Optional[Player]:
        return self.player_black if self.moveside == 1 else self.player_white

    @property
    def player_last(self) -> Optional[Player]:
        return self.player_white if self.moveside == 1 else self.player_black

    def is_full(self):
        return not ((self.b_board | self.w_board) ^ self.full)

    def bit(self, pos: Pos) -> int:
        return 1 << (pos.x * self.size + pos.y)

    def in_range(self, pos: Pos) -> bool:
        return pos.x >= 0 and pos.y >= 0 and pos.x < self.size and pos.y < self.size

    def get(self, pos: Pos) -> int:
        bit = self.bit(pos)
        if self.b_board & bit:
            return 1
        if self.w_board & bit:
            return -1
        return 0

    def set(self, pos: Pos, value: int):
        bit = self.bit(pos)
        if value == 1:
            self.w_board &= ~bit
            self.b_board |= bit
        elif value == -1:
            self.b_board &= ~bit
            self.w_board |= bit
        else:
            self.w_board &= ~bit
            self.b_board &= ~bit

    def push(self, pos: Pos):
        if self.in_range(pos):
            self.set(pos, self.moveside)
        self.moveside = -self.moveside
        self.positions.append(pos)
        self.save()

    def save(self):
        history = History(self.b_board, self.w_board, self.moveside)
        self.history.append(history)

    def pop(self):
        self.history.pop()
        self.positions.pop()
        history = self.history[-1]
        self.b_board = history.b_board
        self.w_board = history.w_board
        self.moveside = history.moveside

    def draw_svg(self):
        size = self.size
        placement = self.placement
        view_size = size + (3 if placement == Placement.CROSS else 4)
        svg = Svg(SvgOptions(view_size=view_size, size=view_size * 50)).fill("white")

        line_group = svg.g(
            {
                "stroke": "black",
                "stroke-width": 0.08,
                "stroke-linecap": "round",
            }
        )

        text_group = svg.g(
            {
                "font-size": "0.6",
                "font-weight": "normal",
                "style": "font-family: Sans; letter-spacing: 0",
            }
        )

        top_text_group = text_group.g({"text-anchor": "middle"})
        left_text_group = text_group.g({"text-anchor": "end"})
        bottom_text_group = text_group.g({"text-anchor": "middle"})
        right_text_group = text_group.g({"text-anchor": "start"})
        mask_group = svg.g({"fill": "white"})
        black_group = svg.g({"fill": "black"})
        white_group = svg.g(
            {
                "fill": "white",
                "stroke": "black",
                "stroke-width": 0.08,
            }
        )

        vertical_offset = 0.3 if placement == Placement.CROSS else 0.8
        horizontal_offset = 0 if placement == Placement.CROSS else 0.5
        for index in range(2, view_size - 1):
            line_group.line(index, 2, index, view_size - 2)
            line_group.line(2, index, view_size - 2, index)
            if index < size + 2:
                top_text_group.text(str(index - 1), index + horizontal_offset, 1.3)
                left_text_group.text(chr(index + 63), 1.3, index + vertical_offset)
                bottom_text_group.text(
                    str(index - 1), index + horizontal_offset, view_size - 0.8
                )
                right_text_group.text(
                    chr(index + 63), view_size - 1.3, index + vertical_offset
                )

        for i in range(size):
            for j in range(size):
                value = self.get(Pos(i, j))
                if not value:
                    if (
                        size >= 13
                        and size % 2 == 1
                        and (i == 3 or i == size - 4 or i * 2 == size - 1)
                        and (j == 3 or j == size - 4 or j * 2 == size - 1)
                    ):
                        line_group.circle(j + 2, i + 2, 0.08)
                    continue

                offset = 2.5
                if placement == Placement.CROSS:
                    mask_group.rect(j + 1.48, i + 1.48, j + 2.52, i + 2.52)
                    offset = 2
                white_mark = 0.08
                black_mark = 0.12
                cx = j + offset
                cy = i + offset
                if value == 1:
                    black_group.circle(cx, cy, 0.36)
                    if self.positions:
                        pos = self.positions[-1]
                        if pos.x == i and pos.y == j:
                            black_group.rect(
                                cx - black_mark,
                                cy - black_mark,
                                cx + black_mark,
                                cy + black_mark,
                                {"fill": "white"},
                            )
                else:
                    white_group.circle(cx, cy, 0.32)
                    if self.positions:
                        pos = self.positions[-1]
                        if pos.x == i and pos.y == j:
                            white_group.rect(
                                cx - white_mark,
                                cy - white_mark,
                                cx + white_mark,
                                cy + white_mark,
                                {"fill": "black"},
                            )
        return svg

    async def draw(self) -> bytes:
        svg = self.draw_svg()
        return await html_to_pic(
            f'<html><body style="margin: 0;">{svg.outer()}</body></html>',
            viewport={"width": 100, "height": 100},
        )
