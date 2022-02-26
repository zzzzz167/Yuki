from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args, AnyParam
from graia.ariadne.message.parser.alconna import AlconnaDispatcher, Arpamar
from utils.control import cheakAcgpicture

saya = Saya.current()
channel = Channel.current()
randomPictureAlc = Alconna(headers=[".setu"], main_args=Args["content":AnyParam]).help(
    "在群中发送 .随机色图 [r18]即可获得色图"
)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(alconna=randomPictureAlc)],
        decorators=[cheakAcgpicture()]
    )
)
async def randomPicture(app: Ariadne, group: Group, source: Source, result: Arpamar):
    if result.matched:
        await app.sendGroupMessage(group, MessageChain.create([Plain("色图来喽~~")]), quote=source)
