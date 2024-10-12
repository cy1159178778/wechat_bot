import random
from typing import List, Tuple
from PIL import ImageDraw
from image_utils import BuildImage

from ..config import draw_config
from ..util import cn2py, load_font
from .base_handle import BaseData, BaseHandle


class BaChar(BaseData):
    pass


class BaHandle(BaseHandle[BaChar]):
    def __init__(self):
        super().__init__("ba", "碧蓝档案")
        self.max_star = 3
        self.config = draw_config.ba
        self.ALL_CHAR: List[BaChar] = []

    def get_card(self, mode: int = 1) -> BaChar:
        if mode == 2:
            star = self.get_star(
                [3, 2], [self.config.BA_THREE_P, self.config.BA_G_TWO_P]
            )
        else:
            star = self.get_star(
                [3, 2, 1],
                [self.config.BA_THREE_P, self.config.BA_TWO_P, self.config.BA_ONE_P],
            )
        chars = [x for x in self.ALL_CHAR if x.star == star and not x.limited]
        return random.choice(chars)

    def get_cards(self, count: int, **kwargs) -> List[Tuple[BaChar, int]]:
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

    def generate_card_img(self, card: BaChar) -> BuildImage:
        sep_w = 5
        sep_h = 5
        star_h = 15
        img_w = 90
        img_h = 100
        font_h = 20
        bar_h = 20
        bar_w = 90
        bg = BuildImage(img_w + sep_w * 2, img_h + font_h + sep_h * 2, color="#EFF2F5")
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(img_w, img_h, background=img_path)
        bar = BuildImage(bar_w, bar_h, color="#6495ED")
        bg.paste(img, (sep_w, sep_h), alpha=True)
        bg.paste(bar, (sep_w, img_h - bar_h + sep_h), alpha=True)
        if card.star == 1:
            star_path = str(self.img_path / "star-1.png")
            star_w = 15
        elif card.star == 2:
            star_path = str(self.img_path / "star-2.png")
            star_w = 30
        else:
            star_path = str(self.img_path / "star-3.png")
            star_w = 45
        star = BuildImage(star_w, star_h, background=star_path)
        bg.paste(
            star, (img_w // 2 - 15 * (card.star - 1) // 2, img_h - star_h), alpha=True
        )
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
            BaChar(
                name=value["名称"],
                star=int(value["星级"]),
                limited=True if "（" in key else False,
            )
            for key, value in self.load_data().items()
        ]

    def title2star(self, title: int):
        if title == "Star-3.png":
            return 3
        elif title == "Star-2.png":
            return 2
        else:
            return 1
