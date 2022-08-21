import os
import imgkit
import hashlib
from loguru import logger

options = {"quiet": "", "encoding": "utf-8"}


def textToImg(text: str, force: bool = False, width: int = 512) -> str:
    """
    非常暴力的图转文 -> 返回生成文件地址
    text: 转化的内容
    force: 是否强制居左
    width: 图片宽度
    """

    path = "./cache/img/"
    options["width"] = str(width)
    sentenceList = text.split("\n")
    saveName = path + hashlib.md5(text.encode("utf8")).hexdigest() + ".jpg"
    if not os.path.exists(path):
        os.mkdir(path)

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
