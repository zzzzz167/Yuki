import aiohttp


async def getHitokoto():  # aiohttp必须放在异步函数中使用
    async with aiohttp.request('GET',
                               "https://v1.hitokoto.cn/?encode=text") as resp:
        return await resp.text()
