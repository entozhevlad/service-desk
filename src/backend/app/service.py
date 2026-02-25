from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from app.db.client import db, has_database_url


def create_app(root_message: str = "Welcome") -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    async def _startup() -> None:
        if has_database_url():
            await db.connect()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await db.disconnect()

    @app.middleware("http")
    async def root_response(request: Request, call_next):
        if request.url.path == "/":
            return PlainTextResponse(root_message)
        return await call_next(request)

    return app
