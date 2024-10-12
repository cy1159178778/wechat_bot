import itertools
import json
import math
import random
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from ..util import random_pick_big
from .model import GachaData, GachaUser, Operator

font_base = ImageFont.truetype(
    str(
        (
            Path(__file__).parent.parent / "resource" / "HarmonyOS_Sans_SC_Medium.ttf"
        ).absolute()
    ),
    16,
)


class ArknightsGacha:
    """抽卡模拟器"""

    five_per: int
    four_per: int
    three_per: int
    data: GachaData

    color: Dict[int, Tuple[int, int, int]] = {
        6: (0xFF, 0x7F, 0x27),  # ff7f27
        5: (0xFF, 0xC9, 0x0E),  # ffc90e
        4: (0x93, 0x19, 0x93),  # d8b3d8
        3: (0x09, 0xB3, 0xF7),  # 09b3f7
    }

    def __init__(self, file: Union[str, Path]):
        """
        :param file: 卡池信息文件
        """
        self.five_per, self.four_per, self.three_per = 8, 50, 40
        self.file = Path(file) if isinstance(file, str) else file
        with self.file.open("r+", encoding="UTF-8") as f_obj:
            self.data = json.load(f_obj)

    def gacha(self, user: GachaUser, count: int = 1) -> List[List[Operator]]:
        """
        模拟抽卡，返回生成的干员信息

        :param user: 抽卡用户，用来继承抽卡概率
        :param count: 抽卡数量
        :return: 干员信息
        """
        gacha_ranks: List[List[Operator]] = []
        cache = []
        for i in range(1, count + 1):
            x = random_pick_big(
                "六五四三", [user.six_per, self.five_per, self.four_per, self.three_per]
            )
            ans = "".join(itertools.islice(x, 1))
            if ans != "六":
                user.six_statis += 1
                if user.six_statis > 50:
                    user.six_per += 2
                    if self.three_per > 1:
                        self.three_per -= 2
                    elif self.four_per > 1:
                        self.four_per -= 2
                    elif self.five_per > 1:
                        self.five_per -= 2
            else:
                user.six_statis = 0
                user.six_per = 2
                self.five_per, self.four_per, self.three_per = 8, 50, 40

            cache.append(self.generate_operator(ans))
            if i % 10 == 0:
                gacha_ranks.append(cache)
                cache = []
        if cache:
            gacha_ranks.append(cache)
        return gacha_ranks

    def generate_operator(self, rank: str) -> Operator:
        """
        抽取单个干员

        :param rank: 干员等级，从 六、五、四、三中选取
        :return: 生成的干员信息
        """
        card_list = self.data["operators"][rank].copy()
        if rank == "六":
            # if (six_per := self.data["six_per"]) >= 1.0:
            #     return Operator(random.choice(self.data["up_six_list"]), 6)
            # up_res = random.choice(self.data["up_six_list"] + self.data["up_limit"])
            # for c in self.data["up_alert_limit"]:
            #     card_list.extend([c for _ in range(5)])
            # card_list.extend(
            #     [up_res for _ in range(int(len(card_list) * six_per / (1 - six_per)))]
            # )
            return Operator(random.choice(card_list), 6)
        if rank == "五":
            # if (five_per := self.data["five_per"]) >= 1.0:
            #     return Operator(random.choice(self.data["up_five_list"]), 5)
            # up_res = random.choice(self.data["up_five_list"])
            # card_list.extend(
            #     [up_res for _ in range(int(len(card_list) * five_per / (1 - five_per)))]
            # )
            return Operator(random.choice(card_list), 5)
        if rank == "四":
            # if self.data["up_four_list"]:
            #     four_per = self.data["four_per"]
            #     up_res = random.choice(self.data["up_four_list"])
            #     card_list.extend(
            #         [
            #             up_res
            #             for _ in range(int(len(card_list) * four_per / (1 - four_per)))
            #         ]
            #     )
            return Operator(random.choice(card_list), 4)
        return Operator(random.choice(card_list), 3)

    def create_image(
        self,
        user: GachaUser,
        result: List[List[Operator]],
        count: int = 1,
        relief: bool = False,
    ) -> bytes:
        """
        将抽卡结果转为图片

        :param user: 抽卡用户
        :param result: 本次抽卡结果
        :param count: 抽卡数量
        :param relief: 是否需要浮雕效果
        :return: 生成的图片bytes
        """
        tile = 20
        width_base = 720
        color_base = 0x40
        color_bases = (color_base, color_base, color_base)
        height = tile * int(math.ceil(count / 10) + 1) + 130
        img = Image.new("RGB", (width_base, height), color_bases)
        # 绘画对象
        draw = ImageDraw.Draw(img)

        draw.text(
            (tile, tile), "博士小心地拉开了包的拉链...会是什么呢？", fill="lightgrey", font=font_base
        )

        pool = f"当前卡池:【{self.data['name']}】"
        l, _, lw, __ = font_base.getbbox(pool)
        draw.text(
            (width_base - lw - l - tile, tile),
            pool,
            fill="lightgrey",
            font=font_base,
        )
        if relief:
            xi = 2 * tile
            yi = 2 * tile + 4
            xj = width_base - (2 * tile)
            yj = tile * (int(math.ceil(count / 10)) + 4)
            for i in range(3, 0, -1):
                d = int(color_base * 0.2) // 4
                r = int(color_base * 0.8) + i * d
                draw.rounded_rectangle(
                    (xi - i, yi - i, xi + i, yj + i), radius=16, fill=(r, r, r)
                )
                draw.rounded_rectangle(
                    (xj - i, yi - i, xj + i, yj + i), radius=16, fill=(r, r, r)
                )
            for i in range(4, 0, -1):
                r = (color_base // 4) * i
                draw.rounded_rectangle(
                    (xi - i, yi - i, xj + i, yi + i),
                    radius=20,
                    fill=(r, r, r, int(256 * 0.6)),
                )
                d = (0xFF - color_base) // 4
                r = 0xFF - i * d
                draw.rounded_rectangle(
                    (xi - i, yj - i, xj + i, yj + i),
                    radius=20,
                    fill=(r, r, r, int(256 * 0.8)),
                )
        for i, ots in enumerate(result):
            base = tile * 3
            if relief:
                draw.rounded_rectangle(
                    (
                        base,
                        tile * (i + 3) + 4,
                        base + tile * 3 * len(ots) - 2,
                        tile * (i + 4) + 3,
                    ),
                    radius=2,
                    fill=(color_base // 2, color_base // 2, color_base // 2),
                )
            for operator in ots:
                width = tile * 3
                length = len(operator.name)
                length = max(length, 3)
                font_size = int(3 * font_base.size / length)
                font = font_base.font_variant(size=font_size)
                l, t, lw, th = font.getbbox(operator.name)
                width_offset = (width - lw - l) // 2
                height_offset = 1 + (tile - th - t) // 2

                draw.rounded_rectangle(
                    (base, tile * (i + 3) + 2, base + width - 2, tile * (i + 4)),
                    radius=2,
                    fill=self.color[operator.rarity],
                )
                half_color: Tuple[int, int, int] = (
                    self.color[operator.rarity][0] // 2, 
                    self.color[operator.rarity][1] // 2, 
                    self.color[operator.rarity][2] // 2
                )
                draw.text(
                    (base + width_offset, tile * (i + 3) + height_offset),
                    operator.name,
                    fill="#ffffff",
                    stroke_width=1,
                    stroke_fill=half_color,
                    font=font,
                )
                base += width
        draw.text(
            (tile, height - 3 * tile + 10),
            f"博士已经抽取了{user.six_statis}次没有6星了" f"\n当前出6星的机率为 {user.six_per}%",
            fill="lightgrey",
            font=font_base,
        )
        imageio = BytesIO()
        img.save(
            imageio,
            format="JPEG",
            quality=95,
            subsampling=2,
            qtables="web_high",
        )
        return imageio.getvalue()

    def gacha_with_img(self, user: GachaUser, count: int = 1, relief: bool = True):
        return self.create_image(user, (self.gacha(user, count)), count, relief)
