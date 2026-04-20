from fastapi.testclient import TestClient

from app.service import create_app


def test_metrics_endpoint_returns_prometheus_metrics(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_USER", "service_desk")
    monkeypatch.setenv("POSTGRES_PASSWORD", "service_desk")
    monkeypatch.setenv("POSTGRES_DB", "service_desk")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    app = create_app()

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"status": "ok"}

    with TestClient(app) as client:
        ping_response = client.get("/ping")
        assert ping_response.status_code == 200

        metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "http_requests_total" in metrics_response.text
    assert 'method="GET",path="/ping",status="200"' in metrics_response.text
    assert "http_request_duration_seconds" in metrics_response.text
