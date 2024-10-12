import random
import dateparser
from lxml import etree
from PIL import Image, ImageDraw
from urllib.parse import unquote
from typing import List, Optional, Tuple
from pydantic import ValidationError
from datetime import datetime, timedelta

from .Paimon_Gacha.draw import draw_gacha_img

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .base_handle import BaseHandle, BaseData, UpChar, UpEvent
from ..config import draw_config
from ..count_manager import GenshinCountManager
from ..util import remove_prohibited_str, cn2py, load_font
from image_utils import BuildImage


class GenshinData(BaseData):
    pass


class GenshinChar(GenshinData):
    pass


class GenshinArms(GenshinData):
    pass


class GenshinHandle(BaseHandle[GenshinData]):
    def __init__(self):
        super().__init__("genshin", "原神")
        self.data_files.append("genshin_arms.json")
        self.max_star = 5
        self.game_card_color = "#ebebeb"
        self.config = draw_config.genshin

        self.ALL_CHAR: List[GenshinData] = []
        self.ALL_ARMS: List[GenshinData] = []
        self.UP_CHAR: Optional[UpEvent] = None
        self.UP_CHAR_LIST: Optional[UpEvent] = []
        self.UP_ARMS: Optional[UpEvent] = None

        self.count_manager = GenshinCountManager((10, 90), ("4", "5"), 180)

    # 抽取卡池
    def get_card(
        self, pool_name: str, mode: int = 1, add: float = 0.0, is_up: bool = False, card_index: int = 0
    ):
        """
        mode 1：普通抽 2：四星保底 3：五星保底
        """
        if mode == 1:
            star = self.get_star(
                [5, 4, 3],
                [
                    self.config.GENSHIN_FIVE_P + add,
                    self.config.GENSHIN_FOUR_P,
                    self.config.GENSHIN_THREE_P,
                ],
            )
        elif mode == 2:
            star = self.get_star(
                [5, 4],
                [self.config.GENSHIN_G_FIVE_P + add, self.config.GENSHIN_G_FOUR_P],
            )
        else:
            star = 5

        if pool_name == "char":
            up_event = self.UP_CHAR_LIST[card_index]
            all_list = self.ALL_CHAR + [
                x for x in self.ALL_ARMS if x.star == star and x.star < 5
            ]
        elif pool_name == "arms":
            up_event = self.UP_ARMS
            all_list = self.ALL_ARMS + [
                x for x in self.ALL_CHAR if x.star == star and x.star < 5
            ]
        else:
            up_event = None
            all_list = self.ALL_ARMS + self.ALL_CHAR

        acquire_char = None
        # 是否UP
        if up_event and star > 3:
            # 获取up角色列表
            up_list = [x.name for x in up_event.up_char if x.star == star]
            # 成功获取up角色
            if random.random() < 0.5 or is_up:
                up_name = random.choice(up_list)
                try:
                    acquire_char = [x for x in all_list if x.name == up_name][0]
                except IndexError:
                    pass
        if not acquire_char:
            chars = [x for x in all_list if x.star == star and not x.limited]
            acquire_char = random.choice(chars)
        return acquire_char

    def get_cards(self, count: int, user_id: int, pool_name: str, card_index: int = 0):
        if not pool_name and not count % 10:
            img, tmp_list = draw_gacha_img(user_id, count // 10)
            cards_list = []
            for i, card_info in enumerate(tmp_list, 1):
                star, name = card_info
                cards_list.append((GenshinData(name=name, star=star, limited=False), i))
            return img, cards_list

        card_list = []  # 获取角色列表
        add = 0.0
        count_manager = self.count_manager
        count_manager.check_count(user_id, count)  # 检查次数累计
        pool = self.UP_CHAR_LIST[card_index] if pool_name == "char" else self.UP_ARMS
        for i in range(count):
            count_manager.increase(user_id)
            star = count_manager.check(user_id)  # 是否有四星或五星保底
            if (
                count_manager.get_user_count(user_id)
                - count_manager.get_user_five_index(user_id)
            ) % count_manager.get_max_guarantee() >= 72:
                add += draw_config.genshin.I72_ADD
            if star:
                if star == 4:
                    card = self.get_card(pool_name, 2, add=add, card_index=card_index)
                else:
                    card = self.get_card(
                        pool_name, 3, add, count_manager.is_up(user_id), card_index=card_index
                    )
            else:
                card = self.get_card(pool_name, 1, add, count_manager.is_up(user_id), card_index=card_index)
            # print(f"{count_manager.get_user_count(user_id)}：",
            # count_manager.get_user_five_index(user_id), star, card.star, add)
            # 四星角色
            if card.star == 4:
                count_manager.mark_four_index(user_id)
            # 五星角色
            elif card.star == self.max_star:
                add = 0
                count_manager.mark_five_index(user_id)  # 记录五星保底
                count_manager.mark_four_index(user_id)  # 记录四星保底
            if pool and card.name in [
                x.name for x in pool.up_char if x.star == self.max_star
            ]:
                count_manager.set_is_up(user_id, True)
            else:
                count_manager.set_is_up(user_id, False)
            card_list.append((card, count_manager.get_user_count(user_id)))
        return "", card_list

    def generate_card_img(self, card: GenshinData) -> BuildImage:
        sep_w = 10
        sep_h = 5
        frame_w = 112
        frame_h = 132
        img_w = 106
        img_h = 106
        bg = BuildImage(frame_w + sep_w * 2, frame_h + sep_h * 2, color="#EBEBEB")
        frame_path = str(self.img_path / "avatar_frame.png")
        frame = Image.open(frame_path)
        # 加名字
        text = card.name
        font = load_font(fontsize=14)
        text_w, text_h = font.getbbox(text)[2:]
        draw = ImageDraw.Draw(frame)
        draw.text(
            ((frame_w - text_w) / 2, frame_h - 15 - text_h / 2),
            text,
            font=font,
            fill="gray",
        )
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(img_w, img_h, background=img_path)
        if isinstance(card, GenshinArms):
            # 武器卡背景不是透明的，切去上方两个圆弧
            r = 12
            circle = Image.new("L", (r * 2, r * 2), 0)
            alpha = Image.new("L", img.size, 255)
            alpha.paste(circle, (-r - 3, -r - 3))  # 左上角
            alpha.paste(circle, (img_h - r + 3, -r - 3))  # 右上角
            img.markImg.putalpha(alpha)
        star_path = str(self.img_path / f"{card.star}_star.png")
        star = Image.open(star_path)
        bg.paste(frame, (sep_w, sep_h), alpha=True)
        bg.paste(img, (sep_w + 3, sep_h + 3), alpha=True)
        bg.paste(star, (sep_w + int((frame_w - star.width) / 2), sep_h - 6), alpha=True)
        return bg

    def format_pool_info(self, pool_name: str, card_index: int = 0) -> str:
        info = ""
        up_event = None
        if pool_name == "char":
            up_event = self.UP_CHAR_LIST[card_index]
        elif pool_name == "arms":
            up_event = self.UP_ARMS
        if up_event:
            star5_list = [x.name for x in up_event.up_char if x.star == 5]
            star4_list = [x.name for x in up_event.up_char if x.star == 4]
            if star5_list:
                info += f"五星UP：{' '.join(star5_list)}\n"
            if star4_list:
                info += f"四星UP：{' '.join(star4_list)}\n"
            info = f"当前up池：{up_event.title}\n{info}"
        return info.strip()

    def draw(self, count: int, user_id: int, pool_name: str = "", **kwargs) -> Tuple[bytes, str]:
        card_index = 0
        if "1" in pool_name:
            card_index = 1
        pool_name = pool_name.replace("1", "")
        img, index2cards = self.get_cards(count, user_id, pool_name, card_index)
        cards = [card[0] for card in index2cards]
        up_event = None
        if pool_name == "char":
            if card_index == 1 and len(self.UP_CHAR_LIST) == 1:
                return b"", "当前没有第二个角色UP池"
            up_event = self.UP_CHAR_LIST[card_index]
        elif pool_name == "arms":
            up_event = self.UP_ARMS
        up_list = [x.name for x in up_event.up_char] if up_event else []
        result = self.format_star_result(cards)
        result += (
            "\n" + max_star_str
            if (max_star_str := self.format_max_star(index2cards, up_list=up_list))
            else ""
        )
        max_card_result = self.format_max_card(cards, **kwargs)
        if max_card_result:
            result += "\n" + max_card_result

        if img:
            return img.getvalue(), result

        result += f"\n距离保底发还剩 {self.count_manager.get_user_guarantee_count(user_id)} 抽"
        # result += "\n【五星：0.6%，四星：5.1%，第72抽开始五星概率每抽加0.585%】"
        pool_info = self.format_pool_info(pool_name, card_index)
        img = self.generate_img(cards)
        bk = BuildImage(img.w, img.h + 50, font_size=20, color="#ebebeb")
        bk.paste(img)
        bk.text((0, img.h + 10), "【五星：0.6%，四星：5.1%，第72抽开始五星概率每抽加0.585%】")
        return bk.pic2bytes(), pool_info + "\n" + result

    def _init_data(self):
        self.ALL_CHAR = [
            GenshinChar(
                name=value["名称"],
                star=int(value["星级"]),
                limited=value["常驻/限定"] == "限定UP",
            )
            for key, value in self.load_data().items()
            if "旅行者" not in key
        ]
        self.ALL_ARMS = [
            GenshinArms(
                name=value["名称"],
                star=int(value["星级"]),
                limited="祈愿" not in value["获取途径"],
            )
            for value in self.load_data("genshin_arms.json").values()
        ]
        self.load_up_char()

    def load_up_char(self):
        try:
            data = self.load_data(f"draw_card_up/{self.game_name}_up_char.json")
            self.UP_CHAR_LIST.append(UpEvent.parse_obj(data.get("char", {})))
            self.UP_CHAR_LIST.append(UpEvent.parse_obj(data.get("char1", {})))
            self.UP_ARMS = UpEvent.parse_obj(data.get("arms", {}))
        except ValidationError:
            print(f"{self.game_name}_up_char 解析出错")

    def reset_count(self, user_id: int) -> bool:
        self.count_manager.reset(user_id)
        return True
