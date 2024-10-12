user_data_dict = {}


def load_user_data(user_id: int) -> dict:
    if user_id in user_data_dict:
        return user_data_dict[user_id]
    new_data = {
        '抽卡数据': {
            '抽卡总数':         0,
            '4星出货数':        0,
            '5星出货数':        0,
            '4星up出货数':      0,
            '5星up出货数':      0,
            '角色池未出5星数':     0,
            '武器池未出5星数':     0,
            '常驻池未出5星数':     0,
            '角色池未出4星数':     0,
            '武器池未出4星数':     0,
            '常驻池未出4星数':     0,
            '角色池5星下次是否为up': False,
            '武器池5星下次是否为up': False,
            '角色池4星下次是否为up': False,
            '武器池4星下次是否为up': False,
            '定轨武器名称':       '',
            '定轨能量':         0
        },
        '角色列表': {},
        '武器列表': {}
    }
    user_data_dict[user_id] = new_data
    return new_data


def save_user_data(user_id: int, data: dict):
    user_data_dict[user_id] = data
