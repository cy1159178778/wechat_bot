import random
from typing import Iterable, List, TypeVar

T = TypeVar("T")


def random_pick_big(sequence: Iterable[T], relative_odds: List[int]):
    """
    sequence: [a, b, c, d]
    relative_odds: [pa, pb, pc, pd], 其中 pa~pd > 0
    """
    table = [z for x, y in zip(sequence, relative_odds) for z in [x] * y]
    while True:
        yield random.choice(table)


def random_pick_small(some_list: List[T], probabilities: List[float]) -> T:
    """
    some_list: [a, b, c, d]
    probabilities: [pa, pb, pc, pd], 其中 0 < pa ~ pd < 1
    """
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    item = some_list[0]
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            break
    return item
