import os
import sys
import asyncio
from loguru import logger
from utils.config import init_config
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.broadcast import Broadcast
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.ariadne.console import Console
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

config = init_config()
logger.remove()
logger.add(sys.stderr, level=config.debug.level)
logger.add(
    "./cache/logs/debuglogs",
    rotation="00:00",
    retention="10 days",
    compression="zip",
)
loop = asyncio.new_event_loop()
broadcast = Broadcast(loop=loop)
scheduler = GraiaScheduler(loop, broadcast)
con = Console(
    broadcast=broadcast,
    prompt=HTML(
        "<botname> YUKI </eroerobot><split_2>></split_2> "
    ),
    style=Style(
        [
            ("botname", "bg:#61afef fg:#ffffff"),
            ("split_2", "fg:#61afef"),
        ]
    ),
)
saya = Saya(broadcast)
saya.install_behaviours(BroadcastBehaviour(broadcast))
saya.install_behaviours(GraiaSchedulerBehaviour(scheduler))
saya.install_behaviours(ConsoleBehaviour(con))

app = Ariadne(
    broadcast=broadcast,
    connect_info=MiraiSession(
        config.mirai.host, config.bot.account, config.mirai.verify_key
    ),
)

ignore = ["__init__.py", "__pycache__"]

with saya.module_context():
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

loop.run_until_complete(app.lifecycle())
