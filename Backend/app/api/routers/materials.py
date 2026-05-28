from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.mock_db import (
    INTERACTIONS,
    MATERIALS,
    next_interaction_id,
    next_material_id,
)
from app.db.session import get_db
from app.models.schemas import InteractionOut, UploadMaterialResponse
from app.repositories import sql_repository
from app.services.auth_service import get_current_user
from app.services.blob_service import (
    download_material_from_blob,
    upload_material_to_blob,
)
from app.services.permission_service import (
    user_has_material_access as mock_user_has_material_access,
    user_has_project_access as mock_user_has_project_access,
)

router = APIRouter(tags=["materials"])


@router.get("/materials/{material_id}/download")
def download_material(
    material_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if settings.data_mode.lower() == "sql":
        if not sql_repository.user_has_material_access(db, current_user["usuario_id"], material_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este material",
            )

        material = sql_repository.get_material_by_id(db, material_id)
        if not material:
            raise HTTPException(status_code=404, detail="Material no encontrado")

        sql_repository.insert_interaction(
            db,
            current_user["usuario_id"],
            material_id,
            "DESCARGA",
            "Descarga simulada en fase 2",
        )

        file_bytes = download_material_from_blob(
            material["container_name"],
            material["blob_path"],
        )

        return Response(
            content=file_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{material["nombre"]}"'
            },
        )

    if not mock_user_has_material_access(current_user["usuario_id"], material_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este material",
        )

    material = next((m for m in MATERIALS if m["material_id"] == material_id), None)
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    INTERACTIONS.append(
        {
            "interaccion_id": next_interaction_id(),
            "usuario_id": current_user["usuario_id"],
            "material_id": material_id,
            "tipo_interaccion": "DESCARGA",
            "fecha_interaccion": datetime.now(timezone.utc),
            "comentario": "Descarga simulada en fase 2",
        }
    )

   
    file_bytes = download_material_from_blob(
            material["container_name"],
            material["blob_path"],
    )

    return Response(
            content=file_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{material["nombre"]}"'
            },
    )


@router.post("/projects/{project_id}/materials", response_model=UploadMaterialResponse)
async def upload_material(
    project_id: int,
    file: UploadFile = File(...),
    tipo_material: str = Form(...),
    version: str = Form("v1"),
    container_name: str = Form("materials"),
    nivel_confidencialidad: str = Form("Interno"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    safe_name = file.filename.replace(" ", "_")
    blob_path = f"project_{project_id}/{uuid4().hex}_{safe_name}"

    if settings.data_mode.lower() == "sql":
        if not sql_repository.user_has_project_access(db, current_user["usuario_id"], project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso para subir materiales a este proyecto",
            )

        blob_result =  await upload_material_to_blob(file, container_name, blob_path)

        material = sql_repository.insert_material(
            db,
            proyecto_id=project_id,
            nombre=file.filename,
            tipo_material=tipo_material,
            version=version,
            container_name=blob_result["container_name"],
            blob_path=blob_result["blob_path"],
            creado_por=current_user["usuario_id"],
            nivel_confidencialidad=nivel_confidencialidad,
        )

        sql_repository.insert_interaction(
            db,
            current_user["usuario_id"],
            material["material_id"],
            "SUBIDA",
            "Subida simulada en fase 2; metadata insertada en SQL",
        )

        return UploadMaterialResponse(
            message="Metadata registrada en Azure SQL. Blob simulado en fase 2.",
            material=material,
        )

    if not mock_user_has_project_access(current_user["usuario_id"], project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso para subir materiales a este proyecto",
        )

    blob_result = await upload_material_mock(file, container_name, blob_path)

    material = {
        "material_id": next_material_id(),
        "proyecto_id": project_id,
        "nombre": file.filename,
        "tipo_material": tipo_material,
        "version": version,
        "container_name": blob_result["container_name"],
        "blob_path": blob_result["blob_path"],
        "creado_por": current_user["usuario_id"],
        "fecha_creacion": datetime.now(timezone.utc),
        "nivel_confidencialidad": nivel_confidencialidad,
    }

    MATERIALS.append(material)

    return UploadMaterialResponse(
        message="Material registrado correctamente en modo mock",
        material=material,
    )


@router.get("/materials/{material_id}/history", response_model=list[InteractionOut])
def material_history(
    material_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if settings.data_mode.lower() == "sql":
        if not sql_repository.user_has_material_access(db, current_user["usuario_id"], material_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso al historial de este material",
            )
        return sql_repository.list_material_history(db, material_id)

    if not mock_user_has_material_access(current_user["usuario_id"], material_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso al historial de este material",
        )

    return [i for i in INTERACTIONS if i["material_id"] == material_id]
