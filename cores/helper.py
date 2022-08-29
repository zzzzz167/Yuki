import pickle
import json
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
from utils.control import cheakBan
from utils.text2img import textToImg, templateToImg
from utils.database import getGroup


saya = Saya.current()
channel = Channel.current()
channel.name("帮助")
channel.description("生成帮助消息, Eg: .help/.插件 --help")
channel.meta["icon"] = "help.svg"

helperAlc = Alconna(headers=[".help", ".帮助"], help_text="帮助文档")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(helperAlc)],
        decorators=[cheakBan()],
    ),
)
async def groupHelper(app: Ariadne, group: Group, source: Source):
    tempOpin = {"pluginsEnable": [], "unable": {"group": [], "global": []}, "cores": []}
    config = json.loads(await getGroup(group.id).config)
    with open("./unMountPlugin.pickle", "rb") as f:
        unMountPlugin = pickle.load(f)
    for module, channel in saya.channels.items():
        if "cores." in module:
            if channel.meta["name"]:
                tempOpin["cores"].append(
                    {
                        "name": channel.meta["name"],
                        "description": channel.meta["description"],
                        "icon": channel.meta["icon"],
                    }
                )
        else:
            if channel.meta["name"] in unMountPlugin:
                tempOpin["unable"]["global"].append(
                    {
                        "name": channel.meta["name"],
                        "description": channel.meta["description"],
                        "icon": channel.meta["icon"],
                    }
                )
            elif config.get(channel.meta["switchKey"]):
                tempOpin["pluginsEnable"].append(
                    {
                        "name": channel.meta["name"],
                        "description": channel.meta["description"],
                        "icon": channel.meta["icon"],
                    }
                )
            else:
                tempOpin["unable"]["group"].append(
                    {
                        "name": channel.meta["name"],
                        "description": channel.meta["description"],
                        "icon": channel.meta["icon"],
                    }
                )
    await app.send_group_message(
        group,
        MessageChain([Image(path=await templateToImg("helpTemplate.html", tempOpin))]),
        quote=source
    )


@listen(AlconnaOutputMessage)
async def pluginHelper(app: Ariadne, event: MessageEvent, output: str, source: Source):
    await app.send_group_message(
        event.sender.group,
        MessageChain([Image(path=await textToImg(output, True))]),
        quote=source,
    )
