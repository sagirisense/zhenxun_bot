from io import BytesIO
from typing import List

import imagehash
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.typing import T_State
from PIL import Image

from services.log import logger
from utils.depends import ImageList
from utils.http_utils import AsyncHttpx
from utils.utils import get_message_at, get_message_img, get_message_text

from ._model import WordBank


async def check(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
) -> bool:
    text = get_message_text(event.message)
    img_list = get_message_img(event.message)
    problem = text
    if not text and len(img_list) == 1:
        try:
            r = await AsyncHttpx.get(img_list[0])
            problem = str(imagehash.average_hash(Image.open(BytesIO(r.content))))
        except Exception as e:
            logger.warning(f"获取图片失败", "词条检测", e=e)
    if get_message_at(event.message):
        temp = ""
        for seg in event.message:
            if seg.type == "at":
                temp += f"[at:{seg.data['qq']}]"
            elif seg.type == "text":
                temp += seg.data["text"]
        problem = temp
    if event.to_me and bot.config.nickname:
        if str(event.original_message).startswith("[CQ:at"):
            problem = f"[at:{bot.self_id}]" + problem
        else:
            if problem and bot.config.nickname:
                nickname = [
                    nk
                    for nk in bot.config.nickname
                    if str(event.original_message).startswith(nk)
                ]
                problem = nickname[0] + problem if nickname else problem
    if problem and (await WordBank.check_problem(event, problem) is not None):
        state["problem"] = problem
        return True
    return False
