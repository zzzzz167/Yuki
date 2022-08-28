from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Source
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna, Args
from arclet.alconna.graia.dispatcher import AlconnaDispatcher, AlconnaProperty
from utils.control import cheakBan, groupConfigRequire
from utils.hitokoto import getJsonHitokoto


channel = Channel.current()
channel.name("一言")

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
    headers=[".hito", ".一言"],
    main_args=Args["content;O", str],
    help_text="获取一条好句子 包括分类:动画、漫画、游戏、文学、原创、网络、其他、影视、诗词、网易云、哲学",
)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(hitoAlc, send_flag="post")],
        decorators=[cheakBan(), groupConfigRequire("hito")],
    )
)
async def groupHelper(
    app: Ariadne, group: Group, source: Source, result: AlconnaProperty
):
    classification = result.result.content
    if classification:
        if classification in clsdic.keys():
            rehito = await getJsonHitokoto(c=clsdic[classification])
            msg = f"{rehito['hitokoto']}\n------「{rehito['from']}」"
            await app.send_group_message(
                group, MessageChain([Plain(msg)]), quote=source
            )
        else:
            await app.send_group_message(
                group,
                MessageChain([Plain("没有这个分类哦,看看使用文档再给我发消息吧")]),
                quote=source,
            )
    else:
        rehito = await getJsonHitokoto()
        msg = f"{rehito['hitokoto']}\n------「{rehito['from']}」"
        await app.send_group_message(group, MessageChain([Plain(msg)]), quote=source)
