import asyncio
import json
import random
from creart import create
from loguru import logger
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.saya import Channel
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl
from arclet.alconna import Alconna, Option, Args, Subcommand
from arclet.alconna.graia.dispatcher import AlconnaDispatcher
from arclet.alconna.graia import match_path, Query
from utils.control import Permission, cheakBan, groupConfigRequire
from utils.database import getGroup, updataGroup, GroupList

channel = Channel.current()
channel.name("群组关键词设置")
inc = create(InterruptControl)

keyAlc = Alconna(
    headers=["."],
    command="keyReply",
    options=[
        Subcommand(
            "add",
            args=Args["key", str],
            options=[
                Option("probability", Args["prob", float, 0.6], alias=["-P"], help_text="设置回复概率,区间为0~1"),
                Option(
                    "mode",
                    Args["modele", ["completely", "part"], "completely"],
                    alias=["-M"],
                    help_text="设置回复模式「completely」完全匹配消息, 「part」消息中包含关键字"
                ),
            ],
            help_text="添加一个新的关键词回复"
        ),
        Subcommand("remove", args=Args["key", str], help_text="删除一个已知的关键词回复"),
    ],
    help_text="关键词回复"
)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(keyAlc, send_flag="post"))
@decorate(
    groupConfigRequire("keyReplaySwitch"),
    Permission.require(Permission.GROUP_ADMIN),
    match_path("add"),
)
async def addKeyReply(
    app: Ariadne,
    group: Group,
    source: Source,
    member: Member,
    mode: Query[str] = Query("add.mode.modele", "completely"),
    probability: Query[float] = Query("add.probability.prob", 0.6),
    key: Query[str] = Query("add.key"),
):
    await app.send_group_message(
        group,
        MessageChain(
            f"回复关键词{key.result}正在被以{mode.result}的模式和{probability.result}的概率创建\n请于15s内回复需要的回复的富文本信息,或者输入'取消'取消本次操作"
        ),
        quote=source,
    )

    @Waiter.create_using_function([GroupMessage])
    async def neWaiter(
        waiter_member: Member, waiter_group: Group, waiter_message: MessageChain
    ) -> MessageChain:
        if waiter_member.id == member.id and waiter_group.id == group.id:
            return waiter_message

    try:
        retMsg: MessageChain = await asyncio.wait_for(inc.wait(neWaiter), timeout=15)
        if retMsg.display == "取消":
            await app.send_group_message(group, MessageChain("任务已取消"), quote=source)
            return
        else:
            groupDB = await getGroup(group.id)
            groupConfig = json.loads(groupDB.config)
            if not isinstance(groupConfig["keyReplayList"], list):
                logger.warning(f"群组{group.name}({group.id})关键词配置内容类型错误,已重写")
                groupConfig.update({"keyReplayList": []})
                await updataGroup(
                    group.id,
                    {GroupList.config: json.dumps(groupConfig, separators=(",", ":"))},
                )
                groupDB = await getGroup(group.id)

            newReply = {
                "key": key.result,
                "reply": retMsg.as_persistent_string(),
                "mode": mode.result,
                "probability": probability.result,
            }
            s = True
            for i in groupConfig["keyReplayList"]:
                if i["key"] == key.result:
                    i.update(newReply)
                    s = False
            if s:
                groupConfig["keyReplayList"].append(newReply)

            await updataGroup(
                group.id,
                {GroupList.config: json.dumps(groupConfig, separators=(",", ":"))},
            )
            await app.send_group_message(
                group, MessageChain(f"回复关键字{key.result}添加完成!"), quote=source
            )
    except asyncio.TimeoutError:
        await app.send_group_message(group, MessageChain("任务超时已取消"), quote=source)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(keyAlc, send_flag="post"))
@decorate(
    groupConfigRequire("keyReplaySwitch"),
    Permission.require(Permission.GROUP_ADMIN),
    match_path("remove"),
)
async def keyRemove(app: Ariadne, group: Group, key: Query[str] = Query("remove.key")):
    groupDB = await getGroup(group.id)
    groupConfig = json.loads(groupDB.config)
    deList = []
    for i in groupConfig["keyReplayList"]:
        if i["key"] == key.result:
            deList.append(i)
    if len(deList) == 0:
        await app.send_group_message(group, MessageChain(f"关键字{key.result}未找到"))
        return

    for s in deList:
        groupConfig["keyReplayList"].remove(s)
    await updataGroup(
        group.id,
        {GroupList.config: json.dumps(groupConfig, separators=(",", ":"))},
    )
    await app.send_group_message(group, MessageChain(f"关键字{key.result}已移除"))


@listen(GroupMessage)
@decorate(groupConfigRequire("keyReplaySwitch"), cheakBan())
async def replayFunc(app: Ariadne, group: Group, message: MessageChain):
    groupDB = await getGroup(group.id)
    groupConfig = json.loads(groupDB.config)
    if ".key" in message.display:
        return
    for i in groupConfig["keyReplayList"]:
        if i["mode"] == "part":
            if i["key"] in message.display:
                if i["probability"] >= random.random():
                    await app.send_group_message(
                        group, MessageChain.from_persistent_string(i["reply"])
                    )
        elif i["mode"] == "completely":
            if i["key"] == message.display:
                if i["probability"] >= random.random():
                    await app.send_group_message(
                        group, MessageChain.from_persistent_string(i["reply"])
                    )
