import random
from typing import List, Tuple
from PIL import Image, ImageDraw
from PIL.Image import Image as IMG

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .base_handle import BaseHandle, BaseData
from ..config import draw_config
from ..util import cn2py, load_font
from image_utils import BuildImage


class OnmyojiChar(BaseData):
    @property
    def star_str(self) -> str:
        return ["N", "R", "SR", "SSR", "SP"][self.star - 1]


class OnmyojiHandle(BaseHandle[OnmyojiChar]):
    def __init__(self):
        super().__init__("onmyoji", "阴阳师")
        self.max_star = 5
        self.config = draw_config.onmyoji
        self.ALL_CHAR: List[OnmyojiChar] = []

    def get_card(self, **kwargs) -> OnmyojiChar:
        star = self.get_star(
            [5, 4, 3, 2],
            [
                self.config.ONMYOJI_SP,
                self.config.ONMYOJI_SSR,
                self.config.ONMYOJI_SR,
                self.config.ONMYOJI_R,
            ],
        )
        chars = [x for x in self.ALL_CHAR if x.star == star and not x.limited]
        return random.choice(chars)

    def format_max_star(self, card_list: List[Tuple[OnmyojiChar, int]]) -> str:
        rst = ""
        for card, index in card_list:
            if card.star == self.max_star:
                rst += f"第 {index} 抽获取SP {card.name}\n"
            elif card.star == self.max_star - 1:
                rst += f"第 {index} 抽获取SSR {card.name}\n"
        return rst.strip()

    @staticmethod
    def star_label(star: int) -> IMG:
        text, color1, color2 = [
            ("N", "#7E7E82", "#F5F6F7"),
            ("R", "#014FA8", "#37C6FD"),
            ("SR", "#6E0AA4", "#E94EFD"),
            ("SSR", "#E5511D", "#FAF905"),
            ("SP", "#FA1F2D", "#FFBBAF"),
        ][star - 1]
        w = 200
        h = 110
        # 制作渐变色图片
        base = Image.new("RGBA", (w, h), color1)
        top = Image.new("RGBA", (w, h), color2)
        mask = Image.new("L", (w, h))
        mask_data = []
        for y in range(h):
            mask_data.extend([int(255 * (y / h))] * w)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        # 透明图层
        font = load_font("gorga.otf", 100)
        alpha = Image.new("L", (w, h))
        draw = ImageDraw.Draw(alpha)
        draw.text((20, -30), text, fill="white", font=font)
        base.putalpha(alpha)
        # stroke
        bg = Image.new("RGBA", (w, h))
        draw = ImageDraw.Draw(bg)
        draw.text(
            (20, -30),
            text,
            font=font,
            fill="gray",
            stroke_width=3,
            stroke_fill="gray",
        )
        bg.paste(base, (0, 0), base)
        return bg

    def generate_img(self, card_list: List[OnmyojiChar]) -> BuildImage:
        return super().generate_img(card_list, num_per_line=10)

    def generate_card_img(self, card: OnmyojiChar) -> BuildImage:
        bg = BuildImage(73, 240, color="#F1EFE9")
        img_path = str(self.img_path / f"{cn2py(card.name)}_mark_btn.png")
        img = Image.open(img_path).convert("RGBA")
        label = self.star_label(card.star).resize((60, 33), Image.Resampling.LANCZOS)
        bg.paste(img, (0, 0), alpha=True)
        bg.paste(label, (0, 135), alpha=True)
        font = load_font("msyh.ttf", 16)
        draw = ImageDraw.Draw(bg.markImg)
        text = "\n".join([t for t in card.name[:4]])
        # _, text_h = font.getsize_multiline(text, spacing=0)
        _, text_h = font.getbbox(text)[2:]
        draw.text(
            (40, 150 + (90 - text_h) / 2), text, font=font, fill="gray", spacing=0
        )
        return bg

    def _init_data(self):
        self.ALL_CHAR = [
            OnmyojiChar(
                name=value["名称"],
                star=["N", "R", "SR", "SSR", "SP"].index(value["星级"]) + 1,
                limited=True
                if key
                in [
                    "奴良陆生",
                    "卖药郎",
                    "鬼灯",
                    "阿香",
                    "蜜桃&芥子",
                    "犬夜叉",
                    "杀生丸",
                    "桔梗",
                    "朽木露琪亚",
                    "黑崎一护",
                    "灶门祢豆子",
                    "灶门炭治郎",
                ]
                else False,
            )
            for key, value in self.load_data().items()
        ]
