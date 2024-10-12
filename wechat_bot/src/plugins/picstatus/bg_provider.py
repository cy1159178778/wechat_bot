import os
import glob
import random
from pathlib import Path
from typing import Awaitable, Callable, Dict, List, TypeVar

import anyio

from .config import DEFAULT_BG_PATH, config

BGProviderType = Callable[[], Awaitable[bytes]]
TBP = TypeVar("TBP", bound=BGProviderType)

registered_bg_providers: Dict[str, BGProviderType] = {}
file_path = os.path.abspath(os.path.join("data", "file", "status", "*"))


def get_bg_files() -> List[Path]:
    if not config.ps_bg_local_path.exists():
        return [DEFAULT_BG_PATH]
    if config.ps_bg_local_path.is_file():
        return [config.ps_bg_local_path]

    files = [x for x in config.ps_bg_local_path.glob("*") if x.is_file()]
    if not files:
        return [DEFAULT_BG_PATH]
    return files


BG_FILES = get_bg_files()


def bg_provider(func: TBP) -> TBP:
    name = func.__name__
    if name in registered_bg_providers:
        raise ValueError(f"Duplicate bg provider name `{name}`")
    registered_bg_providers[name] = func
    return func


@bg_provider
async def local():
    file_list = glob.glob(file_path)
    if not file_list:
        return DEFAULT_BG_PATH
    file = random.choice(file_list)
    print("状态图片", file)
    return await anyio.Path(file).read_bytes()


@bg_provider
async def none():
    return b""


async def get_bg():
    return await local()
