from datetime import datetime, timezone
from importlib import import_module
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.tickets.dependencies import get_service_desk
from app.api.tickets.schemas import Ticket
from app.db.types import TicketPriority, TicketStatus
from app.routers import all_routers
from app.service import create_app


def make_ticket(ticket_id: int = 1) -> Ticket:
    now = datetime.now(timezone.utc)
    return Ticket(
        id=ticket_id,
        title=f"ticket-{ticket_id}",
        description="desc",
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
        created_at=now,
        updated_at=now,
    )


def create_test_client(monkeypatch, service_desk_mock: AsyncMock) -> TestClient:
    monkeypatch.setenv("POSTGRES_USER", "service_desk")
    monkeypatch.setenv("POSTGRES_PASSWORD", "service_desk")
    monkeypatch.setenv("POSTGRES_DB", "service_desk")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    app = create_app("Service Desk Backend")
    for router in all_routers:
        app.include_router(router)
    app.dependency_overrides[get_service_desk] = lambda: service_desk_mock

    return TestClient(app)


def test_root_and_healthz_endpoints(monkeypatch) -> None:
    service_desk_mock = AsyncMock()

    with create_test_client(monkeypatch, service_desk_mock) as client:
        root_response = client.get("/")
        health_response = client.get("/healthz")

    assert root_response.status_code == 200
    assert root_response.text == "Service Desk Backend"
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}


def test_create_ticket_endpoint(monkeypatch) -> None:
    service_desk_mock = AsyncMock()
    created_ticket = make_ticket(10)
    service_desk_mock.create_ticket.return_value = created_ticket

    with create_test_client(monkeypatch, service_desk_mock) as client:
        response = client.post(
            "/ticket",
            json={"title": "printer", "description": "jammed"},
        )

    assert response.status_code == 200
    assert response.json()["id"] == created_ticket.id
    service_desk_mock.create_ticket.assert_awaited_once()


def test_get_ticket_endpoint_returns_404(monkeypatch) -> None:
    service_desk_mock = AsyncMock()
    service_desk_mock.get_ticket.return_value = None

    with create_test_client(monkeypatch, service_desk_mock) as client:
        response = client.get("/tickets/404")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket_endpoint_validates_payload(monkeypatch) -> None:
    service_desk_mock = AsyncMock()

    with create_test_client(monkeypatch, service_desk_mock) as client:
        response = client.put("/tickets/1", json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_update_ticket_endpoint_returns_404(monkeypatch) -> None:
    service_desk_mock = AsyncMock()
    service_desk_mock.update_ticket.return_value = None

    with create_test_client(monkeypatch, service_desk_mock) as client:
        response = client.put("/tickets/1", json={"title": "updated"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket_endpoint_returns_ticket(monkeypatch) -> None:
    service_desk_mock = AsyncMock()
    updated_ticket = make_ticket(2)
    updated_ticket.title = "updated"
    service_desk_mock.update_ticket.return_value = updated_ticket

    with create_test_client(monkeypatch, service_desk_mock) as client:
        response = client.put("/tickets/2", json={"title": "updated"})

    assert response.status_code == 200
    assert response.json()["title"] == "updated"


def test_list_tickets_endpoint(monkeypatch) -> None:
    service_desk_mock = AsyncMock()
    service_desk_mock.list_tickets.return_value = [make_ticket(1), make_ticket(2)]

    with create_test_client(monkeypatch, service_desk_mock) as client:
        response = client.get("/tickets")

    assert response.status_code == 200
    assert [ticket["id"] for ticket in response.json()] == [1, 2]


def test_delete_ticket_endpoint_success_and_404(monkeypatch) -> None:
    service_desk_mock = AsyncMock()
    service_desk_mock.delete_ticket.side_effect = [True, False]

    with create_test_client(monkeypatch, service_desk_mock) as client:
        success_response = client.delete("/tickets/5")
        missing_response = client.delete("/tickets/6")

    assert success_response.status_code == 200
    assert success_response.json() == {"id": 5, "message": "Ticket deleted"}
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Ticket not found"


def test_get_service_desk_factory_returns_service_instance() -> None:
    session = object()

    service = get_service_desk(session=session)

    assert service._session is session


def test_app_main_registers_routes() -> None:
    module = import_module("app.main")
    paths = {route.path for route in module.app.routes}

    assert "/healthz" in paths
    assert "/ticket" in paths
    assert "/tickets" in paths
