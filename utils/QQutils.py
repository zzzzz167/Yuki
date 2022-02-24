import aiohttp


async def getAvatar(qqunm: int) -> bytes:  # aiohttp必须放在异步函数中使用
    async with aiohttp.request(
        "GET", "http://q1.qlogo.cn/g?b=qq&nk=%s&s=640" % str(qqunm)
    ) as resp:
        return await resp.read()
