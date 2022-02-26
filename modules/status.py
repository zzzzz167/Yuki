import psutil
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.model import Friend
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

saya = Saya.current()
channel = Channel.current()
config = init_config()


async def get_sys_status_sync() -> dict:
    net = psutil.net_io_counters()
    net_sent = net.bytes_sent / 1024 / 1024
    net_recv = net.bytes_recv / 1024 / 1024
    v_mem = psutil.virtual_memory()
    s_mem = psutil.swap_memory()
    cpu_percent = str(psutil.cpu_percent(0))
    cpu_tem = str(psutil.sensors_temperatures()["cpu_thermal"][0].current)
    v_mem_percent = str(v_mem.percent)
    s_mem_percent = str(s_mem.percent)
    return {
        "当前CPU占用": cpu_percent,
        "当前CPU温度": cpu_tem,
        "实体内存占用": v_mem_percent,
        "交换内存占用": s_mem_percent,
        "网络发包": net_sent,
        "网络收包": net_recv,
    }


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight([FullMatch(".status")])],
    )
)
async def status(app: Ariadne, friend: Friend):
    if friend.id == config.permission.Master:
        await app.sendMessage(
            friend,
            MessageChain.create(Plain("目前已知情报为:\n" + str(await get_sys_status_sync()))),
        )
