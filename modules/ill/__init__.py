import json
import random
import time
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args, Empty
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaProperty
from utils.control import cheakBan
from utils.database.db import addBanList

saya = Saya.current()
channel = Channel.current()

with open("./source/ill/data.json", "r", encoding="UTF-8") as f:
    TEMPLATES = json.loads(f.read())["data"]

ill = Alconna(
    headers=[".发病"],
    main_args=Args["content;0", [str, At], Empty],
    help_text="生成一段发病文字 Example: .发病 老公;",
)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(ill, send_flag="reply")],
        decorators=[cheakBan()],
    )
)
async def fabing(app: Ariadne, member: Member, group: Group, result: AlconnaProperty):
    if result.result.content:
        content = result.result.content[0]
        if type(content) == At:
            obj = await app.get_member(group, content.target)
            target = obj.name
        elif type(content) == str:
            target = content
        else:
            return

        if len(target) >= 25:
            await app.send_group_message(group, MessageChain("字数太长啦,想整活?门都没有,封禁了"))
            await addBanList(member.id, 2, time.time(), "发送超长信息")
            return
        elif len(target) >= 15:
            await app.send_group_message(group, MessageChain("字数太长啦,谁名字这么长呢"))
            return
    else:
        target = member.name
    await app.send_group_message(
        group, MessageChain(random.choice(TEMPLATES).format(target=target))
    )
