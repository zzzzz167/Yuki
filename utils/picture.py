from io import BytesIO
from PIL import Image as IMG, ImageFilter, ImageDraw, ImageFont
from utils.QQutils import getAvatar


async def getMaskBg(
    qqnum: int,
    pic_size=640,
    avatar_size=300,
):
    word_ttf = ImageFont.truetype('./source/font/T1.ttf', 40)
    avatar = IMG.open(BytesIO(await getAvatar(qqnum))).resize(
        (pic_size, pic_size), IMG.ANTIALIAS)
    bg = avatar.copy().filter(ImageFilter.GaussianBlur(radius=7))
    # 头像框粘贴
    ab = IMG.open("./source/magic-circle.png").resize(
        map(lambda x: int(x * 7 / 4), (avatar_size - 80, avatar_size - 80)),
        IMG.ANTIALIAS)
    paste_s = int((pic_size - ab.size[0]) / 2)
    bg.paste(ab, (paste_s, paste_s - int(pic_size / 8)), mask=ab)
    # 使用超采样制作圆形mask防抗锯齿
    mask = IMG.new('L', (avatar_size * 3, avatar_size * 3), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size * 3, avatar_size * 3),
                                 fill=255)
    mask = mask.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
    # 缩小头像并粘贴
    s_avatar = avatar.resize((avatar_size, avatar_size), IMG.ANTIALIAS)
    paste_point = int((pic_size - avatar_size) / 2)
    bg.paste(s_avatar, (paste_point, paste_point - int(pic_size / 8)),
             mask=mask)
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
    write_draw.text((50, 52), "等级:test", font=word_ttf)
    bg.paste(write_bg, (int(
        (pic_size - l) / 2), int(pic_size / 2 + avatar_size / 2) - 25),
             mask=write_bg)
    b = BytesIO()
    bg.save(b, format='JPEG', quality=99)
    return b.getvalue()
