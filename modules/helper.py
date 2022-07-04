from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna
from arclet.alconna.graia.dispatcher import AlconnaDispatcher
from arclet.alconna.manager import CommandManager


saya = Saya.current()
channel = Channel.current()
helperAlc = Alconna(headers=[".help", ".帮助"], help_text="帮助文档")
manager = CommandManager()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(alconna=helperAlc)],
    )
)
async def groupHelper(app: Ariadne, group: Group, source: Source):
    await app.send_group_message(
        group,
        MessageChain(
            [
                Plain(
                    manager.all_command_help(
                        header="Yuki使用帮助",
                        footer="任意命令均可使用 .命令名 --help 查看更详细的帮助。",
                    )
                )
            ]
        ),
        quote=source,
    )
