import asyncio

from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_tea_util import models as util_models


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> alimt20181012Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id="",
            access_key_secret=""
        )
        config.endpoint = f'mt.cn-hangzhou.aliyuncs.com'
        return alimt20181012Client(config)

    @staticmethod
    def translate_to_en(text):
        client = Sample.create_client()
        translate_general_request = alimt_20181012_models.TranslateGeneralRequest(
            source_language='auto',
            target_language='en',
            source_text=text,
            format_type="text"
        )
        runtime = util_models.RuntimeOptions()
        try:
            res = client.translate_general_with_options(translate_general_request, runtime)
            return str(res.body.data.translated)
        except Exception as error:
            print(error)

    @staticmethod
    def translate_to_any(text, to):
        client = Sample.create_client()
        translate_general_request = alimt_20181012_models.TranslateGeneralRequest(
            source_language='auto',
            target_language=to,
            source_text=text,
            format_type="text"
        )
        runtime = util_models.RuntimeOptions()
        try:
            res = client.translate_general_with_options(translate_general_request, runtime)
            return str(res.body.data.translated)
        except Exception as error:
            print(error)


async def async_trans(text, to):
    target = None
    try:
        target = await asyncio.get_event_loop().run_in_executor(None, Sample.translate_to_any, text, to)
    except Exception as e:
        print(e)

    return target

if __name__ == '__main__':
    print(Sample.translate_to_any("我其實鐘意你好耐咗", "yue"))
