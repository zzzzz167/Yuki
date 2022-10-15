import traceback
from io import StringIO
from utils.config import init_config
from utils.text2img import markdownToImg
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.util.saya import listen
from graia.broadcast.builtin.event import ExceptionThrowed
from graia.ariadne.event.message import GroupMessage
from graia.saya import Channel

channel = Channel.current()
masterNumber = init_config().permission.Master


@listen(ExceptionThrowed)
async def except_handle(event: ExceptionThrowed):
    if isinstance(event.event, ExceptionThrowed):
        return
    app = Ariadne.current()
    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()

        msg = f"""\
## 异常事件:
{str(event.event.__repr__())}
## 异常类型:
`{type(event.exception)}`
## 异常内容:
{str(event.exception)}
## 异常追踪:
```py
{tb}
```

"""

    await app.send_friend_message(
        masterNumber,
        MessageChain(Plain("发生了咩有捕获的异常捏"), Image(path=await markdownToImg(msg))),
    )


@listen(GroupMessage)
async def error_handler_test(msg: MessageChain):
    if str(msg) == ".错误捕捉测试":
        raise ValueError("错误捕捉测试")
