import aiohttp


async def getAvatar(qqunm: int) -> bytes:  # aiohttp必须放在异步函数中使用
    async with aiohttp.request(
        "GET", "https://q2.qlogo.cn/headimg_dl?dst_uin=%s&spec=640" % str(qqunm)
    ) as resp:
        return await resp.read()
