from pydantic import BaseModel


class MiraiApiHttpConfig(BaseModel):
    host: str = ""
    verify_key: str = ""


class BotConfig(BaseModel):
    account: int
    database: str


class Permission(BaseModel):
    Master: int
    DefaultAcceptInvite: bool
    favor: int
