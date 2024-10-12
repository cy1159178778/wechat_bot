from typing import Optional

from .game import Game, MoveResult, Pos


class Gomoku(Game):
    name: str = "五子棋"

    def __init__(self):
        super().__init__(size=15)

    def update(self, pos: Pos) -> Optional[MoveResult]:
        size = self.size
        moveside = self.moveside
        self.push(pos)
        board = self.b_board if moveside == 1 else self.w_board

        v_count = 1
        h_count = 1
        m_count = 1
        p_count = 1

        x = pos.x
        y = pos.y
        for i in range(x - 1, -1, -1):
            if not (board & self.bit(Pos(i, y))):
                break
            v_count += 1
        for i in range(x + 1, size):
            if not (board & self.bit(Pos(i, y))):
                break
            v_count += 1
        if v_count >= 5:
            return MoveResult(moveside)

        for j in range(y - 1, -1, -1):
            if not (board & self.bit(Pos(x, j))):
                break
            h_count += 1
        for j in range(y + 1, size):
            if not (board & self.bit(Pos(x, j))):
                break
            h_count += 1
        if h_count >= 5:
            return MoveResult(moveside)

        i = x - 1
        j = y - 1
        while i >= 0 and j >= 0 and board & self.bit(Pos(i, j)):
            m_count += 1
            i -= 1
            j -= 1
        i = x + 1
        j = y + 1
        while i < size and j < size and board & self.bit(Pos(i, j)):
            m_count += 1
            i += 1
            j += 1
        if m_count >= 5:
            return MoveResult(moveside)

        i = x - 1
        j = y + 1
        while i >= 0 and j < size and board & self.bit(Pos(i, j)):
            p_count += 1
            i -= 1
            j += 1
        i = x + 1
        j = y - 1
        while i < size and j >= 0 and board & self.bit(Pos(i, j)):
            p_count += 1
            i += 1
            j -= 1
        if p_count >= 5:
            return MoveResult(moveside)

        if self.is_full():
            return MoveResult.DRAW
