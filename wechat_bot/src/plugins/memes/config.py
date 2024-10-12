from datetime import timedelta
from typing import Literal, Optional

from pydantic import BaseModel


class MemeListImageConfig(BaseModel):
    sort_by: Literal["key", "keywords", "date_created", "date_modified"] = "keywords"
    sort_reverse: bool = False
    text_template: str = "{keywords}"
    add_category_icon: bool = True
    label_new_timedelta: timedelta = timedelta(days=30)
    label_hot_threshold: int = 21
    label_hot_days: int = 7


class Config(BaseModel):
    memes_command_prefixes: Optional[list[str]] = None
    memes_disabled_list: list[str] = []
    memes_check_resources_on_startup: bool = True
    memes_prompt_params_error: bool = False
    memes_use_sender_when_no_image: bool = True
    memes_use_default_when_no_text: bool = False
    memes_random_meme_show_info: bool = True
    memes_list_image_config: MemeListImageConfig = MemeListImageConfig()


memes_config = get_plugin_config(Config)

