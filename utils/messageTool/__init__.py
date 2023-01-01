from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain, At


async def moreFriendlyEscape(
    app: Ariadne, msg: MessageChain, group: Group
) -> MessageChain:
    for i in msg[At]:
        at_member = await app.get_member(group, i.target)
        at_name = at_member.name
        msg = msg.replace(i, "@" + at_name)
    return msg
