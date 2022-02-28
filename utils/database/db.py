import time
from utils.config import init_config
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    BigIntegerField,
    BooleanField,
    IntegerField,
)

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
    GoodMorning = BooleanField(default=True)
    Moyu = BooleanField(default=True)
    acgPicture = BooleanField(default=True)
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


db.create_tables([GroupUserTalk], safe=True)
db.create_tables([FriendTalk], safe=True)
db.create_tables([GroupList], safe=True)
db.create_tables([User], safe=True)


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


async def addGroup(id, name):
    ag = GroupList(group_id=id, group_name=name)
    ag.save()


async def getGroupSetting(set: BooleanField) -> list:
    gs = GroupList().select().where(set == 1)
    gs_r = []
    for j in gs:
        gs_r.append(j.group_id)
    return gs_r


async def updataGroup(groupnum: int, change: dict):
    gs = GroupList.update(change).where(GroupList.group_id == str(groupnum))
    gs.execute()


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
