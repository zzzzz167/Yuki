from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member, Friend
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from utils.database.db import addGroupTalk, addFriendTalk

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def savegt(group: Group, member: Member, message: MessageChain):
    await message.download_binary()
    await addGroupTalk(
        group=group.id, qqnum=member.id, msg=message.as_persistent_string()
    )


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def saveft(friend: Friend, message: MessageChain):
    await message.download_binary()
    await addFriendTalk(qqnum=friend.id, msg=message.as_persistent_string())
