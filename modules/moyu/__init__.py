from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from .getHolidays import getMoyuMsg
from utils.database import getGroupSetting


saya = Saya.current()
channel = Channel.current()
channel.name('摸鱼提醒')


@channel.use(SchedulerSchema(crontabify("45 9 * * *")))
async def goodMorning(app: Ariadne):
    logger.info("开始发送摸鱼消息")
    count = 0
    msg = await getMoyuMsg()
    for i in await getGroupSetting('moyu'):
        count += 1
        await app.send_group_message(int(i), MessageChain([Plain(msg)]))
    logger.info("共计发送%s个群聊" % count)
