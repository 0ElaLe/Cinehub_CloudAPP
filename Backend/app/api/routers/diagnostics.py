import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_engine
from app.services.blob_service import get_blob_service_client

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)


def _check_sql() -> dict:
    try:
        with get_engine().connect() as conn:
            row = conn.execute(
                text("SELECT DB_NAME() AS database_name")
            ).mappings().first()
        return {"status": "ok", "database": row["database_name"]}
    except Exception as exc:
        # Loguear solo el tipo de error — no exponer credenciales ni detalles internos
        logger.error("SQL health check fallido: %s", type(exc).__name__)
        return {"status": "error", "detail": type(exc).__name__}


def _check_blob() -> dict:
    try:
        client = get_blob_service_client()
        info = client.get_account_information()
        container = client.get_container_client(settings.blob_container_default)
        return {
            "status": "ok",
            "account_kind": info.get("account_kind"),
            "sku_name": info.get("sku_name"),
            "default_container": settings.blob_container_default,
            "default_container_exists": container.exists(),
        }
    except Exception as exc:
        logger.error("Blob Storage health check fallido: %s", type(exc).__name__)
        return {"status": "error", "detail": type(exc).__name__}


@router.get("/dependencies")
def check_dependencies():
    """Verifica conectividad con SQL y Blob Storage. No expone credenciales."""
    return {
        "api": {
            "status": "ok",
            "environment": settings.environment,
            "data_mode": settings.data_mode,
        },
        "sql": _check_sql(),
        "blob": _check_blob(),
    }


@router.get("/db")
def check_db():
    """Prueba de conexión a Azure SQL Database."""
    return _check_sql()


@router.get("/storage")
def check_storage():
    """Prueba de conexión a Azure Blob Storage."""
    return _check_blob()
