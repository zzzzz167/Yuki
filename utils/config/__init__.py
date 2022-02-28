import yaml
from .config import Debug, MiraiApiHttpConfig, BotConfig, Permission


def init_config():
    global CONFIG
    CONFIG = Config("./config/bot.yaml")
    return CONFIG


class Config:
    mirai: MiraiApiHttpConfig
    bot: BotConfig
    permission: Permission

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            config_content = yaml.safe_load(f.read())
        self.mirai = MiraiApiHttpConfig(**config_content["service"])
        self.bot = BotConfig(**config_content["bot"])
        self.permission = Permission(**config_content["Permission"])
        self.debug = Debug(**config_content["Debug"])
