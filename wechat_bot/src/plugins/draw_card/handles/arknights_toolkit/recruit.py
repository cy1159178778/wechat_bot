from dataclasses import dataclass
from typing import List

from msgpack import dumps


def encode_to_base58(input_: List[int]):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    length = len(alphabet)
    flag = 0
    leading_zero = 0
    encoding = {}
    for c in input_:
        if flag or c:
            flag = 1
        else:
            leading_zero += 1
        carry = c
        i = 0
        while carry or i < len(encoding):
            carry += (encoding[i] << 8) if i in encoding else 0
            encoding[i] = carry % length
            carry = carry // length | 0
            i += 1

    len_ = leading_zero + len(encoding)
    values = [
        alphabet[0 if i < leading_zero else encoding[len_ - i - 1]] for i in range(len_)
    ]
    return "".join(values)


PROFESSION = [
    "近卫",
    "狙击",
    "重装",
    "医疗",
    "辅助",
    "术师",
    "特种",
    "先锋",
]

POSITION = ["近战位", "远程位"]

RARITY = ["高级资深干员", "资深干员", "新手"]

TAG = [
    "支援机械",
    "控场",
    "爆发",
    "治疗",
    "支援",
    "费用回复",
    "输出",
    "生存",
    "群攻",
    "防护",
    "减速",
    "削弱",
    "快速复活",
    "位移",
    "召唤",
]

ALL = PROFESSION + POSITION + RARITY + TAG

PROFESSION_INDEX = len(PROFESSION) + len(POSITION) + len(RARITY) + len(TAG) - 1

POSITION_INDEX = len(POSITION) + len(RARITY) + len(TAG) - 1

RARITY_INDEX = len(RARITY) + len(TAG) - 1

TAG_INDEX = len(TAG) - 1


@dataclass
class Source:
    profession: str
    position: str
    rarity: int
    tag: List[str]
    zh: str
    subset: List[int]
    obtain_method: List[str]


class BitMap:
    def __init__(self, value: int = 0):
        self.value = value

    def get(self, index: int):
        return self.value & (1 << index)

    def set(self, index: int):
        self.value |= 1 << index

    def clear(self, index: int):
        self.value ^= 1 << index

    def range(self, lower: int, upper: int):
        mask = (1 << (upper + 1)) - 1 - ((1 << (lower + 1)) - 1)
        return self.value & mask

    def count(self):
        res = 0
        tmp = self.value
        while tmp:
            tmp &= tmp - 1
            res += 1
        return res

    def get_indict(self):
        result: List[int] = []
        value = self.value
        index = 0
        while value:
            if value & 1:
                result.append(index)
            value >>= 1
            index += 1
        return result

    def get_subset(self):
        result: List[int] = []
        indices = self.get_indict()
        index = BitMap(0)
        while index.value < (1 << len(indices)):
            tmp = 0
            for i in index.get_indict():
                tmp |= 1 << indices[i]
            if tmp:
                result.append(tmp)
            index.value += 1
        return result


class Char:
    def __init__(self, i: int = 0):
        self.bitmap = BitMap(i)

    @classmethod
    def from_source(cls, source: Source):
        char = cls(0)
        char.bitmap.value = 0
        char.bitmap.set(PROFESSION_INDEX - PROFESSION.index(source.profession))
        char.bitmap.set(POSITION_INDEX - POSITION.index(source.position))
        if source.rarity == 4:
            char.bitmap.set(RARITY_INDEX - RARITY.index("资深干员"))
        elif source.rarity == 5:
            char.bitmap.set(RARITY_INDEX - RARITY.index("高级资深干员"))
        for tag in source.tag:
            if tag == "新手":
                char.bitmap.set(RARITY_INDEX - RARITY.index("新手"))
                continue
            char.bitmap.set(TAG_INDEX - TAG.index(tag))
        return char

    def select_all_profession(self):
        for index, val in enumerate(PROFESSION):
            self.bitmap.set(PROFESSION_INDEX - index)

    def unselect_all_profession(self):
        for index, val in enumerate(PROFESSION):
            if self.bitmap.get(PROFESSION_INDEX - index):
                self.bitmap.clear(PROFESSION_INDEX - index)

    def is_profession_empty(self):
        return not self.bitmap.range(
            PROFESSION_INDEX - len(PROFESSION), PROFESSION_INDEX
        )

    def select_all_position(self):
        for index, val in enumerate(POSITION):
            self.bitmap.set(POSITION_INDEX - index)

    def unselect_all_position(self):
        for index, val in enumerate(POSITION):
            if self.bitmap.get(POSITION_INDEX - index):
                self.bitmap.clear(POSITION_INDEX - index)

    def is_position_empty(self):
        return not self.bitmap.range(POSITION_INDEX - len(POSITION), POSITION_INDEX)

    def select_all_rarity(self):
        for index, val in enumerate(RARITY):
            self.bitmap.set(RARITY_INDEX - index)

    def unselect_all_rarity(self):
        for index, val in enumerate(RARITY):
            if self.bitmap.get(RARITY_INDEX - index):
                self.bitmap.clear(RARITY_INDEX - index)

    def is_rarity_empty(self):
        return not self.bitmap.range(RARITY_INDEX - len(RARITY), RARITY_INDEX)

    def select_all_tag(self):
        for index, val in enumerate(TAG):
            self.bitmap.set(TAG_INDEX - index)

    def unselect_all_tag(self):
        for index, val in enumerate(TAG):
            if self.bitmap.get(TAG_INDEX - index):
                self.bitmap.clear(TAG_INDEX - index)

    def is_tag_empty(self):
        return not self.bitmap.range(TAG_INDEX - len(TAG), TAG_INDEX)

    def dump(self):
        profession_state = self.bitmap.range(
            PROFESSION_INDEX - len(PROFESSION), PROFESSION_INDEX
        )
        position_state = self.bitmap.range(
            POSITION_INDEX - len(POSITION), POSITION_INDEX
        )
        rarity_state = self.bitmap.range(RARITY_INDEX - len(RARITY), RARITY_INDEX)
        tag_state = self.bitmap.range(TAG_INDEX - len(TAG), TAG_INDEX)
        payload = {
            "profession": profession_state >> (len(POSITION) + len(RARITY) + len(TAG)),
            "position": position_state >> (len(RARITY) + len(TAG)),
            "rarity": rarity_state >> len(TAG),
            "tag": tag_state,
        }
        return encode_to_base58(dumps(payload))  # type: ignore

    REPLACE_MAP = {
        "术士": "术师",
        "高资": "高级资深干员",
        "资深": "资深干员",
    }


def recruitment(tags: List[str]):
    char = Char()
    for tag in tags:
        if tag in char.REPLACE_MAP:
            tag = char.REPLACE_MAP[tag]
        if tag in PROFESSION:
            char.bitmap.set(PROFESSION_INDEX - PROFESSION.index(tag))
        elif tag in POSITION:
            char.bitmap.set(POSITION_INDEX - POSITION.index(tag))
        elif tag in RARITY:
            char.bitmap.set(RARITY_INDEX - RARITY.index(tag))
        elif tag in TAG:
            char.bitmap.set(TAG_INDEX - TAG.index(tag))
    return f"https://prts.wiki/w/公招计算?filter={char.dump()}"


if __name__ == "__main__":
    print(recruitment(["高资", "支援", "近卫"]))
