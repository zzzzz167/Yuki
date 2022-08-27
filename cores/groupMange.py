from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source, Image
from graia.ariadne.util.saya import listen, dispatch, decorate
from arclet.alconna import Alconna, Args, Option
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, Arpamar
from arclet.alconna.graia import match_path
from graia.saya import Channel
from utils.control import Permission
from utils.config import init_config
from utils.database import changeGroupSet
from utils.text2img import textToImg

channel = Channel.current()
channel.name("群组插件设置")
configKey = init_config().groupDef.pluginSwitch[0].keys()
switch = ["on", "off"]
pluginIntroduction = {
    "power": "是否为本群启用bot",
    "status": "bot状态获取",
    "goodTime": "早晚安定时消息",
    "hito": "一言获取",
    "randomAcgPic": "随机色图",
    "searchAcgPic": "tag搜索色图",
    "sign": "签到",
    "moyu": "摸鱼消息发送",
    "ill": "发病句子生成",
}
ignoreKey = ["keyReplayList"]

groupMange = Alconna(
    headers=[".bot"],
    options=[Option("config", Args["name", str]["switch", switch]), Option("list")],
    help_text="群组bot管理",
    namespace="core",
)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(groupMange))
@decorate(Permission.require(Permission.GROUP_ADMIN), match_path("config"))
async def groupPluginsMange(app: Ariadne, group: Group, source: Source, res: Arpamar):
    pluginName = res.options["config"]["name"]
    if pluginName in ignoreKey:
        await app.send_group_message(
            group, MessageChain(f"{pluginName}不可进行操作, 可使用.bot list查看插件名称"), quote=source
        )
        return

    if pluginName not in configKey:
        await app.send_group_message(
            group, MessageChain(f"{pluginName}不存在, 可使用.bot list查看插件名称"), quote=source
        )
        return

    if res.options["config"]["switch"] == "on":
        await changeGroupSet(group.id, pluginName, True)
        await app.send_group_message(
            group, MessageChain(f"{pluginName}已为本群组启用"), quote=source
        )
    elif res.options["config"]["switch"] == "off":
        await changeGroupSet(group.id, pluginName, False)
        await app.send_group_message(
            group, MessageChain(f"{pluginName}已为本群组停用"), quote=source
        )


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(groupMange))
@decorate(Permission.require(Permission.GROUP_ADMIN), match_path("list"))
async def groupPluginsList(app: Ariadne, group: Group, source: Source):
    msg = "tip:以下均为 插件名称:插件简介 的格式,在设置时请用插件名称"
    for i in configKey:
        if i not in ignoreKey:
            msg += i + " : " + pluginIntroduction.get(i, "没有简介捏") + "\n"
    await app.send_group_message(
        group,
        MessageChain(Image(path=await textToImg(msg))),
        quote=source,
    )
