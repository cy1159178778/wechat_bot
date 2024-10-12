import random
from typing import List, Optional, Tuple
from PIL import ImageDraw
from pydantic import ValidationError

from .base_handle import BaseHandle, BaseData, UpEvent as _UpEvent, UpChar as _UpChar
from ..config import draw_config
from ..util import cn2py, load_font
from image_utils import BuildImage

try:
    import ujson as json
except ModuleNotFoundError:
    import json


class AzurChar(BaseData):
    type_: str  # 舰娘类型

    @property
    def star_str(self) -> str:
        return ["白", "蓝", "紫", "金"][self.star - 1]


class UpChar(_UpChar):
    type_: str  # 舰娘类型


class UpEvent(_UpEvent):
    up_char: List[UpChar]  # up对象


class AzurHandle(BaseHandle[AzurChar]):
    def __init__(self):
        super().__init__("azur", "碧蓝航线")
        self.max_star = 4
        self.config = draw_config.azur
        self.ALL_CHAR: List[AzurChar] = []
        self.UP_EVENT: Optional[UpEvent] = None

    def get_card(self, pool_name: str, **kwargs) -> AzurChar:
        if pool_name == "轻型":
            type_ = ["驱逐", "轻巡", "维修"]
        elif pool_name == "重型":
            type_ = ["重巡", "战列", "战巡", "重炮"]
        else:
            type_ = ["维修", "潜艇", "重巡", "轻航", "航母"]
        up_pool_flag = pool_name == "活动"
        # Up
        up_ship = (
            [x for x in self.UP_EVENT.up_char if x.zoom > 0] if self.UP_EVENT else []
        )
        # print(up_ship)
        acquire_char = None
        if up_ship and up_pool_flag:
            up_zoom: List[Tuple[float, float]] = [(0, up_ship[0].zoom / 100)]
            # 初始化概率
            cur_ = up_ship[0].zoom / 100
            for i in range(len(up_ship)):
                try:
                    up_zoom.append((cur_, cur_ + up_ship[i + 1].zoom / 100))
                    cur_ += up_ship[i + 1].zoom / 100
                except IndexError:
                    pass
            rand = random.random()
            # 抽取up
            for i, zoom in enumerate(up_zoom):
                if zoom[0] <= rand <= zoom[1]:
                    try:
                        acquire_char = [
                            x for x in self.ALL_CHAR if x.name == up_ship[i].name
                        ][0]
                    except IndexError:
                        pass
        # 没有up或者未抽取到up
        if not acquire_char:
            star = self.get_star(
                [4, 3, 2, 1],
                [
                    self.config.AZUR_FOUR_P,
                    self.config.AZUR_THREE_P,
                    self.config.AZUR_TWO_P,
                    self.config.AZUR_ONE_P,
                ],
            )
            acquire_char = random.choice(
                [
                    x
                    for x in self.ALL_CHAR
                    if x.star == star and x.type_ in type_ and not x.limited
                ]
            )
        return acquire_char

    def draw(self, count: int, **kwargs) -> Tuple[bytes, str]:
        index2card = self.get_cards(count, **kwargs)
        cards = [card[0] for card in index2card]
        up_list = [x.name for x in self.UP_EVENT.up_char] if self.UP_EVENT else []
        result = self.format_result(index2card, **{**kwargs, "up_list": up_list})
        return self.generate_img(cards).pic2bytes(), result

    def generate_card_img(self, card: AzurChar) -> BuildImage:
        sep_w = 5
        sep_t = 5
        sep_b = 20
        w = 100
        h = 100
        bg = BuildImage(w + sep_w * 2, h + sep_t + sep_b)
        frame_path = str(self.img_path / f"{card.star}_star.png")
        frame = BuildImage(w, h, background=frame_path)
        img_path = str(self.img_path / f"{cn2py(card.name)}.png")
        img = BuildImage(w, h, background=img_path)
        # 加圆角
        frame.circle_corner(6)
        img.circle_corner(6)
        bg.paste(img, (sep_w, sep_t), alpha=True)
        bg.paste(frame, (sep_w, sep_t), alpha=True)
        # 加名字
        text = card.name[:6] + "..." if len(card.name) > 7 else card.name
        font = load_font(fontsize=14)
        text_w, text_h = font.getbbox(text)[2:]
        draw = ImageDraw.Draw(bg.markImg)
        draw.text(
            (sep_w + (w - text_w) / 2, h + sep_t + (sep_b - text_h) / 2),
            text,
            font=font,
            fill=["#808080", "#3b8bff", "#8000ff", "#c90", "#ee494c"][card.star - 1],
        )
        return bg

    def _init_data(self):
        self.ALL_CHAR = [
            AzurChar(
                name=value["名称"],
                star=int(value["星级"]),
                limited="可以建造" not in value["获取途径"],
                type_=value["类型"],
            )
            for value in self.load_data().values()
        ]
        self.load_up_char()

    def load_up_char(self):
        try:
            data = self.load_data(f"draw_card_up/{self.game_name}_up_char.json")
            self.UP_EVENT = UpEvent.parse_obj(data.get("char", {}))
        except ValidationError:
            print(f"{self.game_name}_up_char 解析出错")

    def dump_up_char(self):
        if self.UP_EVENT:
            data = {"char": json.loads(self.UP_EVENT.json())}
            self.dump_data(data, f"draw_card_up/{self.game_name}_up_char.json")
            self.dump_data(data, f"draw_card_up/{self.game_name}_up_char.json")
