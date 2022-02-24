import datetime
from datetime import timedelta


def caltime(today: datetime.datetime, target):
    targetD = datetime.datetime.strptime(target, "%Y-%m-%d")
    return (targetD - today).days


def retWeekend():
    """
    返回最近的一个周六
    """
    now = datetime.datetime.now()
    this_week_end = now + timedelta(days=6 - now.weekday())
    return this_week_end.strftime("%Y-%m-%d")


def getWeekday(date: datetime.datetime):
    week_map = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
    week = date.weekday()
    dataf = date.strftime("%Y-%m-%d")
    return f"{dataf} 星期{week_map[week]}"


async def getMoyuMsg() -> str:
    today = datetime.datetime.now()
    holidays = [
        ["周末", retWeekend()],
        ["test", "2022-1-23"],
        ["清明节", "2022-04-05"],
        ["劳动节", "2022-05-01"],
        ["端午节", "2022-06-03"],
        ["中秋节", "2022-09-10"],
        ["国庆节", "2022-10-01"],
        ["程序员节", "2022-10-24"],
        ["元旦", "2023-01-01"],
        ["春节", "2023-01-22"],
        ["情人节", "2023-02-14"],
    ]
    tl = []
    for i in holidays:
        tgDays = caltime(today, i[1])
        if tgDays > 0:
            tl.append(f"距离{i[0]}假期还有{caltime(today, i[1])}天")
    str1 = f"「摸鱼办」提醒您:\n今天是{getWeekday(today)},上午好,摸鱼人! 工作再累，一定不要忘记摸鱼哦！有事没事起身去茶水间，去厕所，去廊道走走别老在工位上坐着，钱是老板的,但命是自己的。"
    str2 = "\n".join(tl[:4])
    str3 = "\n上班是帮老板赚钱，摸鱼是赚老板的钱! 最后，祝愿天下所有摸鱼人，都能愉快的渡过每一天…"
    return str1 + str2 + str3
