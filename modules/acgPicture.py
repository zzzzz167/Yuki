import time
import aiohttp
import asyncio
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, Image
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaProperty
from utils.control import cheakAcgpicture
from utils.database.db import updataGroup, getUser, GroupList

saya = Saya.current()
channel = Channel.current()
randomPictureAlc = Alconna(
    headers=[".setu"],
    main_args=Args["content;O", str],
    help_text="在群中发送 .随机色图 [r18]即可获得色图",
)
config = init_config()


async def randomGet(r18: bool = False):
    url = "http://a60.one:404"
    if r18:
        url += "?san=6&only=true"
    async with aiohttp.request("GET", url) as resp:
        rd = await resp.json()
        data = rd["data"]["imgs"][0]
        msg = f"标题:{data['name']}\n作者:{data['username']}\npid:{data['userid']}\n"
    async with aiohttp.request("GET", data["url"]) as pcrp:
        byte = await pcrp.read()
    return [msg, byte]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            AlconnaDispatcher(alconna=randomPictureAlc, help_flag="reply")
        ],
        decorators=[cheakAcgpicture()],
    )
)
async def randomPicture(
    app: Ariadne, group: Group, member: Member, source: Source, result: AlconnaProperty
):
    if result.result.content == "r18":
        user = await getUser(member.id)
        if user.favor >= config.permission.favor:
            await app.send_group_message(group, MessageChain("色小鬼,色图马上就来喽,稍等一下"))
            await updataGroup(group.id, {GroupList.acgPictureUse: time.time()})
            data = await randomGet(True)
            b_msg = await app.send_group_message(
                group,
                MessageChain([Plain(data[0]), Image(data_bytes=data[1])]),
                quote=source,
            )
            await asyncio.sleep(30)
            await app.recall_message(b_msg)
        else:
            await app.send_group_message(
                group,
                MessageChain(
                    [
                        Plain(
                            f"丑弟弟,才陪姐姐几天,就想要这么涩的(保持每天签到,使好感度到{config.permission.favor}后在来吧"
                        )
                    ]
                ),
                quote=source,
            )
    elif result.result.content:
        await app.send_group_message(
            group, MessageChain("呜,你输入的指令似乎有错误哦,检查后再来看看吧"), quote=source
        )
    else:
        await app.send_group_message(group, MessageChain("色图马上就来喽,稍等一下"))
        await updataGroup(group.id, {GroupList.acgPictureUse: time.time()})
        data = await randomGet()
        await app.send_group_message(
            group,
            MessageChain([Plain(data[0]), Image(data_bytes=data[1])]),
            quote=source,
        )
