from dataclasses import dataclass
from typing import NamedTuple, List, TypedDict


class UpdateChar(NamedTuple):
    name: str
    limit: bool
    chance: float


@dataclass
class UpdateInfo:
    title: str
    start: int
    end: int
    four_chars: List[UpdateChar]
    five_chars: List[UpdateChar]
    six_chars: List[UpdateChar]
    pool: str


class GachaPoolInfo(TypedDict):
    gachaPoolId: str
    gachaIndex: int
    openTime: int
    endTime: int
    gachaPoolName: str
    gachaRuleType: str


class CarouselInfo(TypedDict):
    poolId: str
    index: int
    startTime: int
    endTime: int
    spriteId: str


class FreeGachaInfo(TypedDict):
    poolId: str
    openTime: int
    endTime: int
    freeCount: int


class GachaTableIndex(TypedDict):
    gachaPoolClient: List[GachaPoolInfo]
    carousel: List[CarouselInfo]
    freeGacha: List[FreeGachaInfo]


class LimitedWUChar(TypedDict):
    rarityRank: int
    charId: str
    weight: int


class PerAvail(TypedDict):
    charIdList: List[str]
    rarityRank: int
    totalPercent: int


class AvailCharInfo(TypedDict):
    perAvailList: List[PerAvail]


class PerUpChar(TypedDict):
    charIdList: List[str]
    count: int
    percent: int
    rarityRank: int


class PerUpCharInfo(TypedDict):
    perCharList: List[PerUpChar]


class PoolDetail(TypedDict):
    availCharInfo: AvailCharInfo
    upCharInfo: PerUpCharInfo
    weightUpCharInfoList: List[LimitedWUChar]
    limitedChar: List[str]
    gachaObjGroupType: int


class GachaTableDetail(TypedDict):
    detailInfo: PoolDetail


class GachaTableDetails(TypedDict):
    gachaPoolDetail: GachaTableDetail
    gachaPoolId: str
