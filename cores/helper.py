from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Source
from graia.ariadne.util.saya import listen
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaOutputMessage
from graia.ariadne.event.message import MessageEvent
from arclet.alconna.manager import CommandManager
from utils.control import cheakBan
from utils.text2img import textToImg


saya = Saya.current()
channel = Channel.current()
channel.name("帮助")

helperAlc = Alconna(headers=[".help", ".帮助"], help_text="帮助文档")
manager = CommandManager()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(helperAlc)],
        decorators=[cheakBan()],
    ),
)
async def groupHelper(app: Ariadne, group: Group, source: Source):
    await app.send_group_message(
        group,
        MessageChain(
            [
                Image(
                    path=await textToImg(
                        manager.all_command_help(
                            header="Yuki使用帮助",
                            footer="任意命令均可使用 .命令名 --help 查看更详细的帮助。",
                        )
                    )
                )
            ]
        ),
        quote=source,
    )


@listen(AlconnaOutputMessage)
async def pluginHelper(app: Ariadne, event: MessageEvent, output: str, source: Source):
    await app.send_group_message(
        event.sender.group,
        MessageChain([Image(path=await textToImg(output, True))]),
        quote=source
    )
