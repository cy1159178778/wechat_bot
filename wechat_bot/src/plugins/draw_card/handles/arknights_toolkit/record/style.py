"""
本文件控制绘图样式
非常不建议修改本文件中的内容
"""
from math import ceil

"""输出图片的样式"""
# 图像宽度
base_img_w = 1000
# 不包括新干员信息的图像高度
base_img_h = 435

base_img_back_color = "#0d0d0d"  # 底图颜色
img_bcolor = "#1f1f1f"  # 块颜色
title_fcolor = "white"  # 表题文字颜色
text_fcolor = "#f2f2f2"  # 全局文字颜色
pie_percent_color = "white"  # 图表百分比颜色
op_fcolor = "#1f1f1f"  # 干员头像底图颜色#333333
star_colors = {  # 干员头像框颜色
    1: "#fafafa",  # 4d4d4d
    2: "#fafafa",  # 4d4d4d
    3: "#bfbdb4",  # 4d4d4d
    4: "#7c6db9",  # 9f496e
    5: "#deab5f",  # d98666
    6: "#ffA101",  # 并不会用到6星的
}
pie_colors = ("#595959", "#333333", "#7f7f7f", "#1F77B4")  # 饼图颜色，（3，4，5，6）
pie_explode = (0, 0, 0, 0.2)  # 某部分突出显示，值越大，距离中心越远
pie_angle = 45  # 开始角度
pie_wedgeprops = {
    # 'edgecolor':'#f2f2f2',  # 内外框颜色
    # 'linestyle':'-',  # 线型
    # 'linewidth':3,  # 线宽
    # 'facecolor':'white',
    # 'alpha':0.5,  # 透明度
    # 更多参考matplotlib.patches.Wedge
}

#
title_drawer_p = {
    "w": "",
    "h": "",
    "pos": (0, 0),  # 直接0,0，可以不用调
    "back_img_w": "",
    "back_img_h": "",
    "back_img_pos": (0, 0),
}

title_fsize_prop = 0.1
title_pos_prop = 0.1
title_p = {"fsize": title_fsize_prop * base_img_h, "color": "white", "pos": (320, 46)}

sub_title_fsize_prop = 0.75
sub_title_pos_prop = 1.2
sub_title_p = {
    "fsize": sub_title_fsize_prop * title_p["fsize"],
    "color": text_fcolor,
    "pos": (title_p["pos"][0] - 60, title_p["pos"][1] + 58),
}

# pie_p_pos_y = 1.2*(sub_title_p['fsize'] + title_p['fsize'])
pie_p_pos_y = 160
x_step = 0.012 * base_img_w  # 每个块之间的间隔

pie_p_title_fsize_prop = 0.14
pie_p_text_fsize_prop = 0.11
pie_p_percent_fsize_prop = 0.07
# 设置字体大小时要考虑缩放

pie_star_p = {
    "w": 240,
    "h": 240,
    "pos": (x_step, pie_p_pos_y),
    "title_fcolor": title_fcolor,
    "text_fcolor": text_fcolor,
    "percent_fcolor": pie_percent_color,
    "radii": 14,
    "bcolor": img_bcolor,
}
pie_star_p["title_fsize"] = pie_star_p["h"] * pie_p_title_fsize_prop
pie_star_p["text_fsize"] = pie_star_p["h"] * pie_p_text_fsize_prop
pie_star_p["percent_fsize"] = pie_star_p["h"] * pie_p_percent_fsize_prop

# 直方图样式
histo_pool_p = {
    "pos": (pie_star_p["w"] + pie_star_p["pos"][0] + x_step, pie_p_pos_y),
    "w": pie_star_p["h"] * 7 / 6,
    "h": pie_star_p["h"],
    "title_fsize": pie_star_p["title_fsize"],
    "title_fcolor": title_fcolor,
    "tick_fsize": pie_star_p["text_fsize"],
    "tick_fcolor": text_fcolor,
    "radii": 14,
    "bcolor": img_bcolor,
}


# 星级描述样式
desc_title_fsize_prop = 0.11
desc_text_fsize_prop = 0.08
desc_w_prop = 0.6
desc_star_p = {
    "parts": ["title", "text"],
    "bimage": {
        "w": pie_star_p["h"] * 0.8,
        "h": pie_star_p["h"],
        "radii": 14,  # 圆角半径
        "pos": (histo_pool_p["w"] + histo_pool_p["pos"][0] + x_step, pie_p_pos_y),
        "bcolor": img_bcolor,
    },
    "title": {
        "color": title_fcolor,
    },
    "text": {
        "color": text_fcolor,
    },
}
desc_star_p["title"]["fsize"] = desc_title_fsize_prop * desc_star_p["bimage"]["h"]
desc_star_p["text"]["fsize"] = desc_text_fsize_prop * desc_star_p["bimage"]["h"]
desc_star_p["title"]["pos"] = (
    0.03 * desc_star_p["bimage"]["w"],
    0.03 * desc_star_p["bimage"]["w"],
)
desc_star_p["text"]["pos"] = (
    0.03 * desc_star_p["bimage"]["w"],
    1.12 * (desc_star_p["title"]["pos"][1] + desc_star_p["title"]["fsize"]),
)
# 水位情况

desc_shuiwei_p = {
    "parts": ["title", "text"],
    "bimage": {
        "w": pie_star_p["h"] * 0.95,
        "h": pie_star_p["h"],
        "radii": 14,  # 圆角半径
        "pos": (
            desc_star_p["bimage"]["w"] + desc_star_p["bimage"]["pos"][0] + x_step,
            pie_p_pos_y,
        ),
        "bcolor": img_bcolor,
    },
    "title": {
        "color": title_fcolor,
    },
    "text": {
        "color": text_fcolor,
    },
}
desc_shuiwei_p["title"]["fsize"] = desc_title_fsize_prop * pie_star_p["h"]
desc_shuiwei_p["text"]["fsize"] = desc_text_fsize_prop * pie_star_p["h"]
desc_shuiwei_p["title"]["pos"] = (
    0.03 * desc_shuiwei_p["bimage"]["w"],
    0.03 * desc_shuiwei_p["bimage"]["w"],
)
desc_shuiwei_p["text"]["pos"] = (
    0.03 * desc_shuiwei_p["bimage"]["w"],
    1.12 * (desc_shuiwei_p["title"]["pos"][1] + desc_shuiwei_p["title"]["fsize"]),
)


# 卡池情况描述样式
desc_pool_p = {
    "pos": (desc_star_p["bimage"]["w"] + desc_star_p["bimage"]["pos"][0], pie_p_pos_y),
    "w": pie_star_p["h"] * desc_w_prop,
    "h": pie_star_p["h"],
    "color": "brown",
    "fsize": desc_star_p["text"]["fsize"],
}
desc_pool_p["fsize"] = desc_text_fsize_prop * desc_pool_p["h"]

# 水位情况描述样式

"""

角色框样式参数

"""


def get_char_drawer_h(line_cnt):
    return int(
        char_title_p["fsize"]
        + 2 * indi_char_drawer_p["step"]
        + line_cnt * (indi_char_drawer_p["step"] + indi_char_drawer_p["h"])
    )


# 一个drawer 46%的空间
w_prop = 0.45
# 整个大的角色框样式参数
char_drawer_p = {
    "w": base_img_w / 2.15,
    "h": get_char_drawer_h,  # 需要在制图时重新赋值
    "pos_newchar": ((0.5 - w_prop) / 2 * base_img_w, base_img_h),  # x,y
    "pos_star6char": (
        x_step + 0.5 * base_img_w,
        base_img_h,
    ),  # 'pos_star6char':((0.5+(0.5-w_prop)/2)*base_img_w,base_img_h)
    "bcolor": img_bcolor,  # x,y
    "radii": 15,
}

# 大角色框标题样式
char_title_p = {
    "fsize": 0.07 * base_img_h,
    "pos": (0.02 * char_drawer_p["w"], 0.02 * char_drawer_p["w"]),
    "color": text_fcolor,
}

# 每行角色框的高度参数
line_prop = 0.2

# 一行两个drawer的样式
indi_w_prop = 0.475  # 单个drawer的宽度占比


def get_line_drawer_pos0(line):
    # 根据行数获取linedrawer的摆放位置
    return (
        int((0.5 - indi_w_prop) / 2 * char_drawer_p["w"]),
        char_title_p["fsize"]
        + 2 * indi_char_drawer_p["step"]
        + line * (indi_char_drawer_p["step"] + indi_char_drawer_p["h"]),
    )


def get_line_drawer_pos1(line):
    # 根据行数获取linedrawer的摆放位置
    return (
        int((0.5 + (0.5 - indi_w_prop) / 2) * char_drawer_p["w"]),
        char_title_p["fsize"]
        + 2 * indi_char_drawer_p["step"]
        + line * (indi_char_drawer_p["step"] + indi_char_drawer_p["h"]),
    )


step_prop = 0.02
indi_char_drawer_p = {
    "h": line_prop * base_img_h,
    "w": indi_w_prop * char_drawer_p["w"],  # 稍微让出一些地方
    "pos0": get_line_drawer_pos0,
    "pos1": get_line_drawer_pos1,
    "step": step_prop * base_img_h,
    "bcolor": op_fcolor,
}
# 头像及文字的样式
profile_prop = 0.75
profile_pos_y = int((1 - profile_prop) / 2 * indi_char_drawer_p["h"])
profile_w = int(profile_prop * indi_char_drawer_p["h"])
char_text_p = {
    "profile_w": profile_w,
    "profile_pos": (profile_pos_y * 0.3, profile_pos_y),
    "char_name_fsize": int(0.19 * indi_char_drawer_p["h"]),
    "char_name_color": title_fcolor,
    "char_desc_fsize": int(0.16 * indi_char_drawer_p["h"]),
    "char_desc_color": text_fcolor,
    "name_pos": (profile_pos_y * 1.5 + profile_w, profile_pos_y),
}

char_text_p["desc_pos"] = (
    profile_pos_y * 1.5 + profile_w,
    profile_pos_y + char_text_p["char_name_fsize"] + 0.05 * indi_char_drawer_p["h"],
)

title_img_p = {
    "pos": (0, 0),
}


def get_bottom_img_pos():
    return (
        0,
        int(
            char_drawer_p["pos_newchar"][1] + char_drawer_p["h_int"] + 0.03 * base_img_h
        ),
    )


def get_date_text_pos():
    return (
        535,
        int(
            char_drawer_p["pos_newchar"][1]
            + char_drawer_p["h_int"]
            + 0.445 * base_img_h
        ),
    )


bottom_img_p = {"pos": get_bottom_img_pos, "w": 1000, "h": 240}

date_text_p = {"fsize": 38, "fcolor": "white", "pos": get_date_text_pos}

style_params = [
    title_p,
    sub_title_p,
    pie_star_p,
    desc_star_p,
    desc_pool_p,
    histo_pool_p,
    desc_shuiwei_p,
    char_drawer_p,
    char_title_p,
    indi_char_drawer_p,
    char_text_p,
    title_img_p,
    bottom_img_p,
]
# 全部置为int


def parse2int(_params: dict):
    for k in _params:
        if isinstance(_params[k], (int, float)):
            _params[k] = int(_params[k])
        elif isinstance(_params[k], tuple):
            _params[k] = tuple(map(int, _params[k]))
        elif isinstance(_params[k], dict):
            parse2int(_params[k])
    return


for params in style_params:
    parse2int(params)


def get_img_wh(query_result: dict, base_h: int = base_img_h, base_w: int = base_img_w):
    # 根据六星及新干员数量计算输出的图像的高度
    mmax = max(
        query_result["star6char_info"]["count"],
        query_result["newchar_info"]["count"],
    )
    mmax = min(20, mmax)  # 高度不超过20个干员的高度
    char_line_cnt = ceil(mmax / 2)  # 可以排列几行
    base_h += int(1.2 * char_title_p["fsize"])
    base_h += get_char_drawer_h(char_line_cnt)
    base_h += int(bottom_img_p["h"])
    base_h += int(base_img_h * 0.03)
    char_drawer_p["h_int"] = char_drawer_p["h"](char_line_cnt)
    return (base_w, base_h), char_line_cnt


# __all__ = [
#     "get_char_drawer_h",
#     "get_line_drawer_pos0",
#     "get_line_drawer_pos1",
#     "get_bottom_img_pos",
#     "get_date_text_pos",
#     "parse2int",
#     "get_img_wh"
# ]
