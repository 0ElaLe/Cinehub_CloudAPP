from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.mock_db import MATERIALS, PROJECTS
from app.db.session import get_db
from app.models.schemas import MaterialOut, ProjectOut
from app.repositories import sql_repository
from app.services.auth_service import get_current_user
from app.services.permission_service import (
    user_has_project_access as mock_user_has_project_access,
    user_project_ids,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if settings.data_mode.lower() == "sql":
        return sql_repository.list_projects_for_user(db, current_user["usuario_id"])

    allowed_project_ids = user_project_ids(current_user["usuario_id"])
    return [p for p in PROJECTS if p["proyecto_id"] in allowed_project_ids]


@router.get("/{project_id}/materials", response_model=list[MaterialOut])
def list_project_materials(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if settings.data_mode.lower() == "sql":
        if not sql_repository.user_has_project_access(db, current_user["usuario_id"], project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este proyecto",
            )
        return sql_repository.list_materials_for_project(db, project_id)

    if not mock_user_has_project_access(current_user["usuario_id"], project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este proyecto",
        )

    return [m for m in MATERIALS if m["proyecto_id"] == project_id]
