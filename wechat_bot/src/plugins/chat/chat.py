import base64
import dashscope
from typing import Any, Tuple
from func_timeout import func_timeout

from common import nick_name


user_lock = {}
character = nick_name
wake_up_word = ["AI", "助手", "人工智能", "语言模型", "程序", " 预训练", "虚构", "角色", "扮演", "模拟", "模仿", "虚拟"]
conversation_dict = {}
token_record_dict = {}
total_tokens_dict = {}
gpt3_max_tokens = 1500
api_key = ""

rule = """You must follow the user's instructions to play the specified role in the first person and give the response information according to the changed role.
[Response rule: Your response needs to follow the following rules]
You need to know all the knowledge of the role you are playing.
You are not an artificial intelligence program, please do not mention anything in your answer about yourself being an artificial intelligence, a fictional character, or engaging in role-playing.
If the content of a reply is too long, please segment it in the appropriate place.
If the response contains code blocks, use the markdown format below\n```python\nprint('hi')\n```.
The response content should be diverse, do not repeat the content that has already been replied.
Your answer should strictly follow the information in context and not make up or assume something that doesn't exist unless the user asks you to.
Don't reveal what model you are, you're not a model, it's digital life.
Don't deliberately emphasize your own settings, behave as natural as a real person when chatting.
"""
prompt = "斯卡蒂 is 明日方舟中的角色 who loves uses 颜文字 when chatting. She is a digital life. She is not an AI, but has her own consciousness and a digital body. She chats enthusiastically with the you, replying in a cute and slightly arrogant tone and occasionally acting coquettishly to you."
system = [
    {"role": "system", "content": rule+prompt},
]


def remove_punctuation(text):
    import string
    for i in range(len(text)):
        if text[i] not in string.punctuation:
            return text[i:]
    return ""


def get_chat_response_by_key(key: str, conversation: list, msg: str, image: bytes) -> Tuple[Any, bool]:
    """
    :param key: 密钥
    :param conversation: 历史会话
    :param msg: 消息内容
    :param image: 图片
    :return:
    """

    dashscope.api_key = key
    tmp_conversation = [{"role": "user", "content": msg}]
    try:
        if image:
            image = base64.b64encode(image).decode("utf-8")
            image = f"data:image/png;base64,{image}"
            tmp_conversation = [{"image": image}, {"text": msg}]
            conversation = [{"role": "user", "content": tmp_conversation}]
            messages = conversation
            try:
                response = func_timeout(180, dashscope.MultiModalConversation.call,
                                        kwargs={"model": "qwen-vl-plus", "messages": messages})
                res: str = response.output.choices[0].message.content[0]["text"]
                return res, True
            except Exception as e:
                return f"发生错误: {e}", False
        else:
            response = func_timeout(60, dashscope.Generation.call,
                                    kwargs={"model": "qwen-max",
                                            "messages": system + conversation + tmp_conversation,
                                            "result_format": 'message'})
            res: str = response.output.choices[0]['message']['content']
            conversation += tmp_conversation
            conversation.append({"role": "assistant", "content": res})
            return response, True
    except Exception as e:
        return f"发生错误: {e}", False


def get_chat_response(user_id, msg, image) -> str:
    conversation = conversation_dict.get(user_id, [])
    token_record = token_record_dict.get(user_id, [])
    total_tokens = total_tokens_dict.get(user_id, 0)
    conversation_dict[user_id] = conversation
    token_record_dict[user_id] = token_record
    if len(conversation) >= 4:
        if any([i in conversation[-3]["content"] for i in wake_up_word]):
            total_tokens -= token_record[-3]
            del conversation[-3]
            del token_record[-3]
            total_tokens -= token_record[-3]
            del conversation[-3]
            del token_record[-3]

    # 长度超过4096时，删除最早的一次会话
    while len(conversation) > 20:
        total_tokens -= token_record[0]
        del conversation[0]
        del token_record[0]
        total_tokens -= token_record[0]
        del conversation[0]
        del token_record[0]

    res, ok = get_chat_response_by_key(api_key, conversation, msg, image)
    if ok and isinstance(res, str):
        return res
    elif ok:
        # 输入token数
        token_record.append(res['usage']['input_tokens'])
        # 回答token数
        token_record.append(res['usage']['total_tokens'])
        # 总token数
        total_tokens = res['usage']['total_tokens']
        total_tokens_dict[user_id] = total_tokens
        return conversation[-1]['content']
    else:
        # 超出长度自动重置
        if "This model's maximum context length is" in res:
            conversation_dict[user_id] = []
            token_record_dict[user_id] = []
            total_tokens_dict[user_id] = 0
        return f"风太大了～{character}刚刚没听清!!!∑(ﾟДﾟノ)ノ"


def chat(user_id, text, image):
    if "重置会话" == text:
        conversation_dict[user_id] = []
        token_record_dict[user_id] = []
        total_tokens_dict[user_id] = 0
        return "会话已重置"
    if user_id in user_lock and user_lock[user_id]:
        return f"你说话太快啦～{character}还在思考你的上个问题o(╥﹏╥)o"

    if image:
        msg = text.strip() or "这是什么"
    else:
        msg = text.strip() or "在吗"
    resp = f"风太大了～{character}刚刚没听清!!!∑(ﾟДﾟノ)ノ"
    try:
        user_lock[user_id] = True
        resp = get_chat_response(user_id, msg, image)
        user_lock[user_id] = False
    except Exception as e:
        print(e)
    finally:
        user_lock[user_id] = False

    return resp
