import asyncio
import json
import re
import urllib
from pathlib import Path
from typing import Optional, Tuple

import httpx
from httpx._types import ProxiesTypes

from ..update.record import generate
from .database import ArkDatabase
from .drawer import ArkImage
from .style import get_img_wh


async def url_scrawler(token: str, channel: int, proxy: Optional[ProxiesTypes] = None) -> Tuple[str, list]:
    """_summary_
    爬取官网抽卡记录
    Args:
        token (str): token
        channel: 用户官服/B服判据。官服为1，B服为2
        proxy: 代理
    Returns:
        _type_: _description_
    """
    token = urllib.parse.quote(token)  # type: ignore
    base_url = f"https://ak.hypergryph.com/user/api/inquiry/gacha?token={token}"
    draw_info_list = []
    user_agent = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) "
        "AppleWebKit/601.1.46 (KHTML, like Gecko) "
        "Version/9.0 Mobile/13B143 Safari/601.1 wechatdevtools/0.7.0 "
        "MicroMessenger/6.3.9 "
        "Language/zh_CN webview/0"
    )
    headers = {"User-Agent": user_agent}
    async with httpx.AsyncClient(proxies=proxy) as client:
        try:
            for i in range(1, 11):
                _data = await client.get(
                    f"{base_url}&channelId={channel}&page={i}", headers=headers
                )
                res_data = _data.json()
                if page_data := res_data["data"]["list"]:
                    draw_info_list.extend(page_data)
                else:
                    break
            warning_info = "" if draw_info_list else "未获取到有效寻访信息。正在返回缓存信息"
            return warning_info, draw_info_list
        except Exception as e:
            warning_info = "" if draw_info_list else "未成功访问寻访页面，token可能已经失效。正在返回缓存信息"
            return warning_info, []


class ArkRecord:
    def __init__(
        self,
        save_dir: str,
        pool_path: Optional[str] = None,
        db_path: Optional[str] = None,
        max_char_count: int = 20,
        max_pool_count: int = 8,
        proxy: Optional[ProxiesTypes] = None,
    ):
        """
        明日方舟抽卡数据分析
        :param save_dir: 分析结果图像的保存目录
        :param pool_path: 卡池数据文件目录，默认为本项目的 resource/record/pool_info.json
        :param db_path: 数据文件目录，默认为用户路径
        :param max_char_count: 最多展示的干员
        :param max_pool_count: 最多展示的卡池
        :param proxy: 代理
        """
        self.proxy = proxy
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        if not self.save_dir.is_dir():
            raise NotADirectoryError(save_dir)
        if pool_path is None:
            self.pool_path = Path(__file__).parent.parent.joinpath(
                "resource", "record", "pool_info.json"
            )
        else:
            self.pool_path = Path(pool_path)
            if not self.pool_path.exists():
                if not asyncio.events._get_running_loop():  # type: ignore
                    asyncio.run(generate(self.pool_path, self.proxy))
                else:
                    asyncio.create_task(
                        generate(self.pool_path, self.proxy), name="generate_pool_info"
                    )
        self.database = ArkDatabase(db_path, max_char_count, max_pool_count)

    def user_token_save(self, player_token: str, user_session: str):
        """
        token保存


        **token获取方法**：在官网登录后，根据你的服务器，选择复制以下网址中的内容

        官服：https://web-api.hypergryph.com/account/info/hg

        B服：https://web-api.hypergryph.com/account/info/ak-b

        ***请在浏览器中获取token，避免在QQ打开的网页中获取，否则可能获取无效token***

        **token设置方法**：使用插件命令`方舟抽卡token 你的token`(自动识别B服、官服token)
        或`方舟寻访token 你的to.ken`进行设置

        如网页中内容为
        ```json
        {"status":0,"msg":"OK","data":{"token":"example123456789"}}
        ```
        则参数为 example123456789， 如果间隔超**3天**再次使用，建议重新使用上述方式设置token

        """
        if "content" in player_token:
            player_token = re.findall(r"content\":\".*\"", player_token)[0][10:][:-11]
        self.database.write_token2db(user_session, player_token)
        return "成功保存token"

    async def user_analysis(
        self,
        user_session: str,
        count: int = -1,
        pool_name: str = "all",
    ):
        """
        抽卡分析，并保存为图片

        输出时，如果没有可用干员头像，将以海猫头像代替
        """
        player_info = self.database.read_token_from_db(user_session)
        player_name, player_uid, token, channel = player_info
        # 获取官网寻访记录
        warning_info, record_info_list = await url_scrawler(token, channel, self.proxy)
        with self.pool_path.open("r", encoding="utf-8") as f:
            private_tot_pool_info = json.load(f)

        if record_info_list:
            self.database.url_db_writer(
                record_info_list, int(player_uid), private_tot_pool_info
            )
        # 读数据库
        self.database.check_view(int(player_uid))
        _real_count = self.database.create_view(pool_name, int(player_uid), count)
        query_info = self.database.query_all_items(
            pool_name, int(player_uid), _real_count
        )
        # 生成图片
        aig = ArkImage(query_info, player_uid, get_img_wh(query_info), self.save_dir)
        aig.draw_all(player_name, _real_count)
        return warning_info, aig.save()
