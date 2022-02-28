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
from arclet.alconna import Alconna, Args, AnyParam
from graia.ariadne.message.parser.alconna import AlconnaDispatcher, Arpamar
from utils.control import cheakAcgpicture
from utils.database.db import updataGroup, getUser, GroupList

saya = Saya.current()
channel = Channel.current()
randomPictureAlc = Alconna(headers=[".setu"], main_args=Args["content":AnyParam]).help(
    "在群中发送 .随机色图 [r18]即可获得色图"
)
config = init_config()


async def randomGet(r18: bool = False):
    url = "https://api.lolicon.app/setu/v2"
    if r18:
        url += "?r18=1"
    async with aiohttp.request("GET", url) as resp:
        rd = await resp.json()
        msg = f"标题:{rd['data'][0]['title']}\n作者:{rd['data'][0]['author']}\npid:{rd['data'][0]['pid']}\n"
    async with aiohttp.request("GET", rd["data"][0]["urls"]["original"]) as pcrp:
        byte = await pcrp.read()
    return [msg, byte]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(alconna=randomPictureAlc)],
        decorators=[cheakAcgpicture()],
    )
)
async def randomPicture(
    app: Ariadne, group: Group, member: Member, source: Source, result: Arpamar
):
    if result.matched:
        if result.content == "r18":
            user = await getUser(member.id)
            if user.favor >= config.permission.favor:
                await app.sendGroupMessage(
                    group, MessageChain.create("色小鬼,色图马上就来喽,稍等一下")
                )
                await updataGroup(group.id, {GroupList.acgPictureUse: time.time()})
                data = await randomGet(True)
                b_msg = await app.sendGroupMessage(
                    group,
                    MessageChain.create([Plain(data[0]), Image(data_bytes=data[1])]),
                    quote=source,
                )
                await asyncio.sleep(30)
                await app.recallMessage(b_msg)
            else:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create(
                        [
                            Plain(
                                f"丑弟弟,才陪姐姐几天,就想要这么涩的(保持每天签到,使好感度到{config.permission.favor}后在来吧"
                            )
                        ]
                    ),
                    quote=source,
                )
        elif result.content:
            await app.sendGroupMessage(
                group, MessageChain.create("呜,你输入的指令似乎有错误哦,检查后再来看看吧"), quote=source
            )
        else:
            await app.sendGroupMessage(group, MessageChain.create("色图马上就来喽,稍等一下"))
            await updataGroup(group.id, {GroupList.acgPictureUse: time.time()})
            data = await randomGet()
            await app.sendGroupMessage(
                group,
                MessageChain.create([Plain(data[0]), Image(data_bytes=data[1])]),
                quote=source,
            )
