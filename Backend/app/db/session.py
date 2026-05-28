from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def build_sqlalchemy_url() -> str:
    required = {
        "SQL_HOST": settings.sql_host,
        "SQL_DATABASE": settings.sql_database,
        "SQL_USER": settings.sql_user,
        "SQL_PASSWORD": settings.sql_password,
    }

    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"Faltan variables de entorno para SQL: {', '.join(missing)}")

    odbc_connection = (
        f"DRIVER={{{settings.sql_odbc_driver}}};"
        f"SERVER=tcp:{settings.sql_host},{settings.sql_port};"
        f"DATABASE={settings.sql_database};"
        f"UID={settings.sql_user};"
        f"PWD={settings.sql_password};"
        "Encrypt=yes;"
        f"TrustServerCertificate={settings.sql_trust_server_certificate};"
        "Connection Timeout=30;"
    )

    return "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_connection)


engine = create_engine(
    build_sqlalchemy_url(),
    pool_pre_ping=True,
    pool_recycle=1800,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
