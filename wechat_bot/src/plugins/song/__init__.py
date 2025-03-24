import os
import httpx
import asyncio
from pydub import AudioSegment
from pathlib import Path
from pypinyin import lazy_pinyin

from on import on_regex
from common import send_text, send_file, get_url_content


base_path = Path(__file__).parent
music_path = os.path.join(base_path, "music")
dian_ge_url1 = "https://www.hhlqilongzhu.cn/api/dg_qqmusic_SQ.php?n=1&type=json&msg={}"
dian_ge_url2 = "https://www.hhlqilongzhu.cn/api/dg_wyymusic.php?n=1&type=json&gm={}"


def handel_music_file(music_file, content):
    with open(music_file, "wb") as f:
        f.write(content)
    audio = AudioSegment.from_file(music_file)
    audio.export(music_file, format="mp3")


@on_regex(r"^点歌\s*(.*?)\s*$")
async def _(**kwargs):
    match_obj = kwargs.get("match_obj")
    room_id = kwargs.get("room_id")
    sender = kwargs.get("sender")
    sender_name = kwargs.get("sender_name")

    music_name = match_obj.groups()[-1]
    if not music_name:
        await send_text("没有歌名", room_id, sender, sender_name)
        return

    n = 3
    while n:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(dian_ge_url1.format(music_name))
            assert response.status_code == 200
            code = response.json()["code"]
            if code == -1:
                msg = response.json()["msg"]
                await send_text(msg, room_id, sender, sender_name)
                return
            data = response.json()["data"]
            music_url = data["music_url"]
            assert music_url.startswith("http")
            song_name = data["song_name"]
            song_singer = data["song_singer"]
            content = await get_url_content(music_url)
            assert content is not None
            # file_name = sanitize_filename(f"{song_name}-{song_singer}.mp3")
            file_name = " ".join(lazy_pinyin(song_name)) + ".mp3"
            music_file = os.path.join(music_path, file_name)
            await asyncio.get_event_loop().run_in_executor(None, handel_music_file, music_file, content)
            await send_text(f"{song_name}-{song_singer}", room_id)
            await send_file(room_id, music_file)
            return
        except Exception as e:
            print(e)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(dian_ge_url2.format(music_name))
            assert response.status_code == 200
            data = response.json()
            code = data["code"]
            if code == -1:
                msg = data["msg"]
                await send_text(msg, room_id, sender, sender_name)
                return
            music_url = data["music_url"]
            assert music_url.startswith("http")
            title = data["title"]
            singer = data["singer"]
            content = await get_url_content(music_url)
            assert content is not None
            # file_name = sanitize_filename(f"{title}-{singer}.mp3")
            file_name = " ".join(lazy_pinyin(title)) + ".mp3"
            music_file = os.path.join(music_path, file_name)
            await asyncio.get_event_loop().run_in_executor(None, handel_music_file, music_file, content)
            await send_text(f"{title}-{singer}", room_id)
            await send_file(room_id, music_file)
            return
        except Exception as e:
            print(e)
        n -= 1

    await send_text("点歌失败，请稍后再试", room_id, sender, sender_name)
