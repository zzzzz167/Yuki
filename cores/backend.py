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
from utils.database import reset_sign, resetBanList, delBanList, addBanList, reset_tarot
from loguru import logger
import time

saya = Saya.current()
channel = Channel.current()
restable = {
    "sign": {"function": reset_sign, "name": "签到"},
    "ban": {"function": resetBanList, "name": "黑名单"},
    "tarot": {"function": reset_tarot, "name": "塔罗牌"},
}


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
    if str(module.result) in restable.keys():
        res: str = await console.prompt(
            l_prompt=[("class:warn", " 确定重置%s? " % (module.result)), ("", " (y/n) ")],
            style=Style([("warn", "fg:#cdb4db")]),
        )
        if res.lower() in ("y", "yes"):
            await restable[module.result.display]["function"]()
            logger.info(f"{restable[module.result.display]['name']}重置成功")
    else:
        logger.warning(f"模块{module.result.display}不存在")


@channel.use(ConsoleSchema([Twilight.from_command("unban {qqID}")]))
async def unBan(console: Console, qqID: RegexResult):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 确定解封%s? " % (qqID.result)), ("", " (y/n) ")],
        style=Style([("warn", "fg:#cdb4db")]),
    )
    if res.lower() in ("y", "yes"):
        await delBanList(int(str(qqID.result)))
        logger.info("成功解禁%s" % str(qqID.result))


@channel.use(
    ConsoleSchema(
        [
            Twilight(
                FullMatch("ban"),
                ParamMatch().space(SpacePolicy.FORCE) @ "qqID",
                ParamMatch() @ "days",
                WildcardMatch(optional=True) @ "tip",
            )
        ]
    )
)
async def Ban(console: Console, qqID: RegexResult, days: RegexResult, tip: RegexResult):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 确定封禁%s? " % (qqID.result)), ("", " (y/n) ")],
        style=Style([("warn", "fg:#cdb4db")]),
    )
    if res.lower() in ("y", "yes"):
        if str(tip.result) == "":
            await addBanList(int(str(qqID.result)), int(str(days.result)), time.time())
        else:
            await addBanList(
                int(str(qqID.result)),
                int(str(days.result)),
                time.time(),
                ban_tip=str(tip.result),
            )
        logger.info(
            f"成功封禁{str(qqID.result)} {str(days.result)}天,封禁信息:{str(tip.result)} "
        )
