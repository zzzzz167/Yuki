import os
import imgkit
import hashlib
import markdown
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from utils.browser import get_new_page
from graia.ariadne.util.async_exec import io_bound

exts = [
    "markdown.extensions.extra",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
]
CACHEPATH = "./cache/"
TEMPLATEPATH = './source/htmlTemplate/'
env = Environment(loader=FileSystemLoader(TEMPLATEPATH))


@io_bound
def textToImg(text: str, force: bool = False, width: int = 512) -> str:
    """
    非常暴力的图转文 -> 返回生成文件地址
    text: 转化的内容
    force: 是否强制居左
    width: 图片宽度
    """

    cachePath = CACHEPATH + 'img/'
    options = {"quiet": "", "encoding": "utf-8", "width": str(width)}
    sentenceList = text.split("\n")
    saveName = cachePath + hashlib.md5(text.encode("utf8")).hexdigest() + ".jpg"
    if not os.path.exists(cachePath):
        os.mkdir(cachePath)

    if os.path.exists(saveName):
        logger.info(f"Img-hash hit in {saveName}")
        return saveName

    align = "text-align: center;"

    for i in range(len(sentenceList)):
        if force:
            align = "text-align: left;"
        else:
            if len(sentenceList[i]) >= 30:
                align = "text-align: left;"

        if sentenceList[i] == "":
            sentenceList[i] = "<br>"
        else:
            sentenceList[i] = sentenceList[i].replace("<", "&lt;")
            sentenceList[i] = (
                "<div style='white-space: pre-wrap;'>" + sentenceList[i] + "</div>"
            )
    sen = "".join(sentenceList)
    imgkit.from_string(
        f'<div style="word-wrap: break-word;{align}">{sen}</div>',
        saveName,
        options=options,
    )
    return saveName


async def markdownToImg(mdText: str, cssName: str = "github") -> str:
    temOp = {"cssName": cssName, "content": ""}
    temOp["content"] = markdown.markdown(mdText, extensipns=exts)
    saveName = await templateToImg("mdTemplate.html", temOp, viewport={'width': 800, 'height': 10})
    return saveName


async def templateToImg(templateName: str, templateOptions: dict, wait: int = 0, fource: bool = False, **browserOptin) -> str:
    template = env.get_template(templateName)
    imgCache = CACHEPATH + "img/"
    templateOptions['path'] = os.getcwd()

    if not os.path.exists(imgCache):
        os.mkdir(imgCache)

    out = template.render(**templateOptions)
    templateMD5 = hashlib.md5(out.encode('utf-8')).hexdigest()

    imgSaveName = imgCache + templateMD5 + ".jpg"

    if os.path.exists(imgSaveName) and not fource:
        logger.info(f"Img-hash hit in {imgSaveName}")
        return imgSaveName

    async with get_new_page(**browserOptin) as page:
        await page.goto(f"file://{templateOptions['path']}/source/htmlTemplate/")
        await page.set_content(out, wait_until="networkidle")
        await page.wait_for_timeout(wait)
        await page.screenshot(full_page=True, path=imgSaveName)
    return imgSaveName
