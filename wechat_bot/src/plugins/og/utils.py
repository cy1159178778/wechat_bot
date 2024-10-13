import re
from typing import Any, Dict, Optional
import datetime
import aiohttp

from common import get_url_content
from browser import get_browser
from playwright._impl._errors import TimeoutError


group_url_dict = {}


async def get_og_info(msg: str, group_id: str) -> Optional[Dict[str, Any]]:
    url = re.search(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
    if not url:
        return

    url = url.group()

    if not url.startswith("https://github.com/"):
        return
    # if url.startswith("https://www.bilibili.com/"):
    #     return
    # if url.startswith("https://b23.tv/"):
    #     return

    if group_id not in group_url_dict:
        group_url_dict[group_id] = {}
    url_dict = group_url_dict[group_id]
    t1 = url_dict.get(url)
    t2 = datetime.datetime.now()
    if t1 and t2 - t1 < datetime.timedelta(minutes=5):
        return
    url_dict[url] = t2

    if url.startswith("https://github.com/"):
        img = await get_github_reposity_information(url)
        if img == "获取信息失败":
            img = None
        else:
            img = await get_url_content(img)
    else:
        browser = await get_browser()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until='networkidle')
        except TimeoutError:
            await page.close()
            return

        img = None
        try:
            await page.mouse.wheel(0, 100)
            element = await page.query_selector('.qConnectClose')
            if element:
                await element.click()
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)
            img = await page.screenshot(type="jpeg", full_page=True)
        except:
            pass
        finally:
            await page.close()

    if img is None:
        return

    return {"img": img, "url": url}


token = None
github_type = 0

Headers1 = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}
Headers2 = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}

if token is None:
    headers = Headers1
else:
    headers = Headers2


async def get_github_reposity_information(url: str) -> str:
    try:
        UserName, RepoName = url.replace("https://github.com/", "").split("/")[:2]
    except:
        UserName, RepoName = url.replace("github.com/", "").split("/")[:2]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/users/{UserName}", headers=headers, timeout=5) as response:
            RawData = await response.json()
            AvatarUrl = RawData["avatar_url"]
            if github_type == 0:
                ImageUrl = f"https://socialify.git.ci/{UserName}/{RepoName}/png?description=1&font=Rokkitt&forks=1&issues=1&language=1&name=1&owner=1&pattern=Circuit%20Board&pulls=1&stargazers=1&theme=Light&logo={AvatarUrl}"
            else:
                ImageUrl = f"https://opengraph.githubassets.com/githubcard/{UserName}/{RepoName}"
            return ImageUrl
