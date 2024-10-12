import json
import math
from datetime import datetime
from pathlib import Path
from random import Random
from typing import Dict, List, Literal, Optional, TypedDict


class Tags(TypedDict):
    position: str
    detail: List[str]


class SubCareer(TypedDict):
    name: str
    block: str
    attack_speed: str
    cost_basic: int
    talent: str
    tags: Tags


class Career(TypedDict):
    name: str
    info: List[SubCareer]


class Skill(TypedDict):
    cover: List[Literal["自动回复", "攻击回复", "受击回复"]]
    trigger: List[Literal["自动触发", "手动触发"]]
    detail: Dict[Literal["need", "none"], List[str]]


class Information(TypedDict):
    career: List[Career]
    organize: List[str]
    homeland: List[str]
    race: List[str]
    skill: Skill
    phy_exam_evaul: List[str]


class RandomOperator:
    """依据名称随机生成干员"""

    rand_operator_dict: Information

    def __init__(self, path: Optional[str] = None):
        """
        :param path: 模板文件路径
        """
        _path = (
            Path(path)
            if path
            else Path(__file__).parent / "resource" / "operator_template.json"
        )
        with _path.open("r+", encoding="utf-8") as f:
            self.rand_operator_dict = json.load(f)

    def generate(self, name: str) -> str:
        """
        依据名称随机生成干员
        """
        rand = Random()
        count = sum(ord(char) for char in name)
        now = datetime.now()
        rand.seed(count + (now.day * now.month) + now.hour + now.minute + now.year)

        career_dict = rand.choice(self.rand_operator_dict["career"])
        career_name = career_dict["name"]
        career_info_dict = rand.choice(career_dict["info"])

        sex = "男" if rand.randint(1, 2) == 1 else "女"
        career_detail = career_info_dict["name"]
        level = rand.randint(3, 6)
        cost = (
            career_info_dict["cost_basic"]
            + level
            - (2 if rand.randint(0, 4) >= 2 else rand.randint(0, 1))
        )
        attack_speed = career_info_dict["attack_speed"]
        block = career_info_dict["block"]
        talent = career_info_dict["talent"]
        position = career_info_dict["tags"]["position"]
        tags = f"{position} {rand.choice(career_info_dict['tags']['detail'])}"
        infect = "参照医学检测报告，确认为" + ("感染者。" if rand.randint(0, 10) > 5 else "非感染者。")
        race = rand.choice(self.rand_operator_dict["race"])
        homeland = rand.choice(self.rand_operator_dict["homeland"])
        organize = rand.choice(self.rand_operator_dict["organize"])
        if organize.endswith("homeland"):
            organize = rand.choice(self.rand_operator_dict["homeland"])
        height = rand.randint(0, 25) + (165 if sex == "男" else 155)
        fight_exp = (
            rand.randint(0, 6) if rand.randint(0, 10) > 2 else rand.randint(6, 20)
        )
        skills = []
        for i in range(1, 2 if level < 4 else (3 if level < 6 else 4)):
            cover = rand.choice(self.rand_operator_dict["skill"]["cover"])
            trigger = rand.choice(self.rand_operator_dict["skill"]["trigger"])
            total = rand.randint(1, 120 if cover == "自动回复" else 24)
            start = total - rand.randint(1, total)
            detail = rand.choice(
                list(self.rand_operator_dict["skill"]["detail"].keys())
            )
            if career_detail == "处决者":
                skills.append(f"【{i}】被动\n  初始 0; 消耗 0; 持续 -")
                continue
            if position == "远程位" and cover == "受击回复":
                cover = rand.choice(["自动回复", "攻击回复"])
            if career_name == "先锋" and cover == "受击回复":
                cover = rand.choice(["自动回复"])
            if detail == "need":
                last = rand.randint(
                    1,
                    math.ceil(total + 1 / 2)
                    + (0 if rand.randint(0, 10) > 2 else rand.randint(1, start + 1)),
                )
                content = rand.choice(
                    self.rand_operator_dict["skill"]["detail"][detail]
                )
                if content == "-":
                    skills.append(
                        f"【{i}】{cover}/{trigger}\n  初始 {start}; 消耗 {total}; 持续 {last}s"
                    )
                else:
                    skills.append(
                        f"【{i}】{cover}/手动触发\n  初始 {start}; 消耗 {total}; 持续 {last}s\n  {content}"
                    )
            else:
                content = rand.choice(
                    self.rand_operator_dict["skill"]["detail"][detail]
                )
                if content == "-":
                    skills.append(
                        f"【{i}】{cover}/{trigger}\n  初始 {start}; 消耗 {total}; 持续 0s"
                    )
                else:
                    if content.startswith("可充能") or content == "持续时间无限":
                        trigger = "自动触发"
                    else:
                        trigger = "手动触发"
                    if content.endswith("持续时间无限"):
                        start = 0
                        if career_detail == "行商":
                            total = total if total < 15 else math.ceil(total / 5)
                    elif content.startswith("可充能") or content.startswith(
                        "可以在以下状态和初始状态间切换"
                    ):
                        start = 0
                        total = total if total < 20 else math.ceil(total / 5)
                    skills.append(
                        f"【{i}】{cover}/{trigger}\n  初始 {start}; 消耗 {total}; 持续 -\n  {content}"
                    )
        skill = "\n".join(skills)
        return "\n".join(
            [
                f"{name}",
                f"{'★' * level}",
                f"【性别】{sex}",
                f"【职业】{career_name}-{career_detail}",
                f"【初始费用】{cost}",
                f"【阻挡数】{block}",
                f"【攻击速度】{attack_speed}",
                f"【特性】{talent}",
                f"【标签】{tags}",
                "\n",
                f"【种族】{race}",
                f"【身高】{height} cm",
                f"【出生地】{homeland}",
                f"【所属阵营】{organize}",
                f"【战斗经验】{'无' if fight_exp == 0 else f'{fight_exp}年'}",
                "\n",
                f"【技能】\n{skill}",
                "\n",
                f"【矿石病感染情况】{infect}",
                f"【物理强度】{rand.choice(self.rand_operator_dict['phy_exam_evaul'])}",
                f"【战场机动】{rand.choice(self.rand_operator_dict['phy_exam_evaul'])}",
                f"【生理耐受】{rand.choice(self.rand_operator_dict['phy_exam_evaul'])}",
                f"【战术规划】{rand.choice(self.rand_operator_dict['phy_exam_evaul'])}",
                f"【战斗技巧】{rand.choice(self.rand_operator_dict['phy_exam_evaul'])}",
                f"【源石技艺适应性】{rand.choice(self.rand_operator_dict['phy_exam_evaul'])}",
            ]
        )
