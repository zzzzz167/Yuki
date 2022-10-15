import aiohttp
import asyncio
from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.exception import UnknownTarget
from utils.hitokoto import getHitokoto
from utils.database import getGroupSetting

saya = Saya.current()
channel = Channel.current()
channel.name('早晚安')
channel.description("早晚安消息, 主动式插件无法被主动调用")
channel.meta["switchKey"] = "goodTime"
channel.meta["icon"] = "moon.svg"


async def getNews():
    async with aiohttp.ClientSession() as session:
        for i in range(0, 5):
            try:
                async with session.get("http://api.2xb.cn/zaob") as res:
                    db = await res.json()
                async with session.get(db["imageUrl"]) as pic:
                    return await pic.read()
            except Exception as err:
                logger.error(f"第{i + 1}次获取日报失败,正在重试" + f"错误原因:{err}")
                await asyncio.sleep(3)


@channel.use(SchedulerSchema(crontabify("10 7 * * *")))
async def goodMorning(app: Ariadne):
    logger.info("开始发送早安消息")
    hito = await getHitokoto()
    dailyNewsData = await getNews()
    count = 0
    for i in await getGroupSetting('goodTime'):
        try:
            await app.send_group_message(
                int(i),
                MessageChain(
                    [Plain(hito + "早安!\n"), Image(data_bytes=dailyNewsData)]
                ),
            )
            count += 1
        except UnknownTarget:
            logger.error(f"群组{i}消息发送失败捏, 可能是群无了呢")
    logger.info("共计发送%s个群聊" % count)


@channel.use(SchedulerSchema(crontabify("0 23 * * *")))
async def goodNight(app: Ariadne):
    logger.info("开始发送晚安消息")
    count = 0
    for i in await getGroupSetting('goodTime'):
        try:
            await app.send_group_message(
                int(i),
                MessageChain(
                    [
                        Plain("睡觉小助手提示您: 11点了子时睡觉养护阳气，百病不起。\n熬夜伤身体，早睡从我做起~\nGood Night!"),
                    ]
                ),
            )
            count += 1
        except UnknownTarget:
            logger.error(f"群组{i}消息发送失败捏, 可能是群无了呢")
    logger.info("共计发送%s个群聊" % count)
