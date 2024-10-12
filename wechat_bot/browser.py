import jinja2
from os import getcwd
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager
from playwright.async_api import Page, Error, Browser, Playwright, async_playwright


class ConfigError(Exception):
    pass


_browser: Optional[Browser] = None
_playwright: Optional[Playwright] = None


async def init(**kwargs) -> Browser:
    global _browser
    global _playwright
    _playwright = await async_playwright().start()
    try:
        _browser = await launch_browser(**kwargs)
    except Error:
        await install_browser()
        _browser = await launch_browser(**kwargs)
    return _browser


async def launch_browser(proxy=None, **kwargs) -> Browser:
    assert _playwright is not None, "Playwright 没有安装"
    if proxy:
        kwargs["proxy"] = proxy
    # 默认使用 chromium
    print("使用 chromium 启动")
    return await _playwright.chromium.launch(**kwargs)


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()


async def shutdown_browser():
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()  # type: ignore


async def install_browser():
    import os
    import sys

    from playwright.__main__ import main

    print("使用镜像源进行下载")
    os.environ[
        "PLAYWRIGHT_DOWNLOAD_HOST"
    ] = "https://npmmirror.com/mirrors/playwright/"
    success = False

    # 默认使用 chromium
    print("正在安装 chromium")
    sys.argv = ["", "install", "chromium"]
    try:
        print("正在安装依赖")
        os.system("playwright install-deps")
        main()
    except SystemExit as e:
        if e.code == 0:
            success = True
    if not success:
        print("浏览器更新失败, 请检查网络连通性")


async def html_to_pic(
    html: str, wait: int = 0, template_path: str = f"file://{getcwd()}", **kwargs
) -> bytes:
    """html转图片

    Args:
        html (str): html文本
        wait (int, optional): 等待时间. Defaults to 0.
        template_path (str, optional): 模板路径 如 "file:///path/to/template/"

    Returns:
        bytes: 图片, 可直接发送
    """
    # logger.debug(f"html:\n{html}")
    if "file:" not in template_path:
        raise Exception("template_path 应该为 file:///path/to/template")
    async with get_new_page(**kwargs) as page:
        await page.goto(template_path)
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(wait)
        img_raw = await page.screenshot(full_page=True)
    return img_raw


async def template_to_pic(
    template_path: str,
    template_name: str,
    templates: dict,
    pages: dict = {
        "viewport": {"width": 500, "height": 10},
        "base_url": f"file://{getcwd()}",
    },
    wait: int = 0,
) -> bytes:
    """使用jinja2模板引擎通过html生成图片

    Args:
        template_path (str): 模板路径
        template_name (str): 模板名
        templates (dict): 模板内参数 如: {"name": "abc"}
        pages (dict): 网页参数 Defaults to
            {"base_url": f"file://{getcwd()}", "viewport": {"width": 500, "height": 10}}
        wait (int, optional): 网页载入等待时间. Defaults to 0.
    Returns:
        bytes: 图片 可直接发送
    """

    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path),
        enable_async=True,
    )
    template = template_env.get_template(template_name)

    return await html_to_pic(
        template_path=f"file://{template_path}",
        html=await template.render_async(**templates),
        wait=wait,
        **pages,
    )
