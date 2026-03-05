# Organizations Directory API (FastAPI + PostgreSQL)

Тестовое REST API для справочника организаций, зданий и деятельностей.

## Что реализовано

- FastAPI + Pydantic + SQLAlchemy + Alembic.
- PostgreSQL как основная БД.
- Статический API ключ для всех бизнес-методов (`X-API-Key`).
- Миграции и тестовые данные.
- Dockerfile + docker-compose для запуска на любой машине.
- Swagger UI (`/docs`) и ReDoc (`/redoc`).
- Пагинация (`limit` / `offset`) для списочных методов.
- Health-check сервиса и БД (`/health`, `/health/db`).

## Модель данных

- `buildings`: адрес + координаты.
- `activities`: дерево деятельностей с ограничением глубины до 3 уровней (`level` + ограничения БД).
- `organizations`: карточка организации, привязка к одному зданию.
- `organization_phones`: несколько телефонов для одной организации.
- `organization_activity`: связь many-to-many между организациями и деятельностями.

## Запуск через Docker Compose

```bash
docker compose up --build
```

При старте API-сервиса автоматически выполняются:

- `alembic upgrade head`
- `python -m app.db.seed`
- запуск `uvicorn`

После запуска:

- API: <http://localhost:8000>
- Swagger: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health DB: <http://localhost:8000/health/db>

## API ключ

Во все запросы к `/api/*` нужно передавать заголовок:

```http
X-API-Key: super-secret-api-key
```

## Основные эндпоинты

- `GET /api/buildings` - список зданий.
- `GET /api/buildings/{building_id}` - здание по ID.
- `GET /api/activities` - список деятельностей.
- `GET /api/activities/{activity_id}` - деятельность по ID.
- `GET /api/organizations/by-building/{building_id}` - организации в здании.
- `GET /api/organizations/by-activity/{activity_id}` - организации по конкретной деятельности.
- `GET /api/organizations/by-activity-tree/{activity_id}` - организации по деятельности с учетом дочерних узлов.
- `GET /api/organizations/geo/radius?latitude=...&longitude=...&radius_km=...` - организации в радиусе.
- `GET /api/organizations/geo/box?min_lat=...&max_lat=...&min_lon=...&max_lon=...` - организации в прямоугольнике.
- `GET /api/organizations/search?q=...` - поиск по названию.
- `GET /api/organizations/{organization_id}` - карточка организации.

## Пагинация

Для списочных методов можно передавать:

- `limit` (по умолчанию `100`, максимум `500`)
- `offset` (по умолчанию `0`)

## Быстрая проверка cURL

```bash
curl -H "X-API-Key: super-secret-api-key" http://localhost:8000/api/buildings
curl -H "X-API-Key: super-secret-api-key" http://localhost:8000/api/activities
curl -H "X-API-Key: super-secret-api-key" "http://localhost:8000/api/organizations/search?q=Еда"
curl -H "X-API-Key: super-secret-api-key" "http://localhost:8000/api/organizations/by-activity-tree/<activity_uuid>"
curl -H "X-API-Key: super-secret-api-key" "http://localhost:8000/api/organizations/by-building/<building_uuid>?limit=2&offset=0"
```

## Локальный запуск без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```
