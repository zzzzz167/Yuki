import asyncio

from loguru import logger
from utils.config import init_config
from utils.database.db import getGroupList, addGroup
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.mirai import (
    BotInvitedJoinGroupRequestEvent,
    MemberJoinEvent,
    MemberHonorChangeEvent,
    BotJoinGroupEvent,
)
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl

saya = Saya.current()
channel = Channel.current()
config = init_config()
bcc = saya.broadcast
inc = InterruptControl(bcc)


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def accept(app: Ariadne, invite: BotInvitedJoinGroupRequestEvent):
    await app.send_friend_message(
        config.permission.Master,
        MessageChain.create(
            [
                Plain("收到邀请入群事件"),
                Plain(f"\n邀请者: {invite.supplicant} | {invite.nickname}"),
                Plain(f"\n群号: {invite.source_group}"),
                Plain(f"\n群名: {invite.group_name}"),
                Plain("\n\n请发送“同意”或“拒绝”"),
            ]
        ),
    )

    @Waiter.create_using_function([FriendMessage])
    async def waiter(waiter_friend: Friend, waiter_message: MessageChain):
        if waiter_friend.id == config.permission.Master:
            saying = waiter_message.asDisplay()
            if saying == "同意":
                return True
            elif saying == "拒绝":
                return False
            else:
                await app.send_friend_message(
                    config.permission.Master,
                    MessageChain([Plain("请发送同意或拒绝")]),
                )

    try:
        if await asyncio.wait_for(inc.wait(waiter), timeout=60):
            await invite.accept()
            await app.send_friend_message(
                config.permission.Master,
                MessageChain([Plain("已同意申请")]),
            )
        else:
            await invite.reject("主人拒绝加入该群")
            await app.send_friend_message(
                config.permission.Master,
                MessageChain([Plain("已拒绝申请")]),
            )
    except asyncio.TimeoutError:
        if config.permission.DefaultAcceptInvite:
            await invite.accept()
            await app.send_friend_message(
                config.permission.Master,
                MessageChain([Plain("已自动同意申请")]),
            )
        else:
            await invite.reject("由于主人长时间未审核，已自动拒绝")
            await app.send_friend_message(
                config.permission.Master,
                MessageChain([Plain("申请超时已自动拒绝")]),
            )


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def getMemberJoinEvent(events: MemberJoinEvent, app: Ariadne):
    """
    有人加入群聊
    """
    msg = [
        Image(url=f"http://q1.qlogo.cn/g?b=qq&nk={str(events.member.id)}&s=4"),
        Plain("\n欢迎 "),
        At(events.member.id),
        Plain(" 加入本群\n可以使用.help命令查看我的使用帮助哦"),
    ]
    await app.send_group_message(events.member.group, MessageChain(msg))


@channel.use(ListenerSchema(listening_events=[MemberHonorChangeEvent]))
async def get_MemberHonorChangeEvent(events: MemberHonorChangeEvent, app: Ariadne):
    """
    有人群荣誉变动
    """
    msg = [
        At(events.member.id),
        Plain(
            f" {'获得了' if events.action == 'achieve' else '失去了'} \
                群荣誉 {events.honor}!"
        ),
    ]
    await app.send_group_message(events.member.group, MessageChain(msg))


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def init_bot(app: Ariadne):
    gpList = await app.get_group_list()
    dataBaseList = await getGroupList()
    count = 0
    for i in gpList:
        if str(i.id) in dataBaseList:
            pass
        else:
            count += 1
            await addGroup(i.id, i.name)
    logger.info("共 %s 个群未进行初始化,现已完成" % (count))


@channel.use(ListenerSchema(listening_events=[BotJoinGroupEvent]))
async def get_BotJoinGroup(app: Ariadne, joingroup: BotJoinGroupEvent):
    await addGroup(joingroup.group.id, joingroup.group.name)
    logger.info("为群组%s进行初始化" % (joingroup.group.name))
    await app.send_group_message(
        joingroup.group.id, MessageChain([Plain("我是Yuki,很高兴见到大家.\n发送.help可以查看功能列表")])
    )
