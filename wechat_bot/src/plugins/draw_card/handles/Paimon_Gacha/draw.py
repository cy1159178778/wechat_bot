import json
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFont

from .data_source import get_once_data


base_path = Path(__file__).parent

with open(base_path / "gacha_res/gacha_info.json", encoding="utf-8") as f:
    gacha_data = json.load(f)

with open(base_path / "gacha_res/type.json", encoding="utf-8") as f:
    type_json = json.load(f)

GACHA_RES = base_path / "gacha_res"
count_font = ImageFont.truetype(str(GACHA_RES / 'hywh.ttf'), 35)


def draw_center_text(draw_target, text: str, left_width: int, right_width: int, height: int, fill: str, font):
    """
    绘制居中文字
    :param draw_target: ImageDraw对象
    :param text: 文字
    :param left_width: 左边位置横坐标
    :param right_width: 右边位置横坐标
    :param height: 位置纵坐标
    :param fill: 字体颜色
    :param font: 字体
    """
    text_length = draw_target.textlength(text, font=font)
    draw_target.text((left_width + (right_width - left_width - text_length) / 2, height), text, fill=fill,
                     font=font)


def draw_single_item(rank, item_type, name, element, count, dg_time):
    bg = Image.open(GACHA_RES / f'{rank}_background.png').resize((143, 845))
    item_img = Image.open(GACHA_RES / item_type / f'{name}.png')
    rank_img = Image.open(GACHA_RES / f'{rank}_star.png').resize((119, 30))
    if item_type == '角色':
        item_img = item_img.resize((item_img.size[0] + 12, item_img.size[1] + 45))
        item_img.alpha_composite(rank_img, (4, 510))

        item_type_icon = Image.open(GACHA_RES / '元素' / f'{element}.png').resize((80, 80))
        item_img.alpha_composite(item_type_icon, (25, 420))
        bg.alpha_composite(item_img, (3, 125))

    else:
        bg.alpha_composite(item_img, (3, 240))
        bg.alpha_composite(rank_img, (9, 635))

        if item_type_icon := type_json.get(name):
            item_type_icon = Image.open(GACHA_RES / '类型' / f'{item_type_icon}.png').resize((100, 100))

            bg.alpha_composite(item_type_icon, (18, 530))
    # if rank == 5 and count != -1:
    #     draw = ImageDraw.Draw(bg)
    #     draw_center_text(draw, f'{str(count)}抽', 0, 143, 750, 'white', count_font)
    #     if dg_time != -1:
    #         if dg_time == 3:
    #             draw_center_text(draw, '定轨结束', 0, 143, 785, 'white', count_font)
    #         else:
    #             draw_center_text(draw, f'定轨{str(dg_time)}/2', 0, 143, 785, 'white', count_font)
    return bg


def draw_ten_items(user_id, cards_list):
    gacha_list = []
    for _ in range(10):
        role = get_once_data(user_id, gacha_data).copy()
        gacha_list.append(role)
        cards_list.append([role['rank'], role['item_name']])
    gacha_list.sort(key=lambda x: x["rank"], reverse=True)
    img = Image.open(GACHA_RES / 'background.png')
    for i, wish in enumerate(gacha_list, start=1):
        rank = wish['rank']
        item_type = wish['item_type']
        name = wish['item_name']
        element = wish.get('item_attr') or type_json[name]
        count = wish['count']
        try:
            dg_time = wish['dg_time']
        except KeyError:
            dg_time = -1
        i_img = draw_single_item(rank, item_type, name, element, count, dg_time)
        img.alpha_composite(i_img, (105 + i_img.size[0] * i, 123))
    img.thumbnail((1024, 768))
    img2 = Image.new("RGB", img.size, (255, 255, 255))
    img2.paste(img, mask=img.split()[3])
    bio = BytesIO()
    img2.save(bio, format='JPEG', quality=100)
    return img2


def draw_gacha_img(user_id: int, num: int):
    cards_list = []
    if num == 1:
        img = draw_ten_items(user_id, cards_list)
    else:
        img = Image.new('RGB', (1024, 575 * num), (255, 255, 255))
        for i in range(num):
            one_img = draw_ten_items(user_id, cards_list)
            img.paste(one_img, (0, 575 * i))
    imageio = BytesIO()
    img.save(
        imageio,
        format="JPEG",
        quality=95,
        subsampling=2,
        qtables="web_high",
    )
    return imageio, cards_list
