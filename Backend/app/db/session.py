from urllib.parse import quote_plus
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Inicialización lazy: el engine se crea solo cuando se necesita,
# no al importar el módulo. Evita crash en startup si faltan vars SQL.
_engine: Engine | None = None
_SessionLocal = None


def _init() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        return

    required = {
        "SQL_HOST": settings.sql_host,
        "SQL_DATABASE": settings.sql_database,
        "SQL_USER": settings.sql_user,
        "SQL_PASSWORD": settings.sql_password,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(
            f"Faltan variables de entorno requeridas para SQL: {', '.join(missing)}. "
            "Configúralas como App Settings en Azure Portal."
        )

    odbc = (
        f"DRIVER={{{settings.sql_odbc_driver}}};"
        f"SERVER=tcp:{settings.sql_host},{settings.sql_port};"
        f"DATABASE={settings.sql_database};"
        f"UID={settings.sql_user};"
        f"PWD={settings.sql_password};"
        "Encrypt=yes;"
        f"TrustServerCertificate={settings.sql_trust_server_certificate};"
        "Connection Timeout=30;"
    )
    url = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc)

    _engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
        future=True,
    )


def get_engine() -> Engine:
    _init()
    return _engine


def get_db() -> Generator[Session, None, None]:
    _init()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
