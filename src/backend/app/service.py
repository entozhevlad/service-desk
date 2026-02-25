from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from app.db.session import get_engine


def create_app(root_message: str = "Welcome") -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await get_engine().dispose()

    app = FastAPI(lifespan=lifespan)

    @app.middleware("http")
    async def root_response(request: Request, call_next):
        if request.url.path == "/":
            return PlainTextResponse(root_message)
        return await call_next(request)

    return app
