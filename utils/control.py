from utils.config import init_config

config = init_config("./config/bot.yaml")


class Permission:

    Master = 100
    GROUP_ADMIN = 20
    USER = 10
    BANNED = 0
    DEFAULT = USER
