from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from app.db.session import get_engine


def create_app(root_message: str = "Welcome") -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    async def _startup() -> None:
        pass

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await get_engine().dispose()

    @app.middleware("http")
    async def root_response(request: Request, call_next):
        if request.url.path == "/":
            return PlainTextResponse(root_message)
        return await call_next(request)

    return app
