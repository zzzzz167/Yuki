from utils.database.db import getGroupSetting, GroupList
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne.message.parser.alconna import Arpamar

config = init_config()
favor = config.permission.favor


def cheakAcgpicture():
    async def cheakCanAcgpicture(app: Ariadne, group: Group, result: Arpamar):
        if result.matched:
            if str(group.id) not in await getGroupSetting(GroupList.acgPicture):
                await app.sendGroupMessage(group, MessageChain.create("抱歉,该群并不允许发色图"))
                raise ExecutionStop

    return Depend(cheakCanAcgpicture)
