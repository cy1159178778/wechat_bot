import httpx
from playwright.async_api import async_playwright

bash_url = "https://acg.s1f.ren"


async def get_acg_info(mz_id):
    try:
        url = f"{bash_url}/detail/{mz_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            return data.get("data")
    except:
        return {}


async def get_acg_list(city_id=0, key=None, order=None, page=None, count=None, city_name=None):
    url = f"{bash_url}/list"
    params = {
        "city_id": city_id
    }
    if key:
        params["key"] = key
    if order:
        params["order"] = order
    if count:
        params["count"] = count
    if page:
        params["page"] = page
    if city_name:
        params["city_name"] = city_name

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        return data


def get_coordinate_url(coordinate):
    return "https://uri.amap.com/marker?position=" + coordinate


async def capture_element_screenshot(html_content, ele="#app", width=625, device_scale_factor=1):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(device_scale_factor=device_scale_factor)
        await page.set_viewport_size({"width": width, "height": 1200})

        # 设置页面内容
        await page.set_content(html_content)

        # 等待一段时间以确保 HTML 已经渲染完成
        await page.wait_for_timeout(1000)  # 1000 毫秒（1秒）

        element = page.locator(ele)  # 替换为您要截取的元素的CSS选择器

        # 截取屏幕截图
        screenshot = await element.screenshot()

        # 关闭浏览器
        await browser.close()

        return screenshot
