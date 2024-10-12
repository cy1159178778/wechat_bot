import json
import os

path = r"F:\work\test_bot\src\plugins\Paimon_Gacha\gacha_res\gacha_info.json"
data = json.load(open(path, encoding="utf-8"))

set1 = {i.split(".")[0] for i in os.listdir(r"F:\work\test_bot\src\plugins\Paimon_Gacha\gacha_res\武器")}
set2 = {i.split(".")[0] for i in os.listdir(r"F:\work\test_bot\src\plugins\Paimon_Gacha\gacha_res\角色")}

path2 = r"F:\work\test_bot\src\plugins\Paimon_Gacha\gacha_res\type.json"
data2 = json.load(open(path2, encoding="utf-8"))
print(set1 - set(data2))
print(set2 - set(data2))

star_j4 = """
赛索斯
嘉明
夏沃蕾
夏洛蒂
菲米尼
琳妮特
绮良良
卡维
米卡
瑶瑶
珐露珊
莱依拉
坎蒂丝
多莉
柯莱
鹿野院平藏
久岐忍
云堇
五郎
托马
九条裟罗
早柚
烟绯
罗莎莉亚
辛焱
迪奥娜
芭芭拉
重云
北斗
香菱
行秋
雷泽
凝光
安柏
菲谢尔
砂糖
丽莎
诺艾尔
凯亚
班尼特
"""

star_j5 = """
克洛琳德
阿蕾奇诺
千织
闲云
娜维娅
芙宁娜
莱欧斯利
那维莱特
林尼
旅行者/水
白术
迪希雅
艾尔海森
流浪者
纳西妲
妮露
赛诺
提纳里
旅行者/草
夜兰
神里绫人
八重神子
申鹤
荒泷一斗
珊瑚宫心海
埃洛伊
雷电将军
宵宫
旅行者/雷
神里绫华
枫原万叶
优菈
胡桃
魈
甘雨
阿贝多
钟离
达达利亚
可莉
温迪
旅行者/岩
刻晴
旅行者
七七
迪卢克
琴
旅行者/风
莫娜
"""

star_w3 = """
冷刃
暗铁剑
飞天御剑
黎明神剑
旅行剑
吃虎鱼刀
沐浴龙血的剑
白铁大剑
飞天大御剑
铁影阔剑
以理服人
神射手之誓
弹弓
鸦羽弓
反曲弓
信使
魔导绪论
翡玉法球
讨龙英杰谭
甲级宝珏
异世界行记
黑缨枪
白缨枪
钺矛
"""

star_w4 = """
筑云
沙中伟贤的对答
「究极霸王超级魔剑」
水仙十字之剑
船坞长剑
便携动力锯
测距规
无垠蔚蓝之歌
勘探钻机
狼牙
灰河渡手
海渊终曲
聊聊棒
浪影阔剑
静谧之曲
烈阳之嗣
纯水流华
遗祀玉珑
峡湾长歌
公义的酬报
鹮穿之喙
饰铁之花
东花坊时雨
西福斯的月光
玛海菈的水色
流浪的晚星
风信之锋
原木刀
森林王器
王下近侍
竭泽
盈满之实
贯月矢
笼钓瓶一心
落霞
证誓之明瞳
辰砂之纺锤
恶王丸
曚云之月
断浪长鳍
衔珠海皇
掠食者
「渔获」
天目影打刀
桂木斩长正
破魔之弓
白辰之环
喜多院十文字
幽夜华尔兹
嘟嘟可故事集
暗巷闪光
暗巷猎手
风花之颂
暗巷的酒与诗
千岩古剑
千岩长枪
腐殖之剑
雪葬的星银
忍冬之果
龙脊长枪
铁蜂刺
匣里龙吟
祭礼剑
黑岩长剑
试作斩岩
宗室长剑
笛剑
降临之剑
黑剑
西风剑
钟剑
雨裁
螭骨剑
祭礼大剑
黑岩斩刀
白影剑
宗室大剑
西风大剑
试作古华
祭礼弓
绝弦
试作澹月
黑岩战弓
钢轮弓
宗室长弓
苍翠猎弓
弓藏
西风猎弓
流浪乐章
万国诸海图谱
匣里日月
祭礼残章
黑岩绯玉
宗室秘法录
试作金珀
西风秘典
昭心
匣里灭辰
黑岩刺枪
决斗之枪
试作星镰
宗室猎枪
西风长枪
流月针
"""

star_w5 = """
赦罪
赤月之形
有乐御簾切
鹤鸣余音
裁断
静水流涌之辉
万世流涌大典
金流监督
最初的大魔术
碧落之珑
苇海信标
裁叶萃光
图莱杜拉的回忆
千夜浮梦
圣显之钥
赤沙之杖
猎人之径
若水
波乱月白经津
神乐之真意
息灾
赤角石溃杵
冬极白星
不灭月华
薙草之稻光
雾切之回光
飞雷之弦振
苍古自由之誓
松籁响起之时
终末嗟叹之诗
磐岩结绿
护摩之杖
斫峰之刃
无工之剑
尘世之锁
贯虹之槊
风鹰剑
天空之刃
天空之傲
狼的末路
阿莫斯之弓
天空之翼
天空之卷
四风原典
和璞鸢
天空之脊
"""


# r3_prob_list = []
# r4_prob_list = []
# r5_prob_list = []
# for i, j in enumerate([*set1, *set2], 1):
#     if j in star_j4:
#         r4_prob_list.append({
#               "is_up": 0,
#               "item_id": -i,
#               "item_name": j,
#               "item_type": "角色",
#               "order_value": i,
#               "rank": 4
#             })
#     elif j in star_j5:
#         r5_prob_list.append({
#             "is_up": 0,
#             "item_id": -i,
#             "item_name": j,
#             "item_type": "角色",
#             "order_value": i,
#             "rank": 5
#         })
#     elif j in star_w3:
#         r3_prob_list.append({
#             "is_up": 0,
#             "item_id": -i,
#             "item_name": j,
#             "item_type": "武器",
#             "order_value": i,
#             "rank": 3
#         })
#     elif j in star_w4:
#         r4_prob_list.append({
#             "is_up": 0,
#             "item_id": -i,
#             "item_name": j,
#             "item_type": "武器",
#             "order_value": i,
#             "rank": 4
#         })
#     elif j in star_w5:
#         r5_prob_list.append({
#             "is_up": 0,
#             "item_id": -i,
#             "item_name": j,
#             "item_type": "武器",
#             "order_value": i,
#             "rank": 5
#         })
#
# data["r3_prob_list"] = r3_prob_list
# data["r4_prob_list"] = r4_prob_list
# data["r5_prob_list"] = r5_prob_list
# json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
