from typing import Optional, AsyncIterator
from playwright.sync_api import Page, Error, Browser, Playwright, sync_playwright


class ConfigError(Exception):
    pass


_browser: Optional[Browser] = None
_playwright: Optional[Playwright] = None


def init(**kwargs) -> Browser:
    global _browser
    global _playwright
    _playwright = sync_playwright().start()
    try:
        _browser = launch_browser(**kwargs)
    except Error:
        install_browser()
        _browser = launch_browser(**kwargs)
    return _browser


def launch_browser(proxy=None, **kwargs) -> Browser:
    assert _playwright is not None, "Playwright 没有安装"
    if proxy:
        kwargs["proxy"] = proxy
    # 默认使用 chromium
    return _playwright.chromium.launch(**kwargs)


def get_browser(**kwargs) -> Browser:
    return _browser or init(**kwargs)


def get_new_page(**kwargs):
    browser = get_browser()
    page = browser.new_page(**kwargs)
    return page


def shutdown_browser():
    if _browser:
        _browser.close()
    if _playwright:
        _playwright.stop()  # type: ignore


def install_browser():
    import os
    import sys

    from playwright.__main__ import main

    os.environ[
        "PLAYWRIGHT_DOWNLOAD_HOST"
    ] = "https://npmmirror.com/mirrors/playwright/"
    success = False

    # 默认使用 chromium
    sys.argv = ["", "install", "chromium"]
    try:
        os.system("playwright install-deps")
        main()
    except SystemExit as e:
        if e.code == 0:
            success = True
    if not success:
        print("浏览器更新失败, 请检查网络连通性")
