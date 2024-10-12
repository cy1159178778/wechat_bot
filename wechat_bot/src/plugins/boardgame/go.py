from typing import List, Optional

from .game import Game, MoveResult, Pos

directions = ((-1, 0), (1, 0), (0, -1), (0, 1))


class Go(Game):
    name: str = "围棋"

    def __init__(self):
        super().__init__(size=19)

    def find_eaten(self, pos: Pos) -> int:
        value = self.get(pos)
        if not value:
            return False
        found = 0

        def find_life(pos: Pos) -> bool:
            nonlocal found
            found |= self.bit(pos)
            points: List[Pos] = []
            for dx, dy in directions:
                p = Pos(pos.x + dx, pos.y + dy)
                if not self.in_range(p) or (found & self.bit(p)):
                    continue
                next = self.get(p)
                if not next:
                    return True
                if next == -value:
                    continue
                if next == value:
                    points.append(p)
            for p in points:
                if find_life(p):
                    return True
            return False

        return 0 if find_life(pos) else found

    def update(self, pos: Pos) -> Optional[MoveResult]:
        moveside = self.moveside
        self.push(pos)

        diff = 0
        for dx, dy in directions:
            p = Pos(pos.x + dx, pos.y + dy)
            if not self.in_range(p):
                continue
            if self.get(p) == -moveside:
                diff |= self.find_eaten(p)

        if diff:
            if moveside == 1:
                self.w_board ^= diff
            else:
                self.b_board ^= diff
        elif self.find_eaten(pos):
            self.pop()
            raise ValueError("不入子")

        for history in self.history[1:-1]:
            if (
                history.b_board
                and self.b_board == history.b_board
                and history.w_board
                and self.w_board == history.w_board
            ):
                self.pop()
                raise ValueError("全局同形")
