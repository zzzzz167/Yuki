import asyncio
from creart import create
from loguru import logger
from utils.config import init_config
from utils.database import getGroupSetting
from graia.saya import Saya, Channel
from graia.ariadne.util.saya import listen, dispatch
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.message.parser.twilight import Twilight
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl

inc = create(InterruptControl)
saya = Saya.current()
channel = Channel.current()
channel.name("公告")
channel.description("用来发布bot消息")
channel.meta["switchKey"] = "announce"
channel.meta["icon"] = "horn.svg"
MASTER = init_config().permission.Master


class ContentGet(Waiter.create([FriendMessage])):
    def __init__(self, friend: int):
        self.friendID = friend

    async def detected_event(self, friend: Friend, message: MessageChain):
        if self.friendID == friend.id:
            if message.display == "取消":
                return False, ""
            else:
                return True, message


@listen(FriendMessage)
@dispatch(Twilight.from_command("发布公告"))
async def annoucement(app: Ariadne, friend: Friend):
    if friend.id == MASTER:
        await app.send_friend_message(friend, MessageChain("请在一分钟内发送你要发送的消息或发送‘取消’"))

        try:
            res = await inc.wait(ContentGet(MASTER), timeout=60)
            if res[0]:
                await app.send_friend_message(friend, MessageChain("确定发送? 确认|取消"))

                @Waiter.create_using_function([FriendMessage])
                async def waiter(waiter_friend: Friend, waiter_message: MessageChain):
                    if waiter_friend.id == MASTER:
                        saying = waiter_message.display
                        if saying == "确认":
                            return True
                        elif saying == "取消":
                            return False
                        else:
                            await app.send_friend_message(
                                MASTER,
                                MessageChain("请发送确认或取消"),
                            )

                try:
                    if await asyncio.wait_for(inc.wait(waiter), timeout=20):
                        logger.info("开始发送公告")
                        count = 0
                        for i in await getGroupSetting("announce"):
                            try:
                                await app.send_group_message(
                                    int(i), MessageChain("来自BOT开发者的消息")
                                )
                                await app.send_group_message(int(i), res[1])
                                asyncio.sleep(0.1)
                                count += 1
                            except UnknownTarget:
                                logger.error(f"群组{i}消息发送失败捏, 可能是群无了呢")
                        logger.info("共计发送%s个群聊" % count)
                        await app.send_friend_message(friend, MessageChain("共计发送%s个群聊, 完成了" % count))
                    else:
                        await app.send_friend_message(friend, MessageChain("已取消"))
                except asyncio.TimeoutError:
                    await app.send_friend_message(friend, MessageChain("超时,已自动取消"))
            else:
                await app.send_friend_message(friend, MessageChain("已取消"))
        except asyncio.TimeoutError:
            await app.send_friend_message(friend, MessageChain("超时,已自动取消"))
