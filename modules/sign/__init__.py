import random
from loguru import logger
from utils.control import cheakBan, groupConfigRequire
from utils.database import User
from utils.database import addUser, getAllUser, getUser, updataUser, reset_sign
from utils.hitokoto import getAppointHitokoto
from utils.picture import getMaskBg
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from arclet.alconna import Alconna
from arclet.alconna.graia.dispatcher import AlconnaDispatcher


saya = Saya.current()
channel = Channel.current()
channel.name('签到')
signAlc = Alconna(".sign", help_text="每日签到")


async def sign(app: Ariadne, group: Group, member: Member):
    qdUser = await getUser(member.id)
    if qdUser.today:
        await app.send_group_message(
            group, MessageChain([Plain("今天你已经签到过啦,不要做贪心鬼哦,明天再来吧")])
        )
    else:
        await updataUser(
            member.id,
            {
                User.favor: qdUser.favor + random.randint(0, 5),
                User.days: qdUser.days + 1,
                User.today: True,
            },
        )
        newdata = await getUser(member.id)
        await app.send_group_message(
            group,
            MessageChain(
                [
                    Image(
                        data_bytes=await getMaskBg(
                            member.id,
                            member.name,
                            int(newdata.days),
                            int(newdata.favor),
                            await getAppointHitokoto(max_length="10"),
                        )
                    )
                ]
            ),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(signAlc, send_flag='reply')],
        decorators=[cheakBan(), groupConfigRequire('sign')]
    )
)
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
