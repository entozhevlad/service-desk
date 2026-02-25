# service-desk

# Mini Service Desk

Мини-сервисдеск — это веб-приложение для регистрации и обработки обращений пользователей (тикетов).  
Система позволяет создавать, отслеживать и управлять статусами обращений через удобный веб-интерфейс.

---

## Описание проекта

Mini Service Desk — fullstack-приложение, состоящее из backend API и frontend-клиента.

Пользователь может:

- создавать обращения
- редактировать описание
- менять статус и приоритет
- назначать исполнителя
- искать и фильтровать тикеты
- удалять обращения

Приложение построено по принципу разделения frontend и backend и взаимодействует через REST API.

---

## Технологический стек

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL

### Frontend

- Vue 3

### Инфраструктура

- Docker
- Docker Compose
- Kubernetes

---


## Архитектура

Клиент-серверная архитектура:

- **Backend** — FastAPI (REST API)
- **Frontend** — Vue 3 (SPA)
- **Database** — PostgreSQL

Обмен данными осуществляется по HTTP в формате JSON.

---

##  API

### Создание тикета

    POST /ticket

### Получение списка тикетов

    GET /tickets

### Получение одного тикета

    GET /tickets/{id}

### Обновление тикета

    PUT /tickets/{id}

### Удаление тикета

    DELETE /tickets/{id}

---

##  Frontend

Frontend будет реализован как одностраничное приложение (SPA).

Основной экран:

- таблица тикетов
- фильтрация по статусу и приоритету
- кнопка создания тикета
- редактирование
- удаление
- изменение статуса через select

Дополнительно может быть реализован экран детального просмотра тикета.

---

## Тестирование

### Backend

- pytest
- тестирование CRUD операций
- проверка валидации данных
- проверка изменения статуса
- проверка 404 после удаления

### Frontend

- Vitest
- тестирование service-слоя (корректность HTTP-запросов)

---

## Структура проекта

    service-desk/
    │
    ├── src/
    │   └── backend/
    │       ├── app/
    │       │   ├── api/
    │       │   │   ├── healthz/
    │       │   │   └── tickets/
    │       │   ├── db/
    │       │   │   ├── migrations/
    │       │   │   ├── base.py
    │       │   │   ├── models.py
    │       │   │   └── session.py
    │       │   ├── main.py
    │       │   ├── routers.py
    │       │   └── service.py
    │       ├── tests/
    │       │   ├── integrations/
    │       │   └── unit/
    │       ├── alembic.ini
    │       └── pyproject.toml
    │
    ├── tools/
    │   └── postman/
    │       └── smoke.postman_collection.json
    │
    └── docker-compose.yaml
