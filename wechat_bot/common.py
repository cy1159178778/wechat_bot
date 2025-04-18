import os
import re
import httpx
import base64
import asyncio
import schedule
from pathlib import Path
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from contextlib import asynccontextmanager
from wcferry.roomdata_pb2 import RoomData

from db import Db


@asynccontextmanager
async def lifespan(_):
    asyncio.create_task(schedule_task())
    yield


class Admin:
    def __init__(self, users):
        self.users = users or []

    def __eq__(self, other):
        return other in self.users

    def __ne__(self, other):
        return other not in self.users


app = FastAPI(lifespan=lifespan)
var = {"bot_connect_time": datetime.now().astimezone(), "msg_rec": 0, "msg_sent": 0}
admin = Admin(["wxid_xxx"])
nick_name = "斯卡蒂"
open_groups_obj = Db("open_groups")
base_url = "http://127.0.0.1:9999/"
at_user_compile = re.compile(r"<atuserlist>.*?<!\[CDATA\[(.+?)]]>.*?</atuserlist>")
wechat_save_path = r"替换成自己的微信文件保存位置\Documents\WeChat Files"
save_image_path = os.path.join(Path(__file__).parent, "data", "save_image")


class Msg(BaseModel):
    is_self: bool
    is_group: bool
    id: int
    type: int
    ts: int
    roomid: str
    content: str
    sender: str
    sign: str
    thumb: str
    extra: str
    xml: str
    

async def schedule_task():
    while 1:
        try:
            schedule.run_pending()
            await asyncio.sleep(1)
        except Exception as e:
            print(e)


async def get_alias_in_chatroom(room_id, wx_id):
    params = {
        "roomid": room_id,
        "wxid": wx_id
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url + "alias-in-chatroom", params=params)
        return response.json()["data"]["alias"]
    except Exception as e:
        print("get_alias_in_chatroom error:", e)


async def get_chatroom_member(room_id):
    params = {
        "roomid": room_id
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url + "chatroom-member", params=params)
        return response.json()["data"]["members"]
    except Exception as e:
        print("get_chatroom_member error:", e)


async def query_sql(db, sql):
    data = {
        "db": db,
        "sql": sql
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url + "sql", json=data)
        return response.json()["data"]["bs64"]
    except Exception as e:
        print("query_sql error:", e)


async def get_head_img_by_wx_id(wx_id):
    db = "MicroMsg.db"
    sql = f"SELECT usrName, bigHeadImgUrl FROM ContactHeadImgUrl where usrName = '{wx_id}'"
    results = await query_sql(db, sql)
    if not results:
        return ""
    return results[0].get("bigHeadImgUrl")


async def get_meme_user_info(room_id, wx_id_list):
    user_info = {wx_id: {} for wx_id in wx_id_list}
    db = "MicroMsg.db"
    user_names = "(" + ",".join(f"'{wx_id}'" for wx_id in wx_id_list) + ")"

    sql = f"SELECT UserName, NickName FROM Contact WHERE UserName in {user_names};"
    results = await query_sql(db, sql)
    if not results:
        return user_info
    for result in results:
        user_info[result["UserName"]]["nick_name"] = result["NickName"]

    sql = f"SELECT RoomData FROM ChatRoom WHERE ChatRoomName = '{room_id}';"
    results = await query_sql(db, sql)
    if not results:
        return user_info
    bs = results[0].get("RoomData")
    if not bs:
        return user_info
    crd = RoomData()
    crd.ParseFromString(base64.b64decode(bs))
    for member in crd.members:
        if member.wxid in wx_id_list:
            user_info[member.wxid]["name"] = member.name or user_info[member.wxid]["nick_name"]

    sql = f"SELECT usrName, bigHeadImgUrl FROM ContactHeadImgUrl where usrName in {user_names};"
    results = await query_sql(db, sql)
    if not results:
        return user_info
    for result in results:
        user_info[result["usrName"]]["head_img"] = result["bigHeadImgUrl"]

    return user_info


async def send_text(msg, receiver, aters="", name=None):
    var["msg_sent"] += 1
    if aters == "notify@all":
        msg = "@所有人\u2005" + msg
    elif aters and receiver == aters:
        msg = f"@{name}\u2005" + msg
    elif aters:
        name = await get_alias_in_chatroom(receiver, aters)
        msg = f"@{name}\u2005" + msg
    data = {
        "msg": msg,
        "receiver": receiver,
        "aters": aters
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url + "text", json=data)
            return response
    except Exception as e:
        print("send_text error:", e)


async def send_image(receiver, path):
    var["msg_sent"] += 1
    data = {
        "path": path,
        "receiver": receiver
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url + "image", json=data)
            return response
    except Exception as e:
        print("send_image error:", e)


async def send_emotion(receiver, path):
    var["msg_sent"] += 1
    data = {
        "path": path,
        "receiver": receiver
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url + "emotion", json=data)
            return response
    except Exception as e:
        print("send_emotion error:", e)


async def send_file(receiver, path):
    data = {
        "path": path,
        "receiver": receiver
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url + "file", json=data)
            return response
    except Exception as e:
        print("send_file error:", e)


async def send_xml(receiver, xml, xml_type, path):
    var["msg_sent"] += 1
    data = {
        "receiver": receiver,
        "xml": xml,
        "type": xml_type,
        "path": path
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url + "xml", json=data)
            return response
    except Exception as e:
        print("send_file error:", e)


async def save_image(msg_id, extra, save_dir=save_image_path, timeout=30):
    if not os.path.exists(save_image_path):
        os.makedirs(save_image_path, exist_ok=True)

    data = {
        "id": msg_id,
        "extra": extra,
        "dir": save_dir,
        "timeout": timeout
    }

    try:
        response = httpx.post(base_url + "save-image", json=data)
        return response.json()["data"]["path"]
    except Exception as e:
        print("save_image error:", e)


async def get_data_by_svrid(svrid):
    db = "MSG0.db"
    sql = f"SELECT * FROM MSG where MsgSvrID = {svrid}"
    results = await query_sql(db, sql)
    if not results:
        return

    return results[0]


async def get_image_by_svrid(svrid):
    data = await get_data_by_svrid(svrid)
    if not data:
        return

    if data["Type"] == 47:
        str_content = data["StrContent"]
        cdnurl_list = re.findall(f"cdnurl = \"(.*?)\"", str_content)
        if cdnurl_list:
            return await get_url_content(cdnurl_list[0].replace("&amp;", "&"))
        return

    if data["Type"] != 3:
        return

    bytes_extra = base64.b64decode(data["BytesExtra"])
    str_extra = bytes_extra.decode("utf-8", errors="ignore")
    img_list = re.findall(r"\w+\\.*?\.dat", str_extra)
    if not img_list:
        return

    path = await save_image(int(svrid), os.path.join(wechat_save_path, img_list[0]))
    if not path or not os.path.exists(path):
        return

    with open(path, "rb") as f:
        return f.read()


def get_at_list(xml: str):
    res = at_user_compile.search(xml.replace("\n", ""))
    if res:
        return [*filter(str, res.group(1).split(","))]
    return []


async def get_url_json(url):
    n = 3
    while n:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                assert response.status_code == 200
                return response.json()
        except Exception as e:
            print("get_url_json error:", e)
        n -= 1


async def get_url_text(url):
    n = 3
    while n:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                assert response.status_code == 200
                return response.text.strip()
        except Exception as e:
            print(e)
        n -= 1


async def get_url_content(url, key=""):
    n = 3
    while n:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if key:
                    response = await client.get(response.json()[key])
                assert response.status_code == 200
                return response.content
        except Exception as e:
            print(e)
        n -= 1


def run_async_task(func):
    return lambda: asyncio.create_task(func())
