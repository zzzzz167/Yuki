from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Source, Plain
from graia.saya import Saya, Channel
from arclet.alconna import Alconna, Option, Args
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, Arpamar
from arclet.alconna.graia import match_path
from utils.control import Permission
from utils.text2img import templateToImg
from loguru import logger

saya = Saya.current()
channel = Channel.current()
channel.name("saya插件管理")

manageAlc = Alconna(
    headers=["."],
    command="saya",
    options=[
        Option("list"),
        Option("reloadAll"),
        Option("reload", Args["name", str]),
        Option("install", Args["name", str]),
        Option("uninstall", Args["name", str]),
    ],
    help_text="管理saya插件",
    namespace="core",
)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("reloadAll"))
async def sayaAllReload(app: Ariadne, group: Group, source: Source):
    with saya.module_context():
        module_reload_status = []
        s = saya.channels.copy().items()
        for module, channel in s:
            try:
                if module.split(".")[0] == "cores":
                    continue
                saya.reload_channel(channel)
            except Exception as e:
                module_reload_status.append(f"{channel.name} 重载失败，错误信息：{e}")
    logger.info("插件重载成功 " + "\n".join(module_reload_status))
    await app.send_group_message(
        group,
        MessageChain(
            Plain("插件重载成功" + "\n".join(module_reload_status)),
        ),
        quote=source,
    )


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("reload"))
async def reloadModule(app: Ariadne, group: Group, source: Source, res: Arpamar):
    moduleName = "modules." + res.options["reload"]["name"]
    if moduleName not in saya.channels:
        await app.send_group_message(
            group,
            MessageChain(
                Plain("插件不存在"),
            ),
            quote=source,
        )
        return

    with saya.module_context():
        saya.reload_channel(saya.channels.get(moduleName))
        await app.send_group_message(
            group,
            MessageChain(
                Plain(f"插件{moduleName}重载完成"),
            ),
            quote=source,
        )


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("install"))
async def installModule(app: Ariadne, group: Group, source: Source, res: Arpamar):
    moduleName = "modules." + res.options["install"]["name"]
    if moduleName in saya.channels:
        await app.send_group_message(
            group,
            MessageChain(
                Plain("插件已安装"),
            ),
            quote=source,
        )
        return

    with saya.module_context():
        try:
            saya.require(moduleName)
            await app.send_group_message(
                group,
                MessageChain(
                    Plain(f"插件{moduleName}安装成功"),
                ),
                quote=source,
            )
        except ModuleNotFoundError:
            await app.send_group_message(
                group,
                MessageChain(
                    Plain(f"插件{moduleName}未找到"),
                ),
                quote=source,
            )


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("uninstall"))
async def uninstallModule(app: Ariadne, group: Group, source: Source, res: Arpamar):
    moduleName = "modules." + res.options["uninstall"]["name"]
    if moduleName not in saya.channels:
        await app.send_group_message(
            group,
            MessageChain(
                Plain("插件不存在"),
            ),
            quote=source,
        )
        return
    saya.uninstall_channel(saya.channels.get(moduleName))
    await app.send_group_message(
        group,
        MessageChain(
            Plain(f"插件{moduleName}已卸载"),
        ),
        quote=source,
    )


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc))
@decorate(Permission.require(), match_path("list"))
async def sayaList(
    app: Ariadne,
    group: Group,
    member: Member,
):
    await app.send_group_message(
        group,
        MessageChain(
            At(member.id),
            Image(
                path=await templateToImg(
                    "modulesList.html", {"text": "123"}, fource=True
                )
            ),
        ),
    )
