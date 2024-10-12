import re
import httpx

codeType = {
    'py': ['python', 'py'],
    'cpp': ['cpp', 'cpp'],
    'java': ['java', 'java'],
    'php': ['php', 'php'],
    'js': ['javascript', 'js'],
    'c': ['c', 'c'],
    'c#': ['csharp', 'cs'],
    'go': ['go', 'go'],
    'asm': ['assembly', 'asm']
}


async def run(strcode):
    strcode = strcode.replace('&amp;', '&').replace('&#91;', '[').replace('&#93;', ']')
    try:
        a = re.findall(r'(py|php|java|cpp|js|c#|c|go|asm)\s?(-i)?\s?(\w*)?(\n|\r)((?:.|\n)+)', strcode)[0]
    except:
        return False, "输入有误，目前仅支持c/cpp/c#/py/php/go/java/js\n示例：\ncode py\nprint(1)"
    if "-i" in strcode:
        lang, code = a[0], a[4]
        dataJson = {
            "files": [
                {
                    "name": f"main.{codeType[lang][1]}",
                    "content": code
                }
            ],
            "stdin": a[2],
            "command": ""
        }
    else:
        lang, code = a[0], a[4]
        dataJson = {
            "files": [
                {
                    "name": f"main.{codeType[lang][1]}",
                    "content": code
                }
            ],
            "stdin": "",
            "command": ""
        }
    headers = {
        "Authorization": "Token 0123456-789a-bcde-f012-3456789abcde",
        "content-type": "application/"
    }
    async with httpx.AsyncClient() as client:
        try:
            res = (await client.post(url=f'https://glot.io/run/{codeType[lang][0]}?version=latest', headers=headers, json=dataJson))
        except:
            return False, "呜呜呜~发生了未知的错误~~~"

    if res.status_code == 200:
        if res.json()['stdout'] != "":
            if len(repr(res.json()['stdout'])) < 200:
                return True, res.json()['stdout']
            else:
                return False, "返回字符过长呐~~~"
        else:
            return True, res.json()['stderr'].strip()
