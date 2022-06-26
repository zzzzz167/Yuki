import time
from utils.database.db import getGroupSetting, getGroup, GroupList
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop

config = init_config()
favor = config.permission.favor
cd = config.permission.cd


def cheakAcgpicture():
    async def cheakCanAcgpicture(
        app: Ariadne, group: Group, source: Source
    ):
        g = await getGroup(group.id)
        xc = time.time() - int(g.acgPictureUse)
        if xc < cd:
            await app.send_group_message(
                group,
                MessageChain(f"技能冷却中,距离下次使用还有{round(cd - xc, 2)}s"),
                quote=source,
            )
            raise ExecutionStop
        elif str(group.id) not in await getGroupSetting(GroupList.acgPicture):
            await app.send_group_message(group, MessageChain("抱歉,该群并不允许发色图"))
            raise ExecutionStop

    return Depend(cheakCanAcgpicture)
