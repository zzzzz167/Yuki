from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args, AnyParam
from graia.ariadne.message.parser.alconna import AlconnaDispatcher, Arpamar
from utils.hitokoto import getJsonHitokoto


saya = Saya.current()
channel = Channel.current()
clsdic = {
    "动画": "a",
    "漫画": "b",
    "游戏": "c",
    "文学": "d",
    "原创": "e",
    "网络": "f",
    "其他": "g",
    "影视": "h",
    "诗词": "i",
    "网易云": "j",
    "哲学": "k",
}
hitoAlc = Alconna(
    headers=[".hito", "一言"],
    main_args=Args["content":AnyParam],
).help("获得一条一言")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(alconna=hitoAlc)],
    )
)
async def groupHelper(app: Ariadne, group: Group, source: Source, result: Arpamar):
    if result.matched:
        classification = result.content
        if classification:
            if classification in clsdic.keys():
                rehito = await getJsonHitokoto(c=clsdic[classification])
                msg = f"{rehito['hitokoto']}\n------「{rehito['from']}」"
                await app.sendGroupMessage(
                    group, MessageChain.create([Plain(msg)]), quote=source
                )
            else:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create([Plain("没有这个分类哦,看看使用文档再给我发消息吧")]),
                    quote=source,
                )
        else:
            rehito = await getJsonHitokoto()
            msg = f"{rehito['hitokoto']}\n------「{rehito['from']}」"
            await app.sendGroupMessage(
                group, MessageChain.create([Plain(msg)]), quote=source
            )
