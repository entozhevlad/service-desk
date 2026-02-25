from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ проверки состояния сервиса."""
    status: str

