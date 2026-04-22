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

---

## Kubernetes (Helm)

Для backend добавлен Helm chart: `helm/service-desk-backend`.

### Как собрать и запушить image

Локально:

```bash
export REGISTRY_HOST=cr.example.com
export REGISTRY_USER=svc_service_desk
export REGISTRY_PASSWORD=***REDACTED***
export BACKEND_IMAGE_REPOSITORY=cr.example.com/team/service-desk-backend
export FRONTEND_IMAGE_REPOSITORY=cr.example.com/team/service-desk-frontend

docker login "$REGISTRY_HOST" -u "$REGISTRY_USER" -p "$REGISTRY_PASSWORD"
docker build -f src/backend/Dockerfile -t "$BACKEND_IMAGE_REPOSITORY:$(git rev-parse HEAD)" src/backend
docker push "$BACKEND_IMAGE_REPOSITORY:$(git rev-parse HEAD)"
docker build -f src/frontend/Dockerfile --build-arg VITE_API_BASE_URL=/api -t "$FRONTEND_IMAGE_REPOSITORY:$(git rev-parse HEAD)" src/frontend
docker push "$FRONTEND_IMAGE_REPOSITORY:$(git rev-parse HEAD)"
```

Через GitHub Actions (jobs `backend-image-publish` и
`frontend-image-publish`):

- `vars.REGISTRY_HOST` — адрес registry
- `vars.BACKEND_IMAGE_REPOSITORY` — полный путь до backend image
- `vars.FRONTEND_IMAGE_REPOSITORY` — полный путь до frontend image
- `secrets.REGISTRY_USERNAME` — пользователь registry
- `secrets.REGISTRY_PASSWORD` — пароль/token registry

Тег образа выставляется как полный `github.sha` (воспроизводимый tag).

### Как установить chart

```bash
kubectl create namespace service-desk

helm upgrade --install service-desk-backend ./helm/service-desk-backend \
  --namespace service-desk \
  --set image.repository="$BACKEND_IMAGE_REPOSITORY" \
  --set image.tag="$(git rev-parse HEAD)"
```

Если используется приватный registry, сначала создайте pull secret:

```bash
kubectl create secret docker-registry regcred \
  --namespace service-desk \
  --docker-server="$REGISTRY_HOST" \
  --docker-username="$REGISTRY_USER" \
  --docker-password="$REGISTRY_PASSWORD"
```

И передайте его в chart:

```bash
helm upgrade --install service-desk-backend ./helm/service-desk-backend \
  --namespace service-desk \
  --set image.repository="$BACKEND_IMAGE_REPOSITORY" \
  --set image.tag="$(git rev-parse HEAD)" \
  --set imagePullSecrets[0].name=regcred
```

Для чувствительных переменных backend (`POSTGRES_PASSWORD`,
`DATABASE_URL`) используйте отдельный Kubernetes Secret и передавайте
его имя через `existingSecretName`:

```bash
kubectl create secret generic service-desk-backend-env \
  --namespace service-desk \
  --from-literal=POSTGRES_PASSWORD='change-me'

helm upgrade --install service-desk-backend ./helm/service-desk-backend \
  --namespace service-desk \
  --set image.repository="$BACKEND_IMAGE_REPOSITORY" \
  --set image.tag="$(git rev-parse HEAD)" \
  --set existingSecretName=service-desk-backend-env
```

### Как обновить chart

```bash
helm upgrade service-desk-backend ./helm/service-desk-backend \
  --namespace service-desk \
  --reuse-values \
  --set image.tag="<new-sha-or-tag>"
```

### Как проверить pods/services/hpa

```bash
kubectl get pods -n service-desk
kubectl get svc -n service-desk
kubectl get hpa -n service-desk
kubectl describe hpa service-desk-backend -n service-desk
```

### Как проверить, что HPA масштабирует backend

1. Убедитесь, что в кластере установлен `metrics-server`.
2. Проверьте текущее состояние:

```bash
kubectl get hpa service-desk-backend -n service-desk -w
```

3. Параллельно подайте нагрузку (пример ниже).  
4. Проверьте рост реплик:

```bash
kubectl get deploy service-desk-backend -n service-desk
```

### Как подать нагрузку для демонстрации

```bash
kubectl run loadgen \
  --namespace service-desk \
  --rm -it --restart=Never \
  --image=rakyll/hey \
  -- -z 3m -c 100 http://service-desk-backend:8000/healthz
```

### Frontend в Kubernetes и доступ извне

Для frontend добавлен отдельный chart `helm/service-desk-frontend`.

```bash
helm upgrade --install service-desk-frontend ./helm/service-desk-frontend \
  --namespace service-desk \
  --set image.repository="$FRONTEND_IMAGE_REPOSITORY" \
  --set image.tag="$(git rev-parse HEAD)"
```

По умолчанию chart поднимает `NodePort` сервис на `30081`.
Если у ВМ открыт порт, сайт доступен снаружи:

```text
http://<VM_PUBLIC_IP>:30081
```

Убедитесь, что в security group/фаерволе ВМ разрешен входящий TCP на `30081`.

### Prometheus + Grafana через Helm

Для учебного стенда добавлен lightweight chart
`helm/service-desk-monitoring` (Prometheus + Grafana).

```bash
helm upgrade --install service-desk-monitoring ./helm/service-desk-monitoring \
  --namespace service-desk \
  --set-string prometheus.backendTarget=service-desk-backend.service-desk.svc.cluster.local:8000 \
  --set-string grafana.adminPassword='<change-me>'
```

Проверка:

```bash
kubectl get pods -n service-desk
kubectl get svc -n service-desk
```

Grafana по умолчанию публикуется как `NodePort` `30300`:

```text
http://<VM_PUBLIC_IP>:30300
```

Убедитесь, что во внешнем фаерволе/SG открыт TCP порт `30300`.

Логин: `admin`, пароль: значение `grafana.adminPassword`.

### Метрики и дашборд по заявкам

Backend отдает метрики на `GET /metrics`.
В chart мониторинга уже предзагружен dashboard
`Service Desk Backend Overview` с панелями:

- общий RPS
- RPS создания заявок (`POST /ticket`)
- количество созданных заявок за последний час
- 5xx RPS

Примеры PromQL:

```promql
sum(rate(http_requests_total[1m]))
sum(rate(http_requests_total{handler="/ticket",method="POST",status=~"2.."}[5m]))
sum(increase(http_requests_total{handler="/ticket",method="POST",status=~"2.."}[1h]))
sum(rate(http_requests_total{status=~"5.."}[5m]))
```

Для лабы dashboard по созданию заявок обычно не обязателен, но это сильный
плюс на защите: видно и бизнес-метрику, и техническое состояние API.
