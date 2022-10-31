import os
from loguru import logger
from utils.config import init_config
from utils.fastapiService import FastAPIStarletteService
from creart import create
from graia.saya import Saya
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.ariadne.entry import config
from graia.broadcast import Broadcast
from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.amnesia.builtins.uvicorn import UvicornService
from graia.scheduler import GraiaScheduler
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import StdoutProxy


bot_config = init_config()
logger.remove()
logger.add(StdoutProxy(raw=True), level=bot_config.debug.level)
logger.add(
    "./cache/logs/debuglogs",
    rotation="00:00",
    retention="10 days",
    compression="zip",
)
broadcast = create(Broadcast)
con = Console(
    broadcast=broadcast,
    prompt=HTML("<botname> YUKI </botname><split>></split> "),
    style=Style(
        [
            ("botname", "bg:#61afef fg:#ffffff"),
            ("split", "fg:#61afef"),
        ]
    ),
    replace_logger=False,
)

create(GraiaScheduler)
saya = create(Saya)
saya.install_behaviours(ConsoleBehaviour(con))

app = Ariadne(
    config(account=bot_config.bot.account, verify_key=bot_config.mirai.verify_key),
)
app.launch_manager.add_service(FastAPIStarletteService())
app.launch_manager.add_service(UvicornService())

ignore = ["__init__.py", "__pycache__"]

with saya.module_context():
    for core_module in os.listdir("cores"):
        if core_module in ignore:
            continue
        try:
            if os.path.isdir(core_module):
                saya.require(f"cores.{core_module}")
            else:
                saya.require(f"cores.{core_module.split('.')[0]}")
        except ModuleNotFoundError:
            pass

    logger.info("core模块加载完成")

    for module in os.listdir("modules"):
        if module in ignore:
            continue
        try:
            if os.path.isdir(module):
                saya.require(f"modules.{module}")
            else:
                saya.require(f"modules.{module.split('.')[0]}")
        except ModuleNotFoundError:
            pass
    logger.info("saya模块加载完成")

if __name__ == "__main__":
    try:
        app.launch_blocking()
    except KeyboardInterrupt:
        app.stop()
        exit()
