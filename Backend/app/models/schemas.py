from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    usuario_id: int
    nombres: str
    apellidos: str
    email: EmailStr


class ProjectOut(BaseModel):
    proyecto_id: int
    nombre: str
    descripcion: str | None = None
    estatus: str


class MaterialOut(BaseModel):
    material_id: int
    proyecto_id: int
    nombre: str
    tipo_material: str
    version: str
    container_name: str
    blob_path: str
    creado_por: int | None = None
    fecha_creacion: datetime | None = None
    nivel_confidencialidad: str


class InteractionOut(BaseModel):
    interaccion_id: int
    usuario_id: int
    material_id: int
    tipo_interaccion: str
    fecha_interaccion: datetime | None = None
    comentario: str | None = None


class UploadMaterialResponse(BaseModel):
    message: str
    material: MaterialOut
