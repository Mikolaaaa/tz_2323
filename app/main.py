import time
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.activities import router as activities_router
from app.api.routes.buildings import router as buildings_router
from app.api.routes.organizations import router as organizations_router
from app.db.session import SessionLocal

app = FastAPI(
    title="Organizations Directory API",
    description="Тестовое REST API для справочника организаций, зданий и деятельностей.",
    version="1.0.0",
)


@app.middleware("http")
async def add_observability_headers(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started_at = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - started_at
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    return response


@app.get("/health", tags=["Health"], summary="Проверка состояния сервиса")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"], summary="Проверка подключения к БД")
def healthcheck_db() -> dict[str, str]:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "ok"}


app.include_router(buildings_router, prefix="/api")
app.include_router(activities_router, prefix="/api")
app.include_router(organizations_router, prefix="/api")
