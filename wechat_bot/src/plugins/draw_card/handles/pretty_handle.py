import re
import random
import dateparser
from lxml import etree
from PIL import ImageDraw
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import unquote
from typing import List, Optional, Tuple
from pydantic import ValidationError


try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .base_handle import BaseHandle, BaseData, UpChar, UpEvent
from ..config import draw_config
from ..util import remove_prohibited_str, cn2py, load_font
from image_utils import BuildImage


class PrettyData(BaseData):
    pass


class PrettyChar(PrettyData):
    pass


class PrettyCard(PrettyData):
    @property
    def star_str(self) -> str:
        return ["R", "SR", "SSR"][self.star - 1]


class PrettyHandle(BaseHandle[PrettyData]):
    def __init__(self):
        super().__init__("pretty", "赛马娘")
        self.data_files.append("pretty_card.json")
        self.max_star = 3
        self.game_card_color = "#eff2f5"
        self.config = draw_config.pretty

        self.ALL_CHAR: List[PrettyChar] = []
        self.ALL_CARD: List[PrettyCard] = []
        self.UP_CHAR: Optional[UpEvent] = None
        self.UP_CARD: Optional[UpEvent] = None

    def get_card(self, pool_name: str, mode: int = 1) -> PrettyData:
        if mode == 1:
            star = self.get_star(
                [3, 2, 1],
                [
                    self.config.PRETTY_THREE_P,
                    self.config.PRETTY_TWO_P,
                    self.config.PRETTY_ONE_P,
                ],
            )
        else:
            star = self.get_star(
                [3, 2], [self.config.PRETTY_THREE_P, self.config.PRETTY_TWO_P]
            )
        up_pool = None
        if pool_name == "char":
            up_pool = self.UP_CHAR
            all_list = self.ALL_CHAR
        else:
            up_pool = self.UP_CARD
            all_list = self.ALL_CARD

        all_char = [x for x in all_list if x.star == star and not x.limited]
        acquire_char = None
        # 有UP池子
        if up_pool and star in [x.star for x in up_pool.up_char]:
            up_list = [x.name for x in up_pool.up_char if x.star == star]
            # 抽到UP
            if random.random() < 1 / len(all_char) * (0.7 / 0.1385):
                up_name = random.choice(up_list)
                try:
                    acquire_char = [x for x in all_list if x.name == up_name][0]
                except IndexError:
                    pass
        if not acquire_char:
            acquire_char = random.choice(all_char)
        return acquire_char

    def get_cards(self, count: int, pool_name: str) -> List[Tuple[PrettyData, int]]:
        card_list = []
        card_count = 0  # 保底计算
        for i in range(count):
            card_count += 1
            # 十连保底
            if card_count == 10:
                card = self.get_card(pool_name, 2)
                card_count = 0
            else:
                card = self.get_card(pool_name, 1)
                if card.star > self.max_star - 2:
                    card_count = 0
            card_list.append((card, i + 1))
        return card_list

    def format_pool_info(self, pool_name: str) -> str:
        info = ""
        up_event = self.UP_CHAR if pool_name == "char" else self.UP_CARD
        if up_event:
            star3_list = [x.name for x in up_event.up_char if x.star == 3]
            star2_list = [x.name for x in up_event.up_char if x.star == 2]
            star1_list = [x.name for x in up_event.up_char if x.star == 1]
            if star3_list:
                if pool_name == "char":
                    info += f'三星UP：{" ".join(star3_list)}\n'
                else:
                    info += f'SSR UP：{" ".join(star3_list)}\n'
            if star2_list:
                if pool_name == "char":
                    info += f'二星UP：{" ".join(star2_list)}\n'
                else:
                    info += f'SR UP：{" ".join(star2_list)}\n'
            if star1_list:
                if pool_name == "char":
                    info += f'一星UP：{" ".join(star1_list)}\n'
                else:
                    info += f'R UP：{" ".join(star1_list)}\n'
            info = f"当前up池：{up_event.title}\n{info}"
        return info.strip()

    def draw(self, count: int, pool_name: str, **kwargs) -> Tuple[bytes, str]:
        pool_name = "char" if not pool_name else pool_name
        index2card = self.get_cards(count, pool_name)
        cards = [card[0] for card in index2card]
        up_event = self.UP_CHAR if pool_name == "char" else self.UP_CARD
        up_list = [x.name for x in up_event.up_char] if up_event else []
        result = self.format_result(index2card, up_list=up_list)
        pool_info = self.format_pool_info(pool_name)
        return self.generate_img(cards).pic2bytes(), pool_info + result

    def generate_card_img(self, card: PrettyData) -> BuildImage:
        if isinstance(card, PrettyChar):
            star_h = 30
            img_w = 200
            img_h = 219
            font_h = 50
            bg = BuildImage(img_w, img_h + font_h, color="#EFF2F5")
            star_path = str(self.img_path / "star.png")
            star = BuildImage(star_h, star_h, background=star_path)
            img_path = str(self.img_path / f"{cn2py(card.name)}.png")
            img = BuildImage(img_w, img_h, background=img_path)
            star_w = star_h * card.star
            for i in range(card.star):
                bg.paste(star, (int((img_w - star_w) / 2) + star_h * i, 0), alpha=True)
            bg.paste(img, (0, 0), alpha=True)
            # 加名字
            text = card.name[:5] + "..." if len(card.name) > 6 else card.name
            font = load_font(fontsize=30)
            text_w, _ = font.getbbox(text)[2:]
            draw = ImageDraw.Draw(bg.markImg)
            draw.text(
                ((img_w - text_w) / 2, img_h),
                text,
                font=font,
                fill="gray",
            )
            return bg
        else:
            sep_w = 10
            img_w = 200
            img_h = 267
            font_h = 75
            bg = BuildImage(img_w + sep_w * 2, img_h + font_h, color="#EFF2F5")
            label_path = str(self.img_path / f"{card.star}_label.png")
            label = BuildImage(40, 40, background=label_path)
            img_path = str(self.img_path / f"{cn2py(card.name)}.png")
            img = BuildImage(img_w, img_h, background=img_path)
            bg.paste(img, (sep_w, 0), alpha=True)
            bg.paste(label, (30, 3), alpha=True)
            # 加名字
            text = ""
            texts = []
            font = load_font(fontsize=25)
            for t in card.name:
                if font.getbbox(text + t)[2:4][0] > 190:
                    texts.append(text)
                    text = ""
                    if len(texts) >= 2:
                        texts[-1] += "..."
                        break
                else:
                    text += t
            if text:
                texts.append(text)
            text = "\n".join(texts)
            text_w, _ = font.getbbox(text)[2:4]
            draw = ImageDraw.Draw(bg.markImg)
            draw.text(
                ((img_w - text_w) / 2, img_h),
                text,
                font=font,
                align="center",
                fill="gray",
            )
            return bg

    def _init_data(self):
        self.ALL_CHAR = [
            PrettyChar(
                name=value["名称"],
                star=int(value["初始星级"]),
                limited=False,
            )
            for value in self.load_data().values()
        ]
        self.ALL_CARD = [
            PrettyCard(
                name=value["中文名"],
                star=["R", "SR", "SSR"].index(value["稀有度"]) + 1,
                limited=True if "卡池" not in value["获取方式"] else False,
            )
            for value in self.load_data("pretty_card.json").values()
        ]
        self.load_up_char()

    def load_up_char(self):
        try:
            data = self.load_data(f"draw_card_up/{self.game_name}_up_char.json")
            self.UP_CHAR = UpEvent.parse_obj(data.get("char", {}))
            self.UP_CARD = UpEvent.parse_obj(data.get("card", {}))
        except ValidationError:
            print(f"{self.game_name}_up_char 解析出错")
