from dataclasses import dataclass, field
from typing import Dict, List, NamedTuple, TypedDict


class Operator(NamedTuple):
    name: str
    rarity: int


class GachaData(TypedDict):
    name: str
    six_per: float
    five_per: float
    four_per: float
    operators: Dict[str, List[str]]  # 当期新 up 的干员不应该在里面
    up_limit: List[str]
    up_alert_limit: List[str]
    up_six_list: List[str]
    up_five_list: List[str]
    up_four_list: List[str]


@dataclass
class GachaUser:
    six_per: int = field(default=2)
    six_statis: int = field(default=0)
