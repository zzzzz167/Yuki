from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna
from graia.ariadne.message.parser.alconna import AlconnaDispatcher, Arpamar
from arclet.alconna.manager import CommandManager


saya = Saya.current()
channel = Channel.current()
helperAlc = Alconna(headers=[".help", ".帮助"]).help("帮助命令")
manager = CommandManager()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(alconna=helperAlc)],
    )
)
async def groupHelper(app: Ariadne, group: Group, source: Source, result: Arpamar):
    if result.matched:
        await app.sendGroupMessage(
            group,
            MessageChain.create(
                [
                    Plain(
                        manager.all_command_help(
                            frontTips="Yuko使用帮助",
                            posTips="任意命令均可使用 .命令名 --help 查看更详细的帮助。",
                        )
                    )
                ]
            ),
            quote=source,
        )
