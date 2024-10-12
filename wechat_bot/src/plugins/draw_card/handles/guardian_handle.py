import re
import random
import dateparser
from lxml import etree
from PIL import ImageDraw
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


class GuardianData(BaseData):
    pass


class GuardianChar(GuardianData):
    pass


class GuardianArms(GuardianData):
    pass


class GuardianHandle(BaseHandle[GuardianData]):
    def __init__(self):
        super().__init__("guardian", "坎公骑冠剑")
        self.data_files.append("guardian_arms.json")
        self.config = draw_config.guardian

        self.ALL_CHAR: List[GuardianChar] = []
        self.ALL_ARMS: List[GuardianArms] = []
        self.UP_CHAR: Optional[UpEvent] = None
        self.UP_ARMS: Optional[UpEvent] = None

    def get_card(self, pool_name: str, mode: int = 1) -> GuardianData:
        if pool_name == "char":
            if mode == 1:
                star = self.get_star(
                    [3, 2, 1],
                    [
                        self.config.GUARDIAN_THREE_CHAR_P,
                        self.config.GUARDIAN_TWO_CHAR_P,
                        self.config.GUARDIAN_ONE_CHAR_P,
                    ],
                )
            else:
                star = self.get_star(
                    [3, 2],
                    [
                        self.config.GUARDIAN_THREE_CHAR_P,
                        self.config.GUARDIAN_TWO_CHAR_P,
                    ],
                )
            up_event = self.UP_CHAR
            self.max_star = 3
            all_data = self.ALL_CHAR
        else:
            if mode == 1:
                star = self.get_star(
                    [5, 4, 3, 2],
                    [
                        self.config.GUARDIAN_FIVE_ARMS_P,
                        self.config.GUARDIAN_FOUR_ARMS_P,
                        self.config.GUARDIAN_THREE_ARMS_P,
                        self.config.GUARDIAN_TWO_ARMS_P,
                    ],
                )
            else:
                star = self.get_star(
                    [5, 4],
                    [
                        self.config.GUARDIAN_FIVE_ARMS_P,
                        self.config.GUARDIAN_FOUR_ARMS_P,
                    ],
                )
            up_event = self.UP_ARMS
            self.max_star = 5
            all_data = self.ALL_ARMS

        acquire_char = None
        # 是否UP
        if up_event and star == self.max_star and pool_name:
            # 获取up角色列表
            up_list = [x.name for x in up_event.up_char if x.star == star]
            # 成功获取up角色
            if random.random() < 0.5:
                up_name = random.choice(up_list)
                try:
                    acquire_char = [x for x in all_data if x.name == up_name][0]
                except IndexError:
                    pass
        if not acquire_char:
            chars = [x for x in all_data if x.star == star and not x.limited]
            acquire_char = random.choice(chars)
        return acquire_char

    def get_cards(self, count: int, pool_name: str) -> List[Tuple[GuardianData, int]]:
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
        up_event = self.UP_CHAR if pool_name == "char" else self.UP_ARMS
        if up_event:
            if pool_name == "char":
                up_list = [x.name for x in up_event.up_char if x.star == 3]
                info += f'三星UP：{" ".join(up_list)}\n'
            else:
                up_list = [x.name for x in up_event.up_char if x.star == 5]
                info += f'五星UP：{" ".join(up_list)}\n'
            info = f"当前up池：{up_event.title}\n{info}"
        return info.strip()

    def draw(self, count: int, pool_name: str, **kwargs) -> Tuple[bytes, str]:
        index2card = self.get_cards(count, pool_name)
        cards = [card[0] for card in index2card]
        up_event = self.UP_CHAR if pool_name == "char" else self.UP_ARMS
        up_list = [x.name for x in up_event.up_char] if up_event else []
        result = self.format_result(index2card, up_list=up_list)
        pool_info = self.format_pool_info(pool_name)
        return self.generate_img(cards).pic2bytes(), pool_info + result

    def generate_card_img(self, card: GuardianData) -> BuildImage:
        sep_w = 1
        sep_h = 1
        block_w = 170
        block_h = 90
        img_w = 90
        img_h = 90
        if isinstance(card, GuardianChar):
            block_color = "#2e2923"
            font_color = "#e2ccad"
            star_w = 90
            star_h = 30
            star_name = f"{card.star}_star.png"
            frame_path = ""
        else:
            block_color = "#EEE4D5"
            font_color = "#A65400"
            star_w = 45
            star_h = 45
            star_name = f"{card.star}_star_rank.png"
            frame_path = str(self.img_path / "avatar_frame.png")
        bg = BuildImage(block_w + sep_w * 2, block_h + sep_h * 2, color="#F6F4ED")
        block = BuildImage(block_w, block_h, color=block_color)
        star_path = str(self.img_path / star_name)
        star = BuildImage(star_w, star_h, background=star_path)
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(img_w, img_h, background=img_path)
        block.paste(img, (0, 0), alpha=True)
        if frame_path:
            frame = BuildImage(img_w, img_h, background=frame_path)
            block.paste(frame, (0, 0), alpha=True)
        block.paste(
            star,
            (int((block_w + img_w - star_w) / 2), block_h - star_h - 30),
            alpha=True,
        )
        # 加名字
        text = card.name[:4] + "..." if len(card.name) > 5 else card.name
        font = load_font(fontsize=14)
        text_w, _ = font.getbbox(text)[2:]
        draw = ImageDraw.Draw(block.markImg)
        draw.text(
            ((block_w + img_w - text_w) / 2, 55),
            text,
            font=font,
            fill=font_color,
        )
        bg.paste(block, (sep_w, sep_h))
        return bg

    def _init_data(self):
        self.ALL_CHAR = [
            GuardianChar(name=value["名称"], star=int(value["星级"]), limited=False)
            for value in self.load_data().values()
        ]
        self.ALL_ARMS = [
            GuardianArms(name=value["名称"], star=int(value["星级"]), limited=False)
            for value in self.load_data("guardian_arms.json").values()
        ]
        self.load_up_char()

    def load_up_char(self):
        try:
            data = self.load_data(f"draw_card_up/{self.game_name}_up_char.json")
            self.UP_CHAR = UpEvent.parse_obj(data.get("char", {}))
            self.UP_ARMS = UpEvent.parse_obj(data.get("arms", {}))
        except ValidationError:
            print(f"{self.game_name}_up_char 解析出错")
