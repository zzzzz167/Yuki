import time
from utils.database import (
    getGroupSetting,
    getGroup,
    cheakBanList,
    getBanInfo,
    updateBanInfo,
    BanList,
)
from utils.config import init_config
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member, MemberPerm
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
from typing import Union

config = init_config()
favor = config.permission.favor
cd = config.permission.cd


def groupConfigRequire(configKey: str):
    async def cheakGroupConfig(group: Group):
        if str(group.id) not in await getGroupSetting(configKey):
            raise ExecutionStop

    return Depend(cheakGroupConfig)


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


class Permission:
    """
    用于权限管理
    """

    MASTER = 30
    BOT_ADMIN = 20
    GROUP_ADMIN = 10
    USER = 0
    DEFAULT = USER

    @classmethod
    def getPermission(cls, member: Union[Member, int]) -> int:
        """
        得到指定用户的权限

        :param user: 用户实例或QQ号
        :return: 权限等级,整数
        """

        if isinstance(member, Member):
            user = member.id
            userPermisson = member.permission
        elif isinstance(member, int):
            user = member
            userPermisson = cls.DEFAULT
        else:
            raise ExecutionStop

        if user == config.permission.Master:
            return cls.MASTER
        elif user in config.permission.Admin:
            return cls.BOT_ADMIN
        elif userPermisson in [MemberPerm.Administrator, MemberPerm.Owner]:
            return cls.GROUP_ADMIN
        else:
            return cls.DEFAULT

    @classmethod
    def require(cls, level: int = DEFAULT) -> Depend:
        async def permCheck(member: Member):
            member_leve = cls.getPermission(member)
            if member_leve >= level:
                return
            raise ExecutionStop

        return Depend(permCheck)
