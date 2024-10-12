import os
import time
import random
import hashlib
from pathlib import Path

from on import on_regex
from common import send_text, send_image
from .utils import load_tarot_data, load_spread_data, random_tarot_card, load_fortune_descriptions


base_path = Path(__file__).parent
img_path = os.path.join(base_path, "batarot_img")


def get_seed(user_id):
    content = str(user_id)
    sha256_obj = hashlib.md5(content.encode())
    hex_digest = sha256_obj.hexdigest()
    integer_value = int(hex_digest, 16)
    return integer_value


@on_regex(r"^(运势|塔罗牌运势)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    user_id = get_seed(sender)
    time_day = time.strftime("%Y%m%d", time.localtime())
    seed = int(str(user_id) + str(time_day))
    random.seed(seed)

    cards_dict = load_tarot_data()
    card_key = random.choice(list(cards_dict.keys()))
    card = cards_dict[card_key]
    card_name = card['name_cn']
    card_file = os.path.join(img_path, f"tarot_{card_key}.png")

    fortune_score = random.randint(1, 100)
    fortune_descriptions = load_fortune_descriptions()
    score_range = f"{(fortune_score - 1) // 10 * 10 + 1}-{(fortune_score - 1) // 10 * 10 + 10}"
    fortune_description = random.choice(fortune_descriptions[score_range])

    reply_text = f"\n今日塔罗牌：{card_name}\n今日运势指数：{fortune_score}\n运势解读：{fortune_description}\n"
    await send_text(reply_text, room_id, sender, sender_name)
    await send_image(room_id, card_file)


@on_regex(r"^(塔罗牌|随机塔罗牌)$")
async def _(**kwargs):
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")
    random.seed()
    cards_dict = load_tarot_data()
    card_name, card_meaning_up, card_meaning_down, card_file = random_tarot_card(cards_dict)

    reply_text = f"\n塔罗牌名称: {card_name}\n正位含义: {card_meaning_up}\n逆位含义: {card_meaning_down}\n"
    card_file = os.path.join(img_path, card_file)
    await send_text(reply_text, room_id, sender, sender_name)
    await send_image(room_id, card_file)


@on_regex(r"^塔罗牌解读\s*(.*)$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")

    random.seed()
    cards_dict = load_tarot_data()
    user_input = match_obj.group().strip()
    specific_card_key = None
    card_file = None

    if user_input == "塔罗牌解读":
        specific_card_key = random.choice(list(cards_dict.keys()))

    elif user_input.startswith("塔罗牌解读"):
        specific_card_input = user_input[5:].strip()

        if specific_card_input.isdigit() and specific_card_input in cards_dict:
            specific_card_key = specific_card_input
        else:
            specific_card_key = next(
                (key for key, card in cards_dict.items() if card['name_cn'].lower() == specific_card_input.lower()),
                None)

    if specific_card_key:
        card = cards_dict[specific_card_key]
        card_name = card['name_cn']
        card_description = "\n".join(card['description'])
        card_file = f"tarot_{specific_card_key}.png"
        reply_text = f"\n塔罗牌名称: {card_name}\n解读:\n{card_description}\n"
        card_file = os.path.join(img_path, card_file)
    else:
        reply_text = "未找到指定的塔罗牌或输入格式错误，请输入正确的卡牌编号或名称。"

    await send_text(reply_text, room_id, sender, sender_name)
    if card_file:
        await send_image(room_id, card_file)
