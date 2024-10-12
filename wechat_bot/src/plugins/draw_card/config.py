from pydantic import BaseModel, Extra
from pathlib import Path

# from configs.config import Config as AConfig
DATA_PATH = Path("data/")
IMAGE_PATH = Path("data/image/")
try:
    import ujson as json
except ModuleNotFoundError:
    import json


# 原神
class GenshinConfig(BaseModel, extra=Extra.ignore):
    GENSHIN_FIVE_P: float = 0.006
    GENSHIN_FOUR_P: float = 0.051
    GENSHIN_THREE_P: float = 0.43
    GENSHIN_G_FIVE_P: float = 0.016
    GENSHIN_G_FOUR_P: float = 0.13
    I72_ADD: float = 0.0585


# 明日方舟
class PrtsConfig(BaseModel, extra=Extra.ignore):
    PRTS_SIX_P: float = 0.02
    PRTS_FIVE_P: float = 0.08
    PRTS_FOUR_P: float = 0.48
    PRTS_THREE_P: float = 0.42


# 赛马娘
class PrettyConfig(BaseModel, extra=Extra.ignore):
    PRETTY_THREE_P: float = 0.03
    PRETTY_TWO_P: float = 0.18
    PRETTY_ONE_P: float = 0.79


# 坎公骑冠剑
class GuardianConfig(BaseModel, extra=Extra.ignore):
    GUARDIAN_THREE_CHAR_P: float = 0.0275
    GUARDIAN_TWO_CHAR_P: float = 0.19
    GUARDIAN_ONE_CHAR_P: float = 0.7825
    GUARDIAN_THREE_CHAR_UP_P: float = 0.01375
    GUARDIAN_THREE_CHAR_OTHER_P: float = 0.01375
    GUARDIAN_EXCLUSIVE_ARMS_P: float = 0.03
    GUARDIAN_FIVE_ARMS_P: float = 0.03
    GUARDIAN_FOUR_ARMS_P: float = 0.09
    GUARDIAN_THREE_ARMS_P: float = 0.27
    GUARDIAN_TWO_ARMS_P: float = 0.58
    GUARDIAN_EXCLUSIVE_ARMS_UP_P: float = 0.01
    GUARDIAN_EXCLUSIVE_ARMS_OTHER_P: float = 0.02


# 公主连结
class PcrConfig(BaseModel, extra=Extra.ignore):
    PCR_THREE_P: float = 0.025
    PCR_TWO_P: float = 0.18
    PCR_ONE_P: float = 0.795
    PCR_G_THREE_P: float = 0.025
    PCR_G_TWO_P: float = 0.975


# 碧蓝航线
class AzurConfig(BaseModel, extra=Extra.ignore):
    AZUR_FIVE_P: float = 0.012
    AZUR_FOUR_P: float = 0.07
    AZUR_THREE_P: float = 0.12
    AZUR_TWO_P: float = 0.51
    AZUR_ONE_P: float = 0.3


# 命运-冠位指定
class FgoConfig(BaseModel, extra=Extra.ignore):
    FGO_SERVANT_FIVE_P: float = 0.01
    FGO_SERVANT_FOUR_P: float = 0.03
    FGO_SERVANT_THREE_P: float = 0.4
    FGO_CARD_FIVE_P: float = 0.04
    FGO_CARD_FOUR_P: float = 0.12
    FGO_CARD_THREE_P: float = 0.4


# 阴阳师
class OnmyojiConfig(BaseModel, extra=Extra.ignore):
    ONMYOJI_SP: float = 0.0025
    ONMYOJI_SSR: float = 0.01
    ONMYOJI_SR: float = 0.2
    ONMYOJI_R: float = 0.7875


# 碧蓝档案
class BaConfig(BaseModel, extra=Extra.ignore):
    BA_THREE_P: float = 0.025
    BA_TWO_P: float = 0.185
    BA_ONE_P: float = 0.79
    BA_G_TWO_P: float = 0.975


class Config(BaseModel, extra=Extra.ignore):
    # 开关
    PRTS_FLAG: bool = True
    GENSHIN_FLAG: bool = True
    PRETTY_FLAG: bool = True
    GUARDIAN_FLAG: bool = True
    PCR_FLAG: bool = True
    AZUR_FLAG: bool = True
    FGO_FLAG: bool = True
    ONMYOJI_FLAG: bool = True
    BA_FLAG: bool = True

    # 其他配置
    PCR_TAI: bool = True
    SEMAPHORE: int = 5

    # 抽卡概率
    prts: PrtsConfig = PrtsConfig()
    genshin: GenshinConfig = GenshinConfig()
    pretty: PrettyConfig = PrettyConfig()
    guardian: GuardianConfig = GuardianConfig()
    pcr: PcrConfig = PcrConfig()
    azur: AzurConfig = AzurConfig()
    fgo: FgoConfig = FgoConfig()
    onmyoji: OnmyojiConfig = OnmyojiConfig()
    ba: BaConfig = BaConfig()


# DRAW_PATH = Path("data/draw_card").absolute()
DRAW_PATH = Path(IMAGE_PATH) / "draw_card"
# try:
#     DRAW_PATH = Path(global_config.draw_path).absolute()
# except:
#     pass
config_path = Path(DATA_PATH) / "draw_card" / "draw_card_config" / "draw_card_config.json"

draw_config: Config = Config()

# for game_flag, game_name in zip(
#     [
#         "PRTS_FLAG",
#         "GENSHIN_FLAG",
#         "PRETTY_FLAG",
#         "GUARDIAN_FLAG",
#         "PCR_FLAG",
#         "AZUR_FLAG",
#         "FGO_FLAG",
#         "ONMYOJI_FLAG",
#         "PCR_TAI",
#         "BA_FLAG",
#     ],
#     [
#         "明日方舟",
#         "原神",
#         "赛马娘",
#         "坎公骑冠剑",
#         "公主连结",
#         "碧蓝航线",
#         "命运-冠位指定（FGO）",
#         "阴阳师",
#         "pcr台服卡池",
#         "碧蓝档案",
#     ],
# ):
#     AConfig.add_plugin_config(
#         "draw_card",
#         game_flag,
#         True,
#         name="游戏抽卡",
#         help_=f"{game_name} 抽卡开关",
#         default_value=True,
#         type=bool,
#     )
# AConfig.add_plugin_config(
#     "draw_card", "SEMAPHORE", 5, help_=f"异步数据下载数量限制", default_value=5, type=int
# )
#

