import aiohttp


async def getHitokoto() -> str:  # aiohttp必须放在异步函数中使用
    async with aiohttp.request("GET", "https://v1.hitokoto.cn/?encode=text") as resp:
        return await resp.text()


def hitokotoUrl(url, val):
    if "c" in val.keys():
        url += "&c=%s" % str(val["c"])
    if "min_length" in val.keys():
        url += "&min_length=%s" % str(val["min_length"])
    if "max_length" in val.keys():
        url += "&max_length=%s" % str(val["max_length"])
    return url


async def getAppointHitokoto(**val) -> str:
    url = "https://v1.hitokoto.cn/?encode=text"
    async with aiohttp.request("GET", hitokotoUrl(url, val)) as resp:
        return await resp.text()


async def getJsonHitokoto(**val):
    url = "https://v1.hitokoto.cn/?encode=json"
    async with aiohttp.request("GET", hitokotoUrl(url, val)) as resp:
        return await resp.json()
