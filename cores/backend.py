from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    Twilight,
    RegexResult,
    ParamMatch,
    WildcardMatch,
    SpacePolicy,
)
from graia.saya import Channel, Saya
from prompt_toolkit.styles import Style
from utils.database.db import reset_sign, resetBanList, delBanList, addBanList
from loguru import logger
from utils.text2img import textToImg
import time

saya = Saya.current()
channel = Channel.current()


@channel.use(ConsoleSchema([Twilight([FullMatch("stop")])]))
async def stop(app: Ariadne, console: Console):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 你确定要退出吗? "), ("", " (y/n) ")],
        style=Style([("warn", "fg:#d00000")]),
    )
    if res.lower() in ("y", "yes"):
        app.stop()
        console.stop()


@channel.use(ConsoleSchema([Twilight.from_command("rest {module}")]))
async def restModule(console: Console, module: RegexResult):
    if str(module.result) == "sign":
        res: str = await console.prompt(
            l_prompt=[("class:warn", " 确定重置%s? " % (module.result)), ("", " (y/n) ")],
            style=Style([("warn", "fg:#cdb4db")]),
        )
        if res.lower() in ("y", "yes"):
            await reset_sign()
            logger.info("签到重置成功")
    if str(module.result) == "ban":
        res: str = await console.prompt(
            l_prompt=[("class:warn", " 确定重置%s? " % (module.result)), ("", " (y/n) ")],
            style=Style([("warn", "fg:#cdb4db")]),
        )
        if res.lower() in ("y", "yes"):
            await resetBanList()
            logger.info("黑名单重置成功")


@channel.use(ConsoleSchema([Twilight.from_command("unban {id}")]))
async def unBan(console: Console, id: RegexResult):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 确定解封%s? " % (id.result)), ("", " (y/n) ")],
        style=Style([("warn", "fg:#cdb4db")]),
    )
    if res.lower() in ("y", "yes"):
        await delBanList(int(str(id.result)))
        logger.info("成功解禁%s" % str(id.result))


@channel.use(
    ConsoleSchema(
        [
            Twilight(
                FullMatch("ban"),
                ParamMatch().space(SpacePolicy.FORCE) @ "id",
                ParamMatch() @ "days",
                WildcardMatch(optional=True) @ "tip",
            )
        ]
    )
)
async def Ban(console: Console, id: RegexResult, days: RegexResult, tip: RegexResult):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 确定封禁%s? " % (id.result)), ("", " (y/n) ")],
        style=Style([("warn", "fg:#cdb4db")]),
    )
    if res.lower() in ("y", "yes"):
        if str(tip.result) == "":
            await addBanList(int(str(id.result)), int(str(days.result)), time.time())
        else:
            await addBanList(
                int(str(id.result)),
                int(str(days.result)),
                time.time(),
                ban_tip=str(tip.result),
            )
        logger.info(f"成功封禁{str(id.result)} {str(days.result)}天,封禁信息:{str(tip.result)} ")


@channel.use(ConsoleSchema([Twilight.from_command("test")]))
async def test():
    with saya.module_context():
        h = ''
        for module, channel in saya.channels.items():
            h += f"module: {module} |" + f"name:{channel.meta['name']}\n"
        await textToImg(h)
