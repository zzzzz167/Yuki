import psutil
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Source
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna
from arclet.alconna.graia.dispatcher import AlconnaDispatcher
from utils.control import cheakBan, groupConfigRequire
from utils.text2img import textToImg

channel = Channel.current()
channel.name("运行状态")
channel.description("获取bot当前运行状态, Eg: .status")
channel.meta["switchKey"] = "status"
channel.meta["icon"] = "speedometer.svg"

statusAlc = Alconna(headers=[".status"], help_text="运行状态检查")


def general_system_status() -> str:
    return f"""
    系统状态
    内存：{psutil.virtual_memory().percent}%
    CPU: {psutil.cpu_percent()}%
    磁盘：{psutil.disk_usage('/').percent}%
    开机时间：{psutil.boot_time()}
    磁盘余空间：{psutil.disk_usage('/').free/1024/1024/1024}GB
    磁盘总空间：{psutil.disk_usage('/').total/1024/1024/1024}GB
    内存剩余空间：{psutil.virtual_memory().free/1024/1024/1024}GB
    内存总空间：{psutil.virtual_memory().total/1024/1024/1024}GB
    NetIO: {psutil.net_io_counters()}
    DiskIO: {psutil.disk_io_counters()}
    TCP连接数: {len(psutil.net_connections(kind='tcp'))}
    UDP连接数: {len(psutil.net_connections(kind='udp'))}
    """


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[AlconnaDispatcher(statusAlc, send_flag="reply")],
        decorators=[cheakBan(), groupConfigRequire("status")],
    ),
)
async def groupHelper(app: Ariadne, group: Group, source: Source):
    await app.send_group_message(
        group,
        MessageChain([Image(path=await textToImg(general_system_status()))]),
        quote=source,
    )
