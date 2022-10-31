import time
import aiohttp
import asyncio
from datetime import datetime
from loguru import logger
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source, Image, ForwardNode, Forward
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel
from arclet.alconna import Alconna, Args, Option
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaProperty
from utils.control import cheakAcgpicture, cheakBan, groupConfigRequire
from utils.database import updataGroup, getUser, GroupList, User
from utils.config import init_config


channel = Channel.current()
channel.name("acg图片搜索")
channel.description("简单的tag搜图, Eg: .搜索色图 xxx")
channel.meta["switchKey"] = "searchAcgPic"
channel.meta["icon"] = "pic.svg"

levelToSan: dict = {"r12": 2, "r16": 4, "r18": 6}

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


async def searchGet(tag: str, level: str = None):
    url = "http://a60.one:404"
    if level:
        url += f"/get/tags/{tag}?num=1&only=true&san={levelToSan[level]}"
    else:
        url += f"/get/tags/{tag}?num=1&only=false"
    async with aiohttp.request("GET", url) as resp:
        rd = await resp.json()
        if rd.get("code", 0) == 200:
            data = rd["data"]["imgs"][0]
            msg = f"标题:{data['name']}\n作者:{data['username']}\npid:{data['userid']}\n"
            async with aiohttp.request("GET", data["url"]) as pcrp:
                byte = await pcrp.read()
            return [msg, byte]
        else:
            return [None, None]


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(searchPictureAlc, send_flag="post"))
@decorate(cheakBan(), groupConfigRequire("searchAcgPic"), cheakAcgpicture())
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
                try:
                    await app.recall_message(s_msg)
                except UnknownTarget:
                    logger.warning("图太色了, 未能成功发送, 注意风控可能")
