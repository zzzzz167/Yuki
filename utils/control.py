import time
from utils.database.db import (
    getGroupSetting,
    getGroup,
    GroupList,
    cheakBanList,
    getBanInfo,
    updateBanInfo,
    BanList
)
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop

config = init_config()
favor = config.permission.favor
cd = config.permission.cd


def cheakAcgpicture():
    async def cheakCanAcgpicture(app: Ariadne, group: Group, source: Source):
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


def cheakBan():
    async def cheakAreBan(app: Ariadne, group: Group, source: Source, member: Member):
        if await cheakBanList(member.id):
            info = await getBanInfo(member.id)
            if info.warn_today is False:
                timeArray = time.localtime(info.start_time)
                sTimeStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                await app.send_group_message(
                    group,
                    MessageChain(
                        f"该账户(ID:{info.qq_id})已被列入黑名单\n封禁开始时间: {sTimeStr}\n封禁总时间:{info.ban_days}天\n封禁原因:{info.ban_tip}\n注:你每天只能看见该消息一次"
                    ),
                    quote=source,
                )
                await updateBanInfo(member.id, {BanList.warn_today: True})
                raise ExecutionStop
            else:
                raise ExecutionStop

    return Depend(cheakAreBan)
