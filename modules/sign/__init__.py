import random

from loguru import logger
from utils.database.db import User
from utils.database.db import (addUser, getAllUser, getUser, updataUser,
                               reset_sign)
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema

saya = Saya.current()
channel = Channel.current()


async def sign(app: Ariadne, group: Group, member: Member):
    qdUser = await getUser(member.id)
    if qdUser.today:
        await app.sendGroupMessage(
            group, MessageChain.create([Plain("今天你已经签到过啦,不要做贪心鬼哦,明天再来吧")]))
    else:
        await updataUser(
            member.id, {
                User.favor: qdUser.favor + random.randint(0, 5),
                User.days: qdUser.days + 1,
                User.today: True
            })
        newdata = await getUser(member.id)
        await app.sendGroupMessage(
            group,
            MessageChain.create([
                At(member.id),
                Plain("签到成功 好感度:%s 签到天数:%s" % (newdata.favor, newdata.days))
            ]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"head": UnionMatch(".签到", ".sign")})],
    ))
async def signIn(app: Ariadne, group: Group, member: Member):
    if str(member.id) not in await getAllUser():
        await addUser(member.id, member.name)
        await sign(app, group, member)
    else:
        await sign(app, group, member)


@channel.use(SchedulerSchema(crontabify("30 4 * * *")))
async def rest():
    await reset_sign()
    logger.info("签到重置成功")
