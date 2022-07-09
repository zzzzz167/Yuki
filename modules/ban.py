import asyncio
import time
from utils.config import init_config
from loguru import logger
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexResult,
    FullMatch,
    ParamMatch,
    WildcardMatch,
    SpacePolicy
)
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Saya, Channel
from graia.scheduler.saya.schema import SchedulerSchema
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler.timers import crontabify
from utils.database.db import cheakBanList, delBanList, resetBanList, addBanList

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)
config = init_config()


@channel.use(SchedulerSchema(crontabify("30 12 * * *")))
async def rest():
    await resetBanList()
    logger.info("黑名单重置成功")


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight.from_command("unban {id}")],
    )
)
async def unBan(app: Ariadne, friend: Friend, id: RegexResult):
    if friend.id == config.permission.Master:
        if await cheakBanList(int(str(id.result))):
            await app.send_friend_message(
                friend,
                MessageChain(
                    Plain(f"确认要解封QQ:{str(id.result)}?(确认/取消)"),
                ),
            )

            @Waiter.create_using_function([FriendMessage])
            async def waiter(waiter_friend: Friend, waiter_message: MessageChain):
                if waiter_friend.id == config.permission.Master:
                    saying = waiter_message.display
                    if saying == "确认":
                        return True
                    elif saying == "取消":
                        return False
                    else:
                        await app.send_friend_message(
                            config.permission.Master,
                            MessageChain([Plain("请发送确认或取消")]),
                        )

            try:
                if await asyncio.wait_for(inc.wait(waiter), timeout=20):
                    await delBanList(int(str(id.result)))
                    await app.send_friend_message(
                        config.permission.Master,
                        MessageChain([Plain(f"成功解封{str(id.result)}")]),
                    )
                else:
                    await app.send_friend_message(
                        config.permission.Master, MessageChain(Plain("已取消"))
                    )
            except asyncio.TimeoutError:
                await app.send_friend_message(
                    config.permission.Master, MessageChain(Plain("超时,已自动取消"))
                )
        else:
            await app.send_friend_message(
                friend,
                MessageChain(
                    Plain(f"未找到您要解封的QQ:{str(id.result)}"),
                ),
            )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                FullMatch("ban"),
                ParamMatch().space(SpacePolicy.FORCE) @ "id",
                ParamMatch() @ "days",
                WildcardMatch(optional=True) @ "tip",
            )
        ],
    )
)
async def Ban(
    app: Ariadne, friend: Friend, id: RegexResult, days: RegexResult, tip: RegexResult
):
    if friend.id == config.permission.Master:
        await app.send_friend_message(
            friend, MessageChain(Plain(f"确定封禁{str(id.result)}?(确认/取消)"))
        )

        @Waiter.create_using_function([FriendMessage])
        async def Banwaiter(waiter_friend: Friend, waiter_message: MessageChain):
            if waiter_friend.id == config.permission.Master:
                saying = waiter_message.display
                if saying == "确认":
                    return True
                elif saying == "取消":
                    return False
                else:
                    await app.send_friend_message(
                        config.permission.Master,
                        MessageChain([Plain("请发送确认或取消")]),
                    )

        try:
            if await asyncio.wait_for(inc.wait(Banwaiter), timeout=20):
                if str(tip.result) == "":
                    await addBanList(
                        int(str(id.result)), int(str(days.result)), time.time()
                    )
                else:
                    await addBanList(
                        int(str(id.result)),
                        int(str(days.result)),
                        time.time(),
                        ban_tip=str(tip.result),
                    )
                await app.send_friend_message(
                    config.permission.Master,
                    MessageChain(
                        Plain(
                            f"成功封禁{str(id.result)} {str(days.result)}天,封禁信息:{str(tip.result)} "
                        )
                    ),
                )
            else:
                await app.send_friend_message(
                    config.permission.Master, MessageChain(Plain("已取消"))
                )

        except asyncio.TimeoutError:
            await app.send_friend_message(
                config.permission.Master, MessageChain(Plain("超时,已自动取消"))
            )
