import time
from datetime import datetime
import aiohttp
import asyncio
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, Image, ForwardNode, Forward
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args, Option
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaProperty
from utils.control import cheakAcgpicture, cheakBan
from utils.database.db import updataGroup, getUser, GroupList, User

saya = Saya.current()
channel = Channel.current()

levelToSan: dict = {"r12": 2, "r16": 4, "r18": 6}
randomPictureAlc = Alconna(
    headers=[".setu"],
    main_args=Args["content;O", str],
    help_text="在群中发送 .setu [r18]即可获得色图",
)
searchPictureAlc = Alconna(
    ".搜索色图",
    Args["content;0", str],
    options=[
        Option(
            "level",
            Args[
                "level",
                str,
            ],
            alias=["-L", "--level"],
            help_text="搜图所返回的等级包括[r12,r16, r18],默认为r16",
        )
    ],
    help_text="简单的tag搜图",
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


async def searchGet(tag: str, level: str = None):
    url = "http://a60.one:404"
    if level:
        url += f"/get/tags/{tag}?num=1&only=true&san={levelToSan[level]}"
    else:
        url += f"/get/tags/{tag}?num=1&only=false"
    async with aiohttp.request("GET", url) as resp:
        rd = await resp.json()
        if rd["code"] == 200:
            data = rd["data"]["imgs"][0]
            msg = f"标题:{data['name']}\n作者:{data['username']}\npid:{data['userid']}\n"
            async with aiohttp.request("GET", data["url"]) as pcrp:
                byte = await pcrp.read()
            return [msg, byte]
        else:
            return [None, None]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            AlconnaDispatcher(alconna=randomPictureAlc, help_flag="reply")
        ],
        decorators=[cheakAcgpicture(), cheakBan()],
    )
)
async def randomPicture(
    app: Ariadne, group: Group, member: Member, source: Source, result: AlconnaProperty
):
    try:
        user = await getUser(member.id)
    except User.DoesNotExist:
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


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            AlconnaDispatcher(alconna=searchPictureAlc, help_flag="reply")
        ],
        decorators=[cheakAcgpicture(), cheakBan()],
    )
)
async def searchPicture(
    app: Ariadne, group: Group, member: Member, source: Source, result: AlconnaProperty
):
    arp = result.result
    contents = arp.content[0]
    level = arp.query("level.level")
    er = False
    try:
        user = await getUser(member.id)
    except User.DoesNotExist:
        await app.send_group_message(
            group, MessageChain(Plain("您似乎从来没有签过到呢,先签个到吧 :)")), quote=source
        )
        return
    if contents is None:
        er = True
        await app.send_group_message(
            group, MessageChain(Plain("检查下你的指令吧,没有要搜的东西哦😯")), quote=source
        )
    else:
        if level:
            if level in levelToSan.keys():
                if level == "r18":
                    if user.favor < config.permission.favor:
                        await app.send_group_message(
                            group,
                            MessageChain(
                                Plain(f"太涩啦,不能给你看,使好感度到{config.permission.favor}后在来吧")
                            ),
                            quote=source,
                        )
                        er = True
            else:
                MessageChain(Plain("检查下你的指令吧,分级不对哦"))
                er = True

    if er is False:
        await app.send_group_message(group, MessageChain("色图马上就来喽,稍等一下"))
        if level:
            data = await searchGet(contents, level=level)
        else:
            data = await searchGet(contents)
        if data[0] is None:
            await app.send_group_message(
                group,
                MessageChain([Plain("出现错误了呢,可能是你xp太怪了呢")]),
                quote=source,
            )
        else:
            await updataGroup(group.id, {GroupList.acgPictureUse: time.time()})
            s_msg = await app.send_group_message(
                group,
                MessageChain(
                    Forward(
                        node_list=[
                            ForwardNode(
                                target=member,
                                time=datetime.now(),
                                message=MessageChain(
                                    Plain(f"你要的关于{contents}的色图来啦\n"),
                                    Plain(data[0]),
                                    Image(data_bytes=data[1]),
                                ),
                            )
                        ]
                    )
                ),
            )
            if level == "r18":
                await asyncio.sleep(30)
                await app.recall_message(s_msg)
