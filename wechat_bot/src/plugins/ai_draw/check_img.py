import io
import requests
import numpy as np
from PIL import Image

API_KEY = ""
SECRET_KEY = ""


def check_img(image):
    """
    :return:
    {"conclusion":"合规","log_id":17050803270883834,"isHitMd5":false,"conclusionType":1}
    {"conclusion":"不合规","log_id":17050806550894975,"data":[{"msg":"存在一般色情不合规","conclusion":"不合规","probability":0.99079996,"subType":0,"conclusionType":2,"type":1}],"isHitMd5":false,"conclusionType":2}
    """
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + get_access_token()
    payload = {"image": image}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["conclusionType"]


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


def add_mosaic(bytes_img):
    # 打开原始图像并转换为RGB模式
    image = Image.open(io.BytesIO(bytes_img)).convert("RGB")

    # 获取图像的大小
    width, height = image.size

    # 定义每个马赛克单元格的边长
    cell_width = 64
    cell_height = 64

    # 创建新的空白图像作为输出结果
    mosaic_image = Image.new('RGB', (width, height))

    for y in range(0, height + cell_height, cell_height):
        for x in range(0, width + cell_width, cell_width):
            # 提取当前区域内的颜色平均值
            average_color = tuple([int((np.mean(pixel))) for pixel in zip(*image.crop(
                (x - cell_width // 2, y - cell_height // 2, x + cell_width // 2, y + cell_height // 2)).getdata())])

            # 将该区域内所有像素都设置为平均颜色
            mosaic_image.paste(average_color,
                               (x - cell_width // 2, y - cell_height // 2, x + cell_width // 2, y + cell_height // 2))

    buffer = io.BytesIO()
    mosaic_image.save(buffer, format='JPEG')
    byte_stream = buffer.getvalue()
    return byte_stream
