import time
import json
from utils.config import init_config
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    BigIntegerField,
    BooleanField,
    IntegerField,
)

day_sec = 86400
config = init_config()
db = SqliteDatabase(config.bot.database)


class BaseModel(Model):
    class Meta:
        database = db


class GroupUserTalk(BaseModel):
    """
    群组聊天记录
    """

    group = CharField()
    qqnum = CharField()
    savetime = BigIntegerField()
    msg = CharField()

    class Meta:
        table_name = "GroupUserTalk"


class FriendTalk(BaseModel):
    """
    私聊记录
    """

    qqnum = CharField()
    savetime = BigIntegerField()
    msg = CharField()


class GroupList(BaseModel):
    """
    群组列表与设置
    """

    group_id = CharField()
    group_name = CharField()
    config = CharField()
    acgPictureUse = BigIntegerField(default=0)


class User(BaseModel):
    """
    用户数据
    """

    qq_id = CharField()
    qq_name = CharField()
    favor = IntegerField(default=20)
    days = IntegerField(default=0)
    today = BooleanField(default=False)
    picture = IntegerField(default=0)

    class Meta:
        table_name = "UserInfo"


class BanList(BaseModel):
    """
    黑名单列表,我实在忍不下去了
    """

    qq_id = CharField()
    ban_days = CharField()
    ban_tip = CharField()
    start_time = BigIntegerField(default=0)
    warn_today = BooleanField(default=False)

    class Meta:
        table_name = "BanList"


db.create_tables([GroupUserTalk], safe=True)
db.create_tables([FriendTalk], safe=True)
db.create_tables([GroupList], safe=True)
db.create_tables([User], safe=True)
db.create_tables([BanList], safe=True)


async def addGroupTalk(group, qqnum, msg):
    gt = GroupUserTalk(group=group, qqnum=qqnum, msg=msg, savetime=(time.time()))
    gt.save()


async def addFriendTalk(qqnum, msg):
    ft = FriendTalk(qqnum=qqnum, msg=msg, savetime=int(time.time()))
    ft.save()


async def getGroupList() -> list:
    GroupList_d = GroupList().select()
    GroupList_s = []
    for i in GroupList_d:
        GroupList_s.append(i.group_id)
    return GroupList_s


async def addGroup(id, name, config):
    ag = GroupList(group_id=id, group_name=name, config=config)
    ag.save()


async def getGroupSetting(set: str) -> list:
    gs = GroupList().select()
    gs_r = []
    for j in gs:
        groupConfig = json.loads(j.config)
        if not groupConfig['power']:
            continue

        if set not in groupConfig.keys():
            continue

        if groupConfig[set]:
            gs_r.append(j.group_id)

    return gs_r


async def updataGroup(groupnum: int, change: dict):
    gs = GroupList.update(change).where(GroupList.group_id == str(groupnum))
    gs.execute()


async def changeGroupSet(groupnum: int, configKey: str, switch: bool):
    group = await getGroup(groupnum)
    oldConfig = json.loads(group.config)
    oldConfig.update({configKey: switch})
    newConfig = json.dumps(oldConfig)
    await updataGroup(groupnum, {GroupList.config: newConfig})


async def getGroup(groupnum: int) -> GroupList:
    gb = GroupList.get(GroupList.group_id == str(groupnum))
    return gb


async def addUser(id, nickName):
    au = User(qq_id=id, qq_name=nickName)
    au.save()


async def getAllUser() -> list:
    UserList_d = User().select()
    UserList_s = []
    for i in UserList_d:
        UserList_s.append(i.qq_id)
    return UserList_s


async def getUser(qqnum: int) -> User:
    us = User.get(User.qq_id == str(qqnum))
    return us


async def updataUser(qqnum: int, change: dict):
    us = User.update(change).where(User.qq_id == str(qqnum))
    us.execute()


async def reset_sign():
    User.update(today=False).where(User.today).execute()
    return


async def addBanList(
    qqnum: int, ban_days: int, start_time: int, ban_tip: str = "自己了干什么心里没点数是吧"
):
    ab = BanList(qq_id=qqnum, ban_days=ban_days, start_time=start_time, ban_tip=ban_tip)
    ab.save()


async def delBanList(qqnum: int):
    BanList.delete().where(BanList.qq_id == str(qqnum)).execute()


async def cheakBanList(qqnum: int) -> bool:
    ret = BanList.select().where(BanList.qq_id == str(qqnum))
    if ret.exists():
        return True
    else:
        return False


async def getBanInfo(qqnum: int) -> BanList:
    bi = BanList.get(BanList.qq_id == str(qqnum))
    return bi


async def updateBanInfo(qqnum: int, change: dict):
    ub = BanList.update(change).where(BanList.qq_id == str(qqnum))
    ub.execute()


async def resetBanList():
    BanList.update(warn_today=False).where(BanList.warn_today).execute()
    BanList_d = BanList().select()
    for i in BanList_d:
        now = time.time()
        if now - int(i.start_time) >= day_sec * int(i.ban_days):
            await delBanList(i.qq_id)
    return
