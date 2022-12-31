from graia.ariadne.app import Ariadne
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain, Source, Image
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel
from arclet.alconna import Alconna, Args, CommandMeta, Empty, Arparma, Option
from arclet.alconna.graia.dispatcher import AlconnaDispatcher
from utils.control import cheakBan, groupConfigRequire
from utils.text2img import templateToImg

channel = Channel.current()
channel.name("入典")
channel.description("哈哈, 入典, 合影! Eg: .入典")
channel.meta["switchKey"] = "dian"
channel.meta["icon"] = "hand.svg"

dianAlc = Alconna(
    ".入典",
    Args["content", str, Empty],
    Option("color", alias=["-c"], help_text="生成头像是否为彩色"),
    meta=CommandMeta("哈哈, 入典, 合影! Eg: .入典"),
)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(dianAlc, send_flag="reply"))
@decorate(cheakBan(), groupConfigRequire("dian"))
async def dianPic(
    app: Ariadne,
    group: Group,
    member: Member,
    event: MessageEvent,
    res: Arparma,
    source: Source,
):
    content = res.query("content")
    color = res.query("color")
    if not content and not event.quote:
        await app.send_group_message(
            group, MessageChain("回复消息或手动输入内容时可用"), quote=source
        )
        return
    if not (text := content):
        try:
            event: MessageEvent = await app.get_message_from_id(
                event.quote.id, event.sender.group
            )
            text = event.message_chain.display
        except UnknownTarget:
            app.send_group_message(group, MessageChain("未缓存该消息"), quote=source)
            return
    metadata = {
        "qqnum": event.sender.id,
        "content": text,
        "name": event.sender.name,
        "filter": "" if color else "filter: grayscale(100%);",
    }
    await app.send_group_message(
        group,
        MessageChain(
            Image(
                path=await templateToImg(
                    "dianTemplate.html", metadata, viewport={"width": 640, "height": 1}
                )
            )
        ),
    )
