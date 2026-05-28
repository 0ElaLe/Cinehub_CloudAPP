from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.mock_db import USERS
from app.db.session import get_db
from app.repositories import sql_repository

bearer_scheme = HTTPBearer(auto_error=False)
def authenticate_user(email: str, password: str, db: Session | None = None) -> dict:
    if settings.data_mode.lower() == "sql":
        if db is None:
            raise RuntimeError("Se requiere sesión de base de datos para DATA_MODE=sql")

        user = sql_repository.get_user_by_email(db, email)
        if user and password == settings.demo_password:
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    for user in USERS:
        if user["email"].lower() == email.lower() and user["password"] == password:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
    )


def create_mock_token(user: dict) -> str:
    # Fase 2: aún usamos token simple para no mezclar conexión SQL con seguridad JWT real.
    return f"mock-token-user-{user['usuario_id']}"


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta token Bearer",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esquema de autenticación inválido",
        )

    token = credentials.credentials

    if not token.startswith("mock-token-user-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    try:
        user_id = int(token.split("-")[-1])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    if settings.data_mode.lower() == "sql":
        user = sql_repository.get_user_by_id(db, user_id)
        if user:
            return user
    else:
        for user in USERS:
            if user["usuario_id"] == user_id:
                return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario no encontrado",
    )
