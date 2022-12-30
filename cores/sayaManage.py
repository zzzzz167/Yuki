import os
import pickle
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source, Plain
from graia.saya import Saya, Channel
from arclet.alconna import Alconna, Option, Args, Arparma, CommandMeta
from arclet.alconna.graia.dispatcher import AlconnaDispatcher
from arclet.alconna.graia import match_path
from utils.control import Permission
from loguru import logger

saya = Saya.current()
channel = Channel.current()
channel.name("插件管理")
channel.description("bot插件全局管理, Eg: 「.saya reload ill 」重载发病插件")
channel.meta["icon"] = "cog.svg"

manageAlc = Alconna(
    ".saya",
    Option("reloadAll", help_text="重载所有插件"),
    Option("reload", Args["name", str], help_text="重载制定插件"),
    Option("install", Args["name", str], help_text="装载制定插件"),
    Option("uninstall", Args["name", str], help_text="卸载制定插件"),
    meta=CommandMeta(
        "管理saya插件",
    ),
    namespace="core",
)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc, send_flag="post"))
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
@dispatch(AlconnaDispatcher(manageAlc, send_flag="post"))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("reload"))
async def reloadModule(app: Ariadne, group: Group, source: Source, res: Arparma):
    moduleName = "modules." + res.options["reload"]['args']["name"]
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
@dispatch(AlconnaDispatcher(manageAlc, send_flag="post"))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("install"))
async def installModule(app: Ariadne, group: Group, source: Source, res: Arparma):
    moduleName = "modules." + res.options["install"]['args']["name"]
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
        else:
            with open("./unMountPlugin.pickle", "rb") as f:
                unMountPlugin = pickle.load(f)
            for i in unMountPlugin.copy():
                if i["plugin"] == moduleName:
                    unMountPlugin.remove(i)
            with open("./unMountPlugin.pickle", "wb") as f:
                pickle.dump(unMountPlugin, f)


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(manageAlc, send_flag="post"))
@decorate(Permission.require(Permission.BOT_ADMIN), match_path("uninstall"))
async def uninstallModule(app: Ariadne, group: Group, source: Source, res: Arparma):
    moduleName = "modules." + res.options["uninstall"]['args']["name"]
    if moduleName not in saya.channels:
        await app.send_group_message(
            group,
            MessageChain(
                Plain("插件不存在"),
            ),
            quote=source,
        )
        return
    beforeUninstallChannel = saya.channels.get(moduleName)
    uninstallMete = {
        "plugin": moduleName,
        "name": beforeUninstallChannel.meta["name"],
        "description": beforeUninstallChannel.meta["description"],
        "icon": beforeUninstallChannel.meta["icon"],
    }
    saya.uninstall_channel(beforeUninstallChannel)
    await app.send_group_message(
        group,
        MessageChain(
            Plain(f"插件{moduleName}已卸载"),
        ),
        quote=source,
    )
    with open("./unMountPlugin.pickle", "rb") as f:
        unMountPlugin = pickle.load(f)
    unMountPlugin.append(uninstallMete)
    with open("./unMountPlugin.pickle", "wb") as f:
        pickle.dump(unMountPlugin, f)


@listen(ApplicationLaunched)
async def initSaya():
    if not os.path.exists("./unMountPlugin.pickle"):
        logger.info("未找到插件挂载配置文件,正在生成")
        with open("./unMountPlugin.pickle", "wb") as f:
            pickle.dump([], f)

    with open("./unMountPlugin.pickle", "rb") as f:
        unMountPlugin = pickle.load(f)
        with saya.module_context():
            for i in unMountPlugin:
                saya.uninstall_channel(saya.channels.get(i["plugin"]))
                logger.info(f"插件{i}已全局禁用")
