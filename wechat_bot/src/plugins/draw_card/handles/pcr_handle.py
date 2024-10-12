import random
from typing import List, Tuple
from PIL import ImageDraw

from .base_handle import BaseHandle, BaseData
from ..config import draw_config
from ..util import cn2py, load_font
from image_utils import BuildImage


class PcrChar(BaseData):
    pass


class PcrHandle(BaseHandle[PcrChar]):
    def __init__(self):
        super().__init__("pcr", "公主连结")
        self.max_star = 3
        self.config = draw_config.pcr
        self.ALL_CHAR: List[PcrChar] = []

    def get_card(self, mode: int = 1) -> PcrChar:
        if mode == 2:
            star = self.get_star(
                [3, 2], [self.config.PCR_G_THREE_P, self.config.PCR_G_TWO_P]
            )
        else:
            star = self.get_star(
                [3, 2, 1],
                [self.config.PCR_THREE_P, self.config.PCR_TWO_P, self.config.PCR_ONE_P],
            )
        chars = [x for x in self.ALL_CHAR if x.star == star and not x.limited]
        return random.choice(chars)

    def get_cards(self, count: int, **kwargs) -> List[Tuple[PcrChar, int]]:
        card_list = []
        card_count = 0  # 保底计算
        for i in range(count):
            card_count += 1
            # 十连保底
            if card_count == 10:
                card = self.get_card(2)
                card_count = 0
            else:
                card = self.get_card(1)
                if card.star > self.max_star - 2:
                    card_count = 0
            card_list.append((card, i + 1))
        return card_list

    def generate_card_img(self, card: PcrChar) -> BuildImage:
        sep_w = 5
        sep_h = 5
        star_h = 15
        img_w = 90
        img_h = 90
        font_h = 20
        bg = BuildImage(img_w + sep_w * 2, img_h + font_h + sep_h * 2, color="#EFF2F5")
        star_path = str(self.img_path / "star.png")
        star = BuildImage(star_h, star_h, background=star_path)
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(img_w, img_h, background=img_path)
        bg.paste(img, (sep_w, sep_h), alpha=True)
        for i in range(card.star):
            bg.paste(star, (sep_w + img_w - star_h * (i + 1), sep_h), alpha=True)
        # 加名字
        text = card.name[:5] + "..." if len(card.name) > 6 else card.name
        font = load_font(fontsize=14)
        text_w, text_h = font.getbbox(text)[2:]
        draw = ImageDraw.Draw(bg.markImg)
        draw.text(
            (sep_w + (img_w - text_w) / 2, sep_h + img_h + (font_h - text_h) / 2),
            text,
            font=font,
            fill="gray",
        )
        return bg

    def _init_data(self):
        self.ALL_CHAR = [
            PcrChar(
                name=value["名称"],
                star=int(value["星级"]),
                limited=True if "（" in key else False,
            )
            for key, value in self.load_data().items()
        ]
