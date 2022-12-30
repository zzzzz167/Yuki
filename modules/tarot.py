import random
import json
from io import BytesIO
from loguru import logger
from PIL import Image as Img
from peewee import DoesNotExist
from utils.control import cheakBan, groupConfigRequire
from utils.database import User, getUser, updataUser, reset_tarot
from utils.text2img import textToImg
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source, Plain, Image
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.saya import Saya, Channel
from arclet.alconna import Alconna, CommandMeta
from arclet.alconna.graia.dispatcher import AlconnaDispatcher


saya = Saya.current()
channel = Channel.current()
channel.name("塔罗牌")
channel.description("每日塔罗牌/抽取塔罗牌")
channel.meta["switchKey"] = "tarot"
channel.meta["icon"] = "star.svg"

with open("./source/tarot/data.min.json", "r", encoding="UTF-8") as f:
    TEMPLATES = json.loads(f.read())["tarot"]

everyDayTarotAlc = Alconna(".每日塔罗", meta=CommandMeta("抽取每日塔罗牌"))


@listen(GroupMessage)
@dispatch(AlconnaDispatcher(everyDayTarotAlc, send_flag="reply"))
@decorate(groupConfigRequire("tarot"), cheakBan())
async def everyTarot(app: Ariadne, group: Group, member: Member, source: Source):
    try:
        userDB = await getUser(member.id)
    except DoesNotExist:
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
        neOrientation = random.choice((True, False))
        card = random.choice(TEMPLATES)
        name = card["name"]
        imagePath = "./source/tarot/" + card["imageName"]
        await updataUser(
            member.id, {User.every_tarot: True, User.tarot_quantity: quantity}
        )
        newdata = await getUser(member.id)
        pic = Img.open(imagePath)
        out = BytesIO()
        if neOrientation:
            pic.transpose(Img.FLIP_TOP_BOTTOM).transpose(Img.FLIP_LEFT_RIGHT).save(
                out, format="JPEG", quantity=99
            )
            orientation = "逆位"
            pos = "negative"
        else:
            pic.save(out, format="jpeg", quantity=99)
            orientation = "顺位"
            pos = "positive"
        await app.send_group_message(
            group,
            MessageChain(
                [
                    Image(data_bytes=out.getvalue()),
                    Plain(f"\n你的今日塔罗:{name} - {orientation}"),
                    Plain(f"\n获得今日抽牌次数:{newdata.tarot_quantity}\n"),
                    Image(path=await textToImg("关键词:" + card[pos])),
                ]
            ),
            quote=source,
        )


@channel.use(SchedulerSchema(crontabify("0 0 * * *")))
async def rest():
    await reset_tarot()
    logger.info("每日塔罗重置成功")
