import random
import json
from utils.control import cheakBan, groupConfigRequire
from utils.database import User, getUser, updataUser
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source, Plain, Image
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
async def everyTarot(app: Ariadne, group: Group, member: Member, source: Source):
    try:
        userDB = await getUser(member.id)
    except User.DoesNotExist:
        await app.send_group_message(
            group, MessageChain(Plain("您似乎从来没有签过到呢,先签个到吧 :D")), quote=source
        )
        return
    if userDB.every_tarot:
        await app.send_group_message(
            group, MessageChain(Plain("今天你已经领取过塔罗牌牌数了, 明天再来吧")), quote=source
        )
    else:
        quantity = random.randint(0, 10)
        orientation = random.choice(("顺位", "逆位"))
        card = random.choice(TEMPLATES)
        name = card["name"]
        imagePath = "./source/tarot/" + card["imageName"]
        await updataUser(
            member.id, {User.every_tarot: True, User.tarot_quantity: quantity}
        )
        newdata = await getUser(member.id)
        await app.send_group_message(
            group,
            MessageChain(
                [
                    Image(path=imagePath),
                    Plain(f"\n你的今日塔罗:{name} - {orientation}"),
                    Plain(f"\n获得今日抽牌次数:{newdata.tarot_quantity}"),
                ]
            ),
        )
