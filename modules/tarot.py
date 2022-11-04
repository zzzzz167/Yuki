import random
import json
from utils.control import cheakBan, groupConfigRequire
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from arclet.alconna import Alconna
from arclet.alconna.graia.dispatcher import AlconnaDispatcher
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Saya, Channel

saya = Saya.current()
channel = Channel.current()
channel.name("塔罗牌")
channel.description("每日塔罗牌/抽取塔罗牌")
channel.meta["switchKey"] = "tarot"
channel.meta["icon"] = "star.svg"

with open("./source/tarot/data.min.json", "r", encoding="UTF-8") as f:
    TEMPLATES = json.loads(f.read())["tarot"]

everyDayTarotAlc = Alconna(headers=["."], command="每日塔罗", help_text="抽取每日塔罗牌")


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(everyDayTarotAlc, send_flag="reply"))
@decorate(groupConfigRequire("tarot"), cheakBan())
async def everyTarot(app: Ariadne, group: Group, member: Member):
    card = random.choice(TEMPLATES)
    name = card["name"]
    imageName = card["imageName"]
    await app.send_group_message(
        group,
        MessageChain(Plain(f"今日塔罗:{name}"), Image(path=f"./source/tarot/{imageName}")),
    )
