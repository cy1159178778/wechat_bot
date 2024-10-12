import random
from io import BytesIO
from typing import List, Optional, Tuple

from PIL import ImageDraw, Image
from pathlib import Path
from pydantic import ValidationError

from .arknights_toolkit.gacha import ArknightsGacha, GachaUser
from .arknights_toolkit.gacha.simulate import simulate_image
from dataclasses import asdict

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .base_handle import BaseHandle, BaseData, UpEvent
from ..config import draw_config
from ..util import cn2py, load_font
from image_utils import BuildImage


base_path = Path(__file__).parent
gacha = ArknightsGacha(base_path / "arknights_toolkit/resource/pool.json")
userdata = {}


class Operator(BaseData):
    recruit_only: bool  # 公招限定
    event_only: bool  # 活动获得干员
    # special_only: bool  # 升变/异格干员


class PrtsHandle(BaseHandle[Operator]):
    def __init__(self):
        super().__init__(game_name="prts", game_name_cn="明日方舟")
        self.max_star = 6
        self.game_card_color = "#eff2f5"
        self.config = draw_config.prts

        self.ALL_OPERATOR: List[Operator] = []
        self.UP_EVENT: Optional[UpEvent] = None

    def get_card(self, add: float) -> Operator:
        star = self.get_star(
            star_list=[6, 5, 4, 3],
            probability_list=[
                self.config.PRTS_SIX_P + add,
                self.config.PRTS_FIVE_P,
                self.config.PRTS_FOUR_P,
                self.config.PRTS_THREE_P,
            ],
        )

        all_operators = [
            x
            for x in self.ALL_OPERATOR
            if x.star == star
        ]
        acquire_operator = None

        if self.UP_EVENT:
            up_operators = [x for x in self.UP_EVENT.up_char if x.star == star]
            # UPs
            try:
                zooms = [x.zoom for x in up_operators]
                zoom_sum = sum(zooms)
                if random.random() < zoom_sum:
                    up_name = random.choices(up_operators, weights=zooms, k=1)[0].name
                    acquire_operator = [
                        x for x in self.ALL_OPERATOR if x.name == up_name
                    ][0]
            except IndexError:
                pass
        if not acquire_operator:
            acquire_operator = random.choice(all_operators)
        return acquire_operator

    def get_cards(self, count: int, **kwargs):
        if count % 10:
            card_list = []  # 获取所有角色
            add = 0.0
            count_idx = 0
            for i in range(count):
                count_idx += 1
                card = self.get_card(add)
                if card.star == self.max_star:
                    add = 0.0
                    count_idx = 0
                elif count_idx > 50:
                    add += 0.02
                card_list.append((card, i + 1))
            return card_list
        else:
            session = kwargs["user_id"]
            if session not in userdata:
                user = GachaUser()
                userdata[session] = asdict(user)
            else:
                user = GachaUser(**userdata[session])
            data = gacha.gacha(user, count)
            index2card = []
            i = 1
            end = "\n没有抽中斯卡蒂哦，请继续加油ᕦ(･ㅂ･)ᕤ"
            new_image = Image.new('RGB', (1280, 720*len(data)))
            for img_index, ten in enumerate(data):
                for res in ten:
                    if "斯卡蒂" in res.name:
                        end = "\n呀，你抽中斯卡蒂了，斯卡蒂是你的人了(〃'▽'〃)"
                    index2card.append((Operator(
                                        name=res.name,
                                        star=res.rarity,
                                        limited=False,
                                        recruit_only=True,
                                        event_only=False,
                                    ), i))
                    i += 1
                img = simulate_image(ten)
                new_image.paste(img, box=(0, 720*img_index))
            text = self.format_result(index2card, up_list=[])
            imageio = BytesIO()
            new_image.save(
                imageio,
                format="JPEG",
                quality=95,
                subsampling=2,
                qtables="web_high",
            )
            return imageio.getvalue(), text + end

    def format_pool_info(self) -> str:
        info = ""
        if self.UP_EVENT:
            star6_list = [x.name for x in self.UP_EVENT.up_char if x.star == 6]
            star5_list = [x.name for x in self.UP_EVENT.up_char if x.star == 5]
            star4_list = [x.name for x in self.UP_EVENT.up_char if x.star == 4]
            if star6_list:
                info += f"六星UP：{' '.join(star6_list)}\n"
            if star5_list:
                info += f"五星UP：{' '.join(star5_list)}\n"
            if star4_list:
                info += f"四星UP：{' '.join(star4_list)}\n"
            info = f"当前up池: {self.UP_EVENT.title}\n{info}"
        return info.strip()

    def draw(self, count: int, **kwargs) -> Tuple[bytes, str]:
        res = self.get_cards(count, **kwargs)
        if isinstance(res, list):
            index2card = res
            """这里cards修复了抽卡图文不符的bug"""
            cards = [card[0] for card in index2card]
            up_list = [x.name for x in self.UP_EVENT.up_char] if self.UP_EVENT else []
            result = self.format_result(index2card, up_list=up_list)
            pool_info = self.format_pool_info()
            if "斯卡蒂" in result:
                end = "\n呀，你抽中斯卡蒂了，斯卡蒂是你的人了(〃'▽'〃)"
            else:
                end = "\n没有抽中斯卡蒂哦，请继续加油ᕦ(･ㅂ･)ᕤ"
            return self.generate_img(cards).pic2bytes(), pool_info + result + end
        else:
            img, text = res
            return img, text

    def generate_card_img(self, card: Operator) -> BuildImage:
        sep_w = 5
        sep_h = 5
        star_h = 15
        img_w = 120
        img_h = 120
        font_h = 20
        bg = BuildImage(img_w + sep_w * 2, img_h + font_h + sep_h * 2, color="#EFF2F5")
        star_path = str(self.img_path / "star.png")
        star = BuildImage(star_h, star_h, background=star_path)
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(img_w, img_h, background=img_path)
        bg.paste(img, (sep_w, sep_h), alpha=True)
        for i in range(card.star):
            bg.paste(star, (sep_w + img_w - 5 - star_h * (i + 1), sep_h), alpha=True)
        # 加名字
        text = card.name[:7] + "..." if len(card.name) > 8 else card.name
        font = load_font(fontsize=16)
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
        self.ALL_OPERATOR = [
            Operator(
                name=value["名称"],
                star=int(value["星级"]),
                limited="干员寻访" not in value["获取途径"],
                recruit_only=True
                if "干员寻访" not in value["获取途径"] and "公开招募" in value["获取途径"]
                else False,
                event_only=True if "活动获取" in value["获取途径"] else False,
            )
            for key, value in self.load_data().items()
            if "阿米娅" not in key
        ]
        self.load_up_char()

    def load_up_char(self):
        try:
            data = self.load_data(f"draw_card_up/{self.game_name}_up_char.json")
            """这里的 waring 有点模糊，更新游戏信息时没有up池的情况下也会报错，所以细分了一下"""
            if not data:
                # print(f"当前无UP池或 {self.game_name}_up_char.json 文件不存在")
                pass
            else:
                self.UP_EVENT = UpEvent.parse_obj(data.get("char", {}))
        except ValidationError:
            print(f"{self.game_name}_up_char 解析出错")
