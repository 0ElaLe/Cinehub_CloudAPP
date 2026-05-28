from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.services.blob_service import get_blob_service_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/dependencies")
def check_dependencies():
    result = {
        "api": {
            "status": "ok",
            "environment": settings.environment,
            "data_mode": settings.data_mode,
        },
        "sql": {
            "status": "unknown",
            "detail": None,
        },
        "blob": {
            "status": "unknown",
            "detail": None,
        },
    }

    # Revisar Azure SQL
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT DB_NAME() AS database_name")
            ).mappings().first()

            result["sql"] = {
                "status": "ok",
                "database": row["database_name"],
            }

    except Exception as exc:
        result["sql"] = {
            "status": "error",
            "detail": str(exc),
        }

    # Revisar Azure Blob Storage
    try:
        blob_service_client = get_blob_service_client()

        account_info = blob_service_client.get_account_information()

        container_client = blob_service_client.get_container_client(
            settings.blob_container_default
        )

        container_exists = container_client.exists()

        result["blob"] = {
            "status": "ok",
            "account_kind": account_info.get("account_kind"),
            "sku_name": account_info.get("sku_name"),
            "default_container": settings.blob_container_default,
            "default_container_exists": container_exists,
        }

    except Exception as exc:
        result["blob"] = {
            "status": "error",
            "detail": str(exc),
        }

    return result