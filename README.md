<div align="center">

# wechat_bot

一个娱乐功能为主的微信机器人，基于WeChatFerry和NoneBot2开发，插件式写法，方便插拔

</div>

## 功能
![help](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/help/help.png)

## 安装
* 本项目使用 Python 3.10 开发，所以建议使用 3.10 (其他版本应该也问题不大)
* 配套 [微信](https://github.com/lich0821/WeChatFerry/releases/download/v39.2.4/WeChatSetup-3.9.10.27.exe) 版本：3.9.10.27
* 可以根据 [requirements.txt](https://github.com/cy1159178778/wechat_bot/blob/main/requirements.txt) 搭建环境，或者使用 [整合包](https://pan.quark.cn/s/d4f916df1472)(夸克网盘提取码：6xmJ) / [整合包](https://pan.baidu.com/s/1r-E22_42F9kysXLvTkZ4FA?pwd=rfhh)(百度网盘提取码：rfhh) (不熟悉python的建议使用)

## 配置
* [common.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/common.py) 中配置 admin(管理员微信id) 和 nick_name(机器人昵称)
* 对话功能，使用阿里云通义千问，[apikey获取](https://bailian.console.aliyun.com/?apiKey=1#/api-key)，配置在 [chat/chat.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/chat/chat.py) 中的 api_key
* 翻译功能，使用阿里云机器翻译，[accesskey获取](https://ram.console.aliyun.com/profile/access-keys)，配置在 [translate/aliyun_translate.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/translate/aliyun_translate.py) 中的 access_key_id 和 access_key_secret
* 绘图功能，使用flux，[falkey获取](https://fal.ai/models/fal-ai/flux/schnell/api)，配置在 [ai_draw/__ init__.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/ai_draw/__init__.py) 中的 os.environ["FAL_KEY"]，以前注册有免费额度的，现在好像没了，也可自行更换，绘图还搭配了[百度云图片审核](https://ai.baidu.com/censoring#/strategylist)，配置在 [ai_draw/check_img.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/ai_draw/check_img.py) 中的 API_KEY 和 SECRET_KEY 
* 天气功能，使用和风天气，[apikey获取](https://dev.qweather.com/)，配置在 [heweather/heweather.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/heweather/heweather.py) 中的 api_key
* 图片功能、视频功能、签到、运行状态、kfc、舔狗日记、随机小说，目前是用的本地文件(嫌api不稳定)，需下载 [file](https://pan.quark.cn/s/11f1dd388aee)，提取码：YwGB，各个压缩包解压到当前文件夹，然后放到 [file](https://github.com/cy1159178778/wechat_bot/tree/main/wechat_bot/data/file) 下，也可自行更换api
* 定时发送每日新闻和摸鱼日报，[requests_api/__ init__.py](https://github.com/cy1159178778/wechat_bot/blob/main/wechat_bot/src/plugins/requests_api/__init__.py) 中的 task_group 配置微信群id

## 使用
* [start_wx.bat](https://github.com/cy1159178778/wechat_bot/blob/main/start_wx.bat) 启动微信端
* [start_bot.bat](https://github.com/cy1159178778/wechat_bot/blob/main/start_bot.bat) 启动机器人
* 在群内发送“开启功能“即可开启所有功能

## 特别感谢
* [WeChatFerry](https://github.com/lich0821/WeChatFerry/)
* [NoneBot2](https://github.com/nonebot/nonebot2/)
