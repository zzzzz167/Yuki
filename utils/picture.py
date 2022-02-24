from io import BytesIO
from PIL import Image as IMG, ImageFilter, ImageDraw
from utils.QQutils import getAvatar
from utils.text import EmojiWriter

emoji_write = EmojiWriter()


async def getMaskBg(
    qqnum: int,
    nickname: str,
    days: int,
    favor: int,
    text: str,
    pic_size=640,
    avatar_size=300,
):
    info_text = "签 到 成 功"
    tfx = "签到天数: " + str(days) + "  " + "好感度: " + str(favor)
    avatar = IMG.open(BytesIO(await getAvatar(qqnum))).resize(
        (pic_size, pic_size), IMG.ANTIALIAS
    )
    bg = avatar.copy().filter(ImageFilter.GaussianBlur(radius=7))
    # 头像框粘贴
    ab = IMG.open("./source/magic-circle.png").resize(
        map(lambda x: int(x * 7 / 4), (avatar_size - 80, avatar_size - 80)),
        IMG.ANTIALIAS,
    )
    paste_s = int((pic_size - ab.size[0]) / 2)
    bg.paste(ab, (paste_s, paste_s - int(pic_size / 8)), mask=ab)
    # 使用超采样制作圆形mask防抗锯齿
    mask = IMG.new("L", (avatar_size * 3, avatar_size * 3), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size * 3, avatar_size * 3), fill=255)
    mask = mask.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
    # 缩小头像并粘贴
    s_avatar = avatar.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
    paste_point = int((pic_size - avatar_size) / 2)
    bg.paste(s_avatar, (paste_point, paste_point - int(pic_size / 8)), mask=mask)
    # 制作半透明圆角矩形(写字用)
    l, h = 540, 160
    write_bg = IMG.new("RGBA", (l, h), (0, 0, 0, 0))
    color, d = (0, 0, 0, 200), 80
    write_draw = ImageDraw.Draw(write_bg)
    write_draw.ellipse((0, 0, d, d), fill=color)
    write_draw.ellipse((l - d, 0, l, d), fill=color)
    write_draw.ellipse((0, h - d, d, h), fill=color)
    write_draw.ellipse((l - d, h - d, l, h), fill=color)
    write_draw.rectangle((0, d / 2, l, h - d / 2), fill=color)
    write_draw.rectangle((d / 2, 0, l - d / 2, h), fill=color)
    if emoji_write.get_size(nickname, 40)[0] > l:
        dot = emoji_write.get_size("...", 40)[0]
        while emoji_write.get_size(nickname, 40)[0] + dot > l:
            nickname = nickname[:-1]
        nickname += "..."
    pic_name = emoji_write.text2pic(nickname, "#FFFFFF", 40)
    write_bg.paste(pic_name, (int((l - pic_name.size[0]) / 2), 5), mask=pic_name)
    info_pic = emoji_write.text2pic(info_text, "#FFFFFF", 35)
    write_bg.paste(info_pic, (int((l - info_pic.size[0]) / 2), 43), mask=info_pic)
    tfx_pic = emoji_write.text2pic(tfx, "#FFFFFF", 35)
    write_bg.paste(tfx_pic, (int((l - tfx_pic.size[0]) / 2), 79), mask=tfx_pic)
    text_pic = emoji_write.text2pic(text, "#FFFFFF", 33)
    write_bg.paste(text_pic, (int((l - text_pic.size[0]) / 2), 115), mask=text_pic)
    bg.paste(
        write_bg,
        (int((pic_size - l) / 2), int(pic_size / 2 + avatar_size / 2) - 25),
        mask=write_bg,
    )
    b = BytesIO()
    bg.save(b, format="JPEG", quality=99)
    return b.getvalue()
