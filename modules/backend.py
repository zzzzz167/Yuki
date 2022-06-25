from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import FullMatch, Twilight, RegexResult
from graia.saya import Channel
from prompt_toolkit.styles import Style
from utils.database.db import reset_sign
from loguru import logger

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
async def restSign(console: Console, module: RegexResult):
    if str(module.result) == "sign":
        res: str = await console.prompt(
            l_prompt=[("class:warn", " 确定重置%s? " % (module.result)), ("", " (y/n) ")],
            style=Style([("warn", "fg:#cdb4db")]),
        )
        if res.lower() in ("y", "yes"):
            await reset_sign()
            logger.info("签到重置成功")
