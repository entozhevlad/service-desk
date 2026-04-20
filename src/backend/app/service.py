from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from app.db.session import get_engine
from app.metrics import HttpMetricsCollector, resolve_metrics_path


def create_app(root_message: str = "Welcome") -> FastAPI:
    """Создает экземпляр приложения FastAPI."""
    metrics_collector = HttpMetricsCollector()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """Управляет жизненным циклом приложения."""
        yield
        await get_engine().dispose()

    app = FastAPI(lifespan=lifespan)

    @app.middleware("http")
    async def collect_metrics(request: Request, call_next):
        started_at = perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            if request.url.path != "/metrics":
                status_code = (
                    response.status_code if response is not None else 500
                )
                metrics_collector.observe(
                    method=request.method,
                    path=resolve_metrics_path(request),
                    status=str(status_code),
                    duration_seconds=perf_counter() - started_at,
                )

    @app.middleware("http")
    async def root_response(request: Request, call_next):
        if request.url.path == "/":
            return PlainTextResponse(root_message)
        return await call_next(request)

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> PlainTextResponse:
        return PlainTextResponse(
            content=metrics_collector.render(),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    return app
