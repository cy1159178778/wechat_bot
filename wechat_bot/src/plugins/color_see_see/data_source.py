from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

import random

font_path: Path = Path(__file__).parent / "resources"


class UserScore:
    user_name: str
    score: int


class ColorGame:
    def __init__(self, block_column: int) -> None:
        self.block_column = block_column
        self.diff_block = random.randint(1, block_column ** 2)
        self.color_img = self.__create_blocks()
        self.scores: dict[str, UserScore] = {}

    def __create_blocks(self):
        block_num = self.block_column ** 2
        block_size = 2400 // self.block_column
        color_img = Image.new("RGBA", (2400, 2400), "white")
        draw = ImageDraw.Draw(color_img)
        r = random.randint(0, 192)
        g = random.randint(0, 192 - int(r * 0.299))
        b = random.randint(0, 192 - int(r * 0.299) - int(g * 0.587))
        font_size = max(8, 16 - self.block_column + 1) * 4
        for i in range(block_num):
            a = 255
            if i == self.diff_block - 1:
                a = int(80 * 255 / 100) + block_num * int(1 * 255 / 100)
                if a > int(95 * 255 / 100):
                    a = int(95 * 255 / 100)
            color = (r, g, b, a)
            x = (i % self.block_column) * block_size
            y = (i // self.block_column) * block_size
            draw.rounded_rectangle(
                (x, y, x + block_size - 16, y + block_size - 16), 12, fill=color)
            draw.text((x + 16, y + 16), str(i+1),
                      font=ImageFont.truetype(
                        str(font_path / "arial.ttf"), font_size), fill="white")
        color_img = color_img.resize((600, 600), Image.Resampling.LANCZOS)
        buf = BytesIO()
        color_img.save(buf, format="PNG")
        return buf.getvalue()

    def get_diff_block(self) -> int:
        return self.diff_block

    def get_color_img(self) -> bytes:
        return self.color_img

    def get_next_img(self) -> bytes:
        self.block_column += 1
        self.diff_block = random.randint(1, self.block_column ** 2)
        self.color_img = self.__create_blocks()
        return self.color_img

    def add_score(self, user_id: str, user_name: str):
        if user_id in self.scores:
            self.scores[user_id].score += self.block_column
        else:
            self.scores[user_id] = UserScore()
            self.scores[user_id].user_name = user_name
            self.scores[user_id].score = self.block_column

    def get_scores(self, user_id: str) -> int:
        return self.scores[user_id].score
