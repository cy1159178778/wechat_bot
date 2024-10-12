import json
import platform
import shutil
import sqlite3 as sq
import time
from urllib.parse import unquote
from pathlib import Path
from typing import Any, List, Callable, Optional, Tuple, TypedDict

import httpx
from loguru import logger

""" 
读写数据库
"""
__all__ = ["get_player_uid", "ArkDatabase"]


def get_player_uid(token: str):
    """
    根据token从官网获取uid和昵称
    """
    # 两个服务器的请求头不一样
    base_url = "https://as.hypergryph.com/u8/user/info/v1/basic"
    user_info = {}
    # 官服
    payload = {"appId": 1, "channelMasterId": 1, "channelToken": {"token": f"{token}"}}
    content = httpx.post(base_url, json=payload).content  # 访问官服
    page_content = json.loads(content)
    try:
        if page_content["status"] != 0:  # b服
            token = unquote(token)
            payload = {"token": token}
            content = httpx.post(base_url, data=payload).content
            page_content = json.loads(content)
            assert page_content["status"] == 0, "无效token"
        user_info_source = page_content.get("data")
        user_info["uid"] = user_info_source.get("uid")
        user_info["name"] = user_info_source.get("nickName")
        user_info["channelMasterId"] = user_info_source.get("channelMasterId")
    except Exception as e:
        logger.error(e)
        raise RuntimeError("无效token") from e
    return user_info


class QueryParameter(TypedDict):
    op_type: str
    filter_func: Callable[[list], Any]
    cost_statis: bool


resource_path = Path(__file__).absolute().parent.parent / "resource" / "record"


class ArkDatabase:
    def __init__(
        self,
        db_path: Optional[str] = None,
        max_char_count: int = 20,
        max_pool_count: int = 8,
    ):
        """
        Args:
            db_path: 数据库存放路径，不填如则使用程序默认路径
        """
        if not db_path:
            os_type = platform.system()
            if os_type in ("Windows", "Linux"):
                db_dir = Path("~").expanduser() / ".arkrecord"
            else:
                logger.error(
                    "不支持的操作系统！开发者仅做了Windows和Linux的适配（由于没有苹果电脑）。建议联系开发者或自行修改源码。"
                )
                raise RuntimeError(
                    "不支持的操作系统！开发者仅做了Windows和Linux的适配（由于没有苹果电脑）。建议联系开发者或自行修改源码。"
                )
            db_dir.mkdir(parents=True, exist_ok=True)
            _db_path = db_dir / "arkgacha_record.db"
        else:
            _db_path = Path(db_path)
        _db_path16 = resource_path / "arkgacha_record.db"
        if not _db_path.exists():
            shutil.copy(_db_path16, _db_path)
        self.db = sq.connect(str(_db_path.absolute()))
        self.config = {
            "user_table": "user",
            "user_session_field": "user_session",
            "player_uid_field": "player_uid",
            "player_name_field": "player_name",
            "token_field": "token",
            "channel_field": "channel",
            "record_table": "record",
            "record_id_field": "record_id",
            "pool_name_field": "pool_name",
            "char_name_field": "char_name",
            "star_field": "star",
            "is_new_field": "is_new",
            "timestamp_field": "ts",
            "exclusive_field": "exclusive_type",
            "exclusive_common_name": "常规up池",
        }
        """数据库表、字段名称 """
        self.max_char_count = max_char_count  # 最多显示几个新角色/6星角色信息
        self.max_pool_count = max_pool_count  # 最多显示几个卡池信息
        self.cursor = self.db.cursor()

    def get_pool_in_view(self, player_uid: int):
        """获取视图中包含的卡池"""
        self.cursor.execute(
            f"select distinct {self.config['exclusive_field']} from v{player_uid}"
        )
        return [item[0] for item in self.cursor.fetchall()]

    def get_record_count(self, player_uid: int):
        """获取有效记录数量"""
        self.cursor.execute(
            f"select count(*) from {self.config['record_table']} "
            f"where {self.config['player_uid_field']} = ?",
            (player_uid,),
        )
        return self.cursor.fetchone()[0]

    def check_view(self, player_uid: int):
        """处理完成后删除视图"""
        self.cursor.execute(f"drop view if exists v{player_uid}")

    def _handle_max_count(self, player_uid: int, count: int):
        return self.get_record_count(player_uid) if count < 0 else count

    def create_view(
        self,
        target_pool: str,
        player_uid: int,
        max_record_count: int,
    ):
        """
        创建查询视图
        """
        max_record_count = self._handle_max_count(player_uid, max_record_count)
        # 查询所有卡池情况
        if target_pool == "all":
            create_view_sql = (
                f"create view v{player_uid} as "
                f"select * "
                f"from {self.config['record_table']} "
                f"where {self.config['player_uid_field']} = '{player_uid}' "
                f"order by {self.config['timestamp_field']} desc "
                f"limit {max_record_count};"
            )
            # logger.info(create_view_sql)
        else:  # 旧版单卡池查询用
            create_view_sql = (
                f"create view v{player_uid} as "
                f"select * "
                f"from {self.config['record_field']} "
                f"where {self.config['player_uid_field']} = '{player_uid}' "
                f"and {self.config['pool_name_field']} = '{target_pool}' "
                f"limit {max_record_count};"
            )
        self.cursor.execute(create_view_sql)
        return max_record_count

    def finish(self, player_uid: int):
        """查询完成后删除视图"""
        self.check_view(player_uid)

    def export_query(self, player_uid: int):
        self.cursor.execute(f"select * from v{player_uid}")
        res = self.cursor.fetchall()
        self.finish(player_uid)
        return res

    def query_all_items(self, target_pool: str, player_uid: int, max_record_count: int):
        max_record_count = self._handle_max_count(player_uid, max_record_count)

        def filter_star6char(info: List[str]):  # 判断是否为六星
            return info[2] == 6

        def filter_newchar(info: List[str]):  # 判断是否为新角色
            return info[3]

        star6char_query_param: QueryParameter = {
            "op_type": "六星干员",
            "filter_func": filter_star6char,
            "cost_statis": True,
        }

        newchar_query_param: QueryParameter = {
            "op_type": "新干员",
            "filter_func": filter_newchar,
            "cost_statis": False,
        }
        query_result = {
            "pool_info": self.pool_query(target_pool, player_uid, max_record_count),
            "star_info": self.star_query(player_uid, max_record_count),
            "shuiwei_info": self.shuiwei_query(player_uid),
            "newchar_info": self.char_query(newchar_query_param, player_uid),
            "star6char_info": self.char_query(star6char_query_param, player_uid),
            "fclientuent": self.fclientuent_query(player_uid),
            "max_count": max_record_count,
        }
        self.finish(player_uid)
        return query_result

    def pool_query(self, target_pool: str, player_uid: int, max_record_count: int):
        # 查询卡池信息
        if target_pool != "all":
            return {
                "desc": [target_pool],
                "count": [max_record_count],
            }
        pool_name_sql = (
            f"select {self.config['pool_name_field']}, count(*) "
            f"from v{player_uid} group by {self.config['pool_name_field']} "
            f"order by count(*) desc"
        )
        self.cursor.execute(pool_name_sql)
        pool_info = list(self.cursor.fetchall())[: self.max_pool_count][::-1]
        tmp_lst = {"desc": [], "count": [], "text": ""}
        for pool in pool_info:
            tmp_lst["desc"].append(
                f"{pool[0].split(' ')[0].strip()}"
            )  # 把复刻和常规算作一个，不然放不下了 todo:自适应图片宽度
            tmp_lst["count"].append(pool[1])
            tmp_lst["text"] += f"{pool[0]}:{pool[1]}抽\n\n"
        return tmp_lst

    def star_query(self, player_uid: int, max_record_count: int):
        """查询星级分布"""
        star_sql = (
            f"select {self.config['star_field']}, count(*) "
            f"from v{player_uid} group by {self.config['star_field']}"
        )
        self.cursor.execute(star_sql)
        star_info = sorted(self.cursor.fetchall())
        tmp_lst = {"desc": [], "count": [], "avg": [], "text": f"", "title": "星级分布"}
        for star in star_info:
            tmp_lst["desc"].append(f"{star[0]}星")
            tmp_lst["count"].append(star[1])
            avg = max_record_count / star[1]
            tmp_lst["avg"].append(avg)
            star_desc = f"{star[1]}个{star[0]}星"
            tmp_lst["text"] += f"{star_desc:8}{avg:.1f}抽/个\n\n"
        return tmp_lst

    def char_query(
        self,
        query_params: QueryParameter,
        player_uid: int,
    ):
        """获取获得的新角色或六星角色信息"""
        # 首先获取所有卡池
        tmp_info = {"chars": [], "count": 0}
        # 遍历普通池和每个限定池
        for pool in self.get_pool_in_view(player_uid):
            self.cursor.execute(
                f"select "
                f"{self.config['char_name_field']}, {self.config['timestamp_field']}, "
                f"{self.config['star_field']}, {self.config['is_new_field']}, "
                f"{self.config['pool_name_field']}, {self.config['record_id_field']} "
                f"from v{player_uid} where {self.config['exclusive_field']} = ? "
                f"order by {self.config['record_id_field']} desc",
                (pool,),
            )
            char_info_lst = list(self.cursor.fetchall())
            last_mark_idx = 1e20  # 上一次获得六星时的序号
            char_info_lst = char_info_lst[::-1]
            for idx, char_info in enumerate(char_info_lst):  # 反过来遍历，以统计抽数
                if not query_params["filter_func"](char_info):  # 如果是新角色或者六星角色
                    continue
                # 年月日
                ymd = char_info[1].split(" ")[0].strip().split("-")
                year, month, day = ymd[0], ymd[1], ymd[2]
                indi_info = {
                    "date": char_info[1],
                    "desc": f"于{year}年{month}月{day}日\n{char_info[4]}/{pool}\n",
                    "name": f"{char_info[0]}",
                    "star": char_info[2],
                    "pool": char_info[4],
                    "record_id": char_info[5],
                }
                # indi_info['date'] = idx#用于排序十连
                if query_params["cost_statis"]:
                    # 统计于最近第几抽获得
                    if idx - last_mark_idx < 0:
                        indi_info["desc"] += f"花费至少 {idx + 1} 抽获得"
                    else:
                        indi_info["desc"] += f"花费 {idx - last_mark_idx} 抽获得"
                    last_mark_idx = idx
                else:
                    # 如果不统计花费的抽数，就统计最近几抽
                    indi_info["desc"] += f"该类池最近第{len(char_info_lst) - idx}抽获得"
                tmp_info["chars"].append(indi_info)
                tmp_info["count"] += 1

        if not tmp_info["chars"]:
            tmp_info["describe"] = f"没有获得{query_params['op_type']}\n"
        else:
            tmp_info["chars"].sort(key=lambda item: item["record_id"], reverse=True)
            tmp_info["chars"] = tmp_info["chars"][: self.max_char_count]
            tmp_info[
                "describe"
            ] = f"获得了{len(tmp_info['chars'])}个{query_params['op_type']}\n"
        return tmp_info

    def shuiwei_query(
        self,
        player_uid: int,
    ):
        """查询卡池水位情况"""
        tmp_info = {"text": "", "title": "卡池水位情况"}
        for pool in self.get_pool_in_view(player_uid):
            self.cursor.execute(
                f"select "
                f"{self.config['char_name_field']}, {self.config['timestamp_field']}, "
                f"{self.config['star_field']}, {self.config['record_id_field']} "
                f"from v{player_uid} where {self.config['exclusive_field']} = ? "
                f"order by {self.config['record_id_field']} desc",
                (pool,),
            )
            char_info_lst = list(self.cursor.fetchall())
            for i, char in enumerate(char_info_lst):
                if char[2] == 6:  # 是六星
                    tmp_info["text"] += f"{pool}：{i + 1}抽\n\n"
                    break
            else:
                tmp_info["text"] += f"{pool}：至少{len(char_info_lst)}抽\n\n"
        return tmp_info

    def fclientuent_query(self, player_uid: int, limit: int = 5):
        """
        预留 查询获得次数最多的干员情况
        """
        self.cursor.execute(
            f"select {self.config['char_name_field']}, count(*) "
            f"from v{player_uid} group by {self.config['char_name_field']} "
            f"order by count(*) desc limit ?",
            (limit,),
        )
        fre_info = self.cursor.fetchall()
        tmp_lst = []
        for fre_char in fre_info:
            desc = f"抽到了{fre_char[1]}次{fre_char[0]}"  # 这边格式要优化
            tmp_lst.append(desc)
        return tmp_lst

    def write_token2db(self, user_session: str, token: str):
        """
        向表中写入用户token
        """
        response = get_player_uid(token)
        try:
            self.cursor.execute(
                f"replace into {self.config['user_table']}"
                f"("
                f"{self.config['user_session_field']}, "
                f"{self.config['player_uid_field']}, "
                f"{self.config['player_name_field']}, "
                f"{self.config['token_field']}, "
                f"{self.config['channel_field']}"
                f")"
                f"values (?, ?, ?, ?, ?);",
                (
                    user_session,
                    response["uid"],
                    response["name"],
                    token,
                    response["channelMasterId"],
                ),
            )
            self.db.commit()
            return
        except Exception as e:
            raise RuntimeError("保存token失败") from e

    def read_token_from_db(self, user_session: str) -> Tuple[str, str, str, int]:
        """
        获取用户的token

        Returns:
            _type_: _description_
        """
        try:
            self.cursor.execute(
                f"select * from {self.config['user_table']} "
                f"where {self.config['user_session_field']} = ?;",
                (user_session,),
            )
            # user_name token user_id channel
            res = self.cursor.fetchone()[1:]
        except Exception as e:
            raise RuntimeError("获取已储存的token失败") from e
        assert res, "请先使用 方舟抽卡帮助 查看帮助或使用 方舟抽卡token + 你的token 进行设置"
        return res

    def url_db_writer(
        self, draw_info_list: list, player_uid: int, private_tot_pool_info: dict
    ):
        """
        将单次爬取到的寻访记录写入数据库
        """
        # logger.info(tot_pool_info)
        draw_pool = None
        try:
            base_sql = (
                f"replace into {self.config['record_table']} "
                f"("
                f"{self.config['record_id_field']}, "
                f"{self.config['timestamp_field']}, "
                f"{self.config['player_uid_field']}, "
                f"{self.config['pool_name_field']}, "
                f"{self.config['char_name_field']}, "
                f"{self.config['star_field']}, "
                f"{self.config['is_new_field']}, "
                f"{self.config['exclusive_field']}"
                f") "
                f"values "
            )
            for draw in draw_info_list:
                base_draw_id = draw["ts"]
                draw_pool = draw["pool"]
                char_info = draw["chars"]
                try:
                    if "联合行动" in draw_pool:
                        exclusive_name = self.config["exclusive_common_name"]
                    else:
                        exclusive_name = (
                            draw_pool
                            if private_tot_pool_info[draw_pool]["is_exclusive"]
                            else self.config["exclusive_common_name"]
                        )
                except Exception as e:
                    raise RuntimeError(f"pool {draw_pool} ") from e
                for i, character in enumerate(char_info):  # 为方便排序，这里是的id反着存的
                    draw_id = f"{base_draw_id}_{i}"
                    time_local = time.localtime(base_draw_id)
                    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                    value_sql = (
                        f"("
                        f"'{draw_id}', "
                        f"'{dt}', "
                        f"'{player_uid}', "
                        f"'{draw_pool}', "
                        f"'{character['name']}', "
                        f"{character['rarity'] + 1}, "
                        f"{character['isNew']}, "
                        f"'{exclusive_name}'),"
                    )
                    base_sql += value_sql
            base_sql = f"{base_sql[:-1]};"
            self.cursor.execute(base_sql)
            self.db.commit()
        except Exception as e:
            if "pool" in str(e):
                raise RuntimeError(
                    f"寻访记录中有未知的卡池 {draw_pool},请使用 方舟卡池更新 命令尝试更新卡池。\n"
                    f"若更新失败，请检查PRTS上是否有此卡池，或卡池名称是否相符。\n"
                    f"若对应卡池名称不符，建议联系管理员进行处理。\n"
                    f"管理员可以修改./resource/pool_info.json中的内容以匹配卡池名称。\n"
                    f"PRTS卡池信息页面：https://prts.wiki/w/卡池一览/限时寻访"
                ) from e

            raise RuntimeError(f"数据库写入失败，错误信息{e}") from e
