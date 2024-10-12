import random
from typing import List, Tuple
from PIL import ImageDraw

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .base_handle import BaseHandle, BaseData
from ..config import draw_config
from ..util import cn2py, load_font
from image_utils import BuildImage


class FgoData(BaseData):
    pass


class FgoChar(FgoData):
    pass


class FgoCard(FgoData):
    pass


class FgoHandle(BaseHandle[FgoData]):
    def __init__(self):
        super().__init__("fgo", "命运-冠位指定")
        self.data_files.append("fgo_card.json")
        self.max_star = 5
        self.config = draw_config.fgo
        self.ALL_CHAR: List[FgoChar] = []
        self.ALL_CARD: List[FgoCard] = []

    def get_card(self, mode: int = 1) -> FgoData:
        if mode == 1:
            star = self.get_star(
                [8, 7, 6, 5, 4, 3],
                [
                    self.config.FGO_SERVANT_FIVE_P,
                    self.config.FGO_SERVANT_FOUR_P,
                    self.config.FGO_SERVANT_THREE_P,
                    self.config.FGO_CARD_FIVE_P,
                    self.config.FGO_CARD_FOUR_P,
                    self.config.FGO_CARD_THREE_P,
                ],
            )
        elif mode == 2:
            star = self.get_star(
                [5, 4], [self.config.FGO_CARD_FIVE_P, self.config.FGO_CARD_FOUR_P]
            )
        else:
            star = self.get_star(
                [8, 7, 6],
                [
                    self.config.FGO_SERVANT_FIVE_P,
                    self.config.FGO_SERVANT_FOUR_P,
                    self.config.FGO_SERVANT_THREE_P,
                ],
            )
        if star > 5:
            star -= 3
            chars = [x for x in self.ALL_CHAR if x.star == star and not x.limited]
        else:
            chars = [x for x in self.ALL_CARD if x.star == star and not x.limited]
        return random.choice(chars)

    def get_cards(self, count: int, **kwargs) -> List[Tuple[FgoData, int]]:
        card_list = []  # 获取所有角色
        servant_count = 0  # 保底计算
        card_count = 0  # 保底计算
        for i in range(count):
            servant_count += 1
            card_count += 1
            if card_count == 9:  # 四星卡片保底
                mode = 2
            elif servant_count == 10:  # 三星从者保底
                mode = 3
            else:  # 普通抽
                mode = 1
            card = self.get_card(mode)
            if isinstance(card, FgoCard) and card.star > self.max_star - 2:
                card_count = 0
            if isinstance(card, FgoChar):
                servant_count = 0
            card_list.append((card, i + 1))
        return card_list

    def generate_card_img(self, card: FgoData) -> BuildImage:
        sep_w = 5
        sep_t = 5
        sep_b = 20
        w = 128
        h = 140
        bg = BuildImage(w + sep_w * 2, h + sep_t + sep_b)
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(w, h, background=img_path)
        bg.paste(img, (sep_w, sep_t), alpha=True)
        # 加名字
        text = card.name[:6] + "..." if len(card.name) > 7 else card.name
        font = load_font(fontsize=16)
        text_w, text_h = font.getbbox(text)[2:]
        draw = ImageDraw.Draw(bg.markImg)
        draw.text(
            (sep_w + (w - text_w) / 2, h + sep_t + (sep_b - text_h) / 2),
            text,
            font=font,
            fill="gray",
        )
        return bg

    def _init_data(self):
        self.ALL_CHAR = [
            FgoChar(
                name=value["名称"],
                star=int(value["星级"]),
                limited=True
                if not ("圣晶石召唤" in value["入手方式"] or "圣晶石召唤（Story卡池）" in value["入手方式"])
                else False,
            )
            for value in self.load_data().values()
        ]
        self.ALL_CARD = [
            FgoCard(name=value["名称"], star=int(value["星级"]), limited=False)
            for value in self.load_data("fgo_card.json").values()
        ]