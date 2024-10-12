import os
os.chdir(os.path.dirname(__file__))

import time
import asyncio
import uvicorn
import schedule
import threading
from fastapi import Body

from common import app, Msg
from manager import handle


@app.post("/callback")
async def msg_cb(msg: Msg = Body(description="微信消息")):
    print(f"收到消息：{msg}")
    # await handle(msg)
    asyncio.create_task(handle(msg))
    return {"status": 0, "message": "成功"}


def schedule_task():
    while 1:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    threading.Thread(target=schedule_task, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
