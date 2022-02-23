from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from utils.hitokoto import getHitokoto
from utils.database.db import getGroupSetting, GroupList

saya = Saya.current()
channel = Channel.current()


@channel.use(SchedulerSchema(crontabify("10 8 * * *")))
async def goodMorning(app: Ariadne):
    logger.info("开始发送早安消息")
    hito = await getHitokoto()
    count = 0
    for i in await getGroupSetting(GroupList.GoodMorning):
        count += 1
        await app.sendGroupMessage(
            int(i),
            MessageChain.create([
                Plain(hito + "早安!\n"),
                Image(url="https://api.vvhan.com/api/moyu")
            ]))
    logger.info("共计发送%s个群聊" % count)


@channel.use(SchedulerSchema(crontabify("0 23 * * *")))
async def goodNight(app: Ariadne):
    logger.info("开始发送晚安消息")
    count = 0
    for i in await getGroupSetting(GroupList.GoodMorning):
        count += 1
        await app.sendGroupMessage(
            int(i),
            MessageChain.create([
                Plain(
                    "睡觉小助手提示您: 11点了子时睡觉养护阳气，百病不起。\n熬夜伤身体，早睡从我做起~\nGood Night!"
                ),
            ]))
    logger.info("共计发送%s个群聊" % count)
