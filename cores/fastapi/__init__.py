from fastapi import FastAPI
from graia.amnesia.transport.common.asgi import ASGIHandlerProvider
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from utils.fastapiService.router import Router
from loguru import logger
from .api import routes

channel = Channel.current()


async def root():
    return {"message": "Hello World"}


@listen(ApplicationLaunched)
async def init(app: Ariadne):
    mgr = app.launch_manager
    asgi: FastAPI = mgr.get_interface(ASGIHandlerProvider).get_asgi_handler()
    logger.info("Add some api routes...")
    asgi.add_api_route("/", endpoint=root, methods=["GET"])

    for route in routes:
        asgi.add_api_route(
            path=route.path,
            methods=route.methods,
            endpoint=route.endpoint,
            response_model=route.response_model,
            **route.kwargs,
        )

    for route in Router.routes:
        asgi.add_api_route(
            path=route.path,
            methods=route.methods,
            endpoint=route.endpoint,
            response_model=route.response_model,
            **route.kwargs,
        )

    logger.info("Api routes add done")
