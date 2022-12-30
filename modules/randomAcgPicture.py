import time
import aiohttp
import asyncio
from datetime import datetime
from loguru import logger
from utils.config import init_config
from peewee import DoesNotExist
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, Image, ForwardNode, Forward
from graia.ariadne.exception import UnknownTarget
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaProperty
from utils.control import cheakAcgpicture, cheakBan, groupConfigRequire
from utils.database import updataGroup, getUser, GroupList

saya = Saya.current()
channel = Channel.current()
channel.name("随机acg图片")
channel.description("随机获取一张图片, Eg: .setu 「r18」")
channel.meta["switchKey"] = "randomAcgPic"
channel.meta["icon"] = "random.svg"

randomPictureAlc = Alconna(
    headers=[".setu"],
    main_args=Args["content;O", str],
    help_text="在群中发送 .setu [r18]即可获得色图",
)

config = init_config()


async def randomGet(r18: bool = False):
    url = "https://api.lolicon.app/setu/v2"
    if r18:
        url += "?r18=2"
    async with aiohttp.request("GET", url) as resp:
        rd = await resp.json()
        data = rd["data"][0]
        msg = f"标题:{data['title']}\n作者:{data['author']}\npid:{data['pid']}\n"
    async with aiohttp.request("GET", data["urls"]["original"]) as pcrp:
        byte = await pcrp.read()
    return [msg, byte]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            AlconnaDispatcher(randomPictureAlc, send_flag="post")
        ],
        decorators=[cheakBan(), groupConfigRequire('randomAcgPic'), cheakAcgpicture()],
    )
)
async def randomPicture(
    app: Ariadne, group: Group, member: Member, source: Source, result: AlconnaProperty
):
    try:
        user = await getUser(member.id)
    except DoesNotExist:
        await app.send_group_message(
            group, MessageChain(Plain("您似乎从来没有签过到呢,先签个到吧 :)")), quote=source
        )
        return
    if result.result.content == "r18":
        if user.favor >= config.permission.favor:
            await app.send_group_message(group, MessageChain("色小鬼,色图马上就来喽,稍等一下"))
            await updataGroup(group.id, {GroupList.acgPictureUse: time.time()})
            data = await randomGet(True)
            b_msg = await app.send_group_message(
                group,
                MessageChain(
                    Forward(
                        node_list=[
                            ForwardNode(
                                target=member,
                                time=datetime.now(),
                                message=MessageChain(
                                    Plain(data[0]), Image(data_bytes=data[1])
                                ),
                            )
                        ]
                    )
                ),
            )
            await asyncio.sleep(30)
            try:
                await app.recall_message(b_msg)
            except UnknownTarget:
                logger.warning("图太色了, 未能成功发送, 注意风控可能")
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
