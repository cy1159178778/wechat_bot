import json
import os
import random


current_dir = os.path.dirname(os.path.abspath(__file__))


def load_tarot_data():
    with open(os.path.join(current_dir, "batarot.json"), 'r', encoding='utf-8') as file:
        batarot_json = json.load(file)
    return batarot_json['cards']


def load_spread_data():
    with open(os.path.join(current_dir, "batarot_spread.json"), 'r', encoding='utf-8') as file:
        batarot_spread = json.load(file)
        return batarot_spread


def random_tarot_card(cards_dict):
    card_key = random.choice(list(cards_dict.keys()))
    card = cards_dict[card_key]
    card_name = card['name_cn']
    card_meaning_up = card['meaning']['up']
    card_meaning_down = card['meaning']['down']

    card_file = f"tarot_{card_key}.png"

    return card_name, card_meaning_up, card_meaning_down, card_file


def load_fortune_descriptions():
    with open(os.path.join(current_dir, "batarot_fortune.json"), 'r', encoding='utf-8') as file:
        return json.load(file)
