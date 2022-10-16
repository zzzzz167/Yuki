from fastapi.responses import ORJSONResponse
from utils.fastapiService.responseModel import GeneralResponse
from utils.fastapiService.router import Route as OriginRoute
from .group import get_group_list


class Route(OriginRoute):
    kwargs: dict = {"response_class": ORJSONResponse}


routes: list[OriginRoute] = [
    Route(
        path="/api/get_group_list",
        endpoint=get_group_list,
        response_model=GeneralResponse,
    )
]
