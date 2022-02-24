from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch

saya = Saya.current()
channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"head": UnionMatch(".帮助", ".help")})],
    )
)
async def groupHelper(app: Ariadne, group: Group, message: MessageChain):
    print("hello ?")
