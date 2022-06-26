import aiohttp


async def getHitokoto() -> str:  # aiohttp必须放在异步函数中使用
    async with aiohttp.request("GET", "https://v1.hitokoto.cn/?encode=text") as resp:
        return await resp.text()


async def getAppointHitokoto(**val) -> str:
    url = "https://v1.hitokoto.cn/?encode=text"
    if "c" in val.keys():
        url += "&c=%s" % str(val["c"])
    if "min_length" in val.keys():
        url += "&min_length=%s" % str(val["min_length"])
    if "max_length" in val.keys():
        url += "&max_length=%s" % str(val["max_length"])
    async with aiohttp.request("GET", url) as resp:
        return await resp.text()


async def getJsonHitokoto(**val):
    url = "https://v1.hitokoto.cn/?encode=json"
    if "c" in val.keys():
        url += "&c=%s" % str(val["c"])
    if "min_length" in val.keys():
        url += "&min_length=%s" % str(val["min_length"])
    if "max_length" in val.keys():
        url += "&max_length=%s" % str(val["max_length"])
    async with aiohttp.request("GET", url) as resp:
        return await resp.json()
