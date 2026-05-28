from sqlalchemy import text
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str) -> dict | None:
    row = db.execute(
        text("""
            SELECT usuario_id, nombres, apellidos, email
            FROM Usuario
            WHERE LOWER(email) = LOWER(:email)
        """),
        {"email": email},
    ).mappings().first()

    return dict(row) if row else None


def get_user_by_id(db: Session, usuario_id: int) -> dict | None:
    row = db.execute(
        text("""
            SELECT usuario_id, nombres, apellidos, email
            FROM Usuario
            WHERE usuario_id = :usuario_id
        """),
        {"usuario_id": usuario_id},
    ).mappings().first()

    return dict(row) if row else None


def list_projects_for_user(db: Session, usuario_id: int) -> list[dict]:
    rows = db.execute(
        text("""
            SELECT DISTINCT
                p.proyecto_id,
                p.nombre,
                p.descripcion,
                p.estatus
            FROM Proyecto p
            INNER JOIN EquipoProyecto ep
                ON p.proyecto_id = ep.proyecto_id
            INNER JOIN UsuarioEquipo ue
                ON ep.equipo_id = ue.equipo_id
            WHERE ue.usuario_id = :usuario_id
            ORDER BY p.nombre
        """),
        {"usuario_id": usuario_id},
    ).mappings().all()

    return [dict(row) for row in rows]


def user_has_project_access(db: Session, usuario_id: int, proyecto_id: int) -> bool:
    count = db.execute(
        text("""
            SELECT COUNT(*) AS total
            FROM EquipoProyecto ep
            INNER JOIN UsuarioEquipo ue
                ON ep.equipo_id = ue.equipo_id
            WHERE ep.proyecto_id = :proyecto_id
              AND ue.usuario_id = :usuario_id
        """),
        {"usuario_id": usuario_id, "proyecto_id": proyecto_id},
    ).scalar_one()

    return count > 0


def list_materials_for_project(db: Session, proyecto_id: int) -> list[dict]:
    rows = db.execute(
        text("""
            SELECT
                material_id,
                proyecto_id,
                nombre,
                tipo_material,
                version,
                container_name,
                blob_path,
                creado_por,
                fecha_creacion,
                nivel_confidencialidad
            FROM Material
            WHERE proyecto_id = :proyecto_id
            ORDER BY fecha_creacion DESC
        """),
        {"proyecto_id": proyecto_id},
    ).mappings().all()

    return [dict(row) for row in rows]


def get_material_by_id(db: Session, material_id: int) -> dict | None:
    row = db.execute(
        text("""
            SELECT
                material_id,
                proyecto_id,
                nombre,
                tipo_material,
                version,
                container_name,
                blob_path,
                creado_por,
                fecha_creacion,
                nivel_confidencialidad
            FROM Material
            WHERE material_id = :material_id
        """),
        {"material_id": material_id},
    ).mappings().first()

    return dict(row) if row else None


def user_has_material_access(db: Session, usuario_id: int, material_id: int) -> bool:
    count = db.execute(
        text("""
            SELECT COUNT(*) AS total
            FROM Material m
            INNER JOIN EquipoProyecto ep
                ON m.proyecto_id = ep.proyecto_id
            INNER JOIN UsuarioEquipo ue
                ON ep.equipo_id = ue.equipo_id
            WHERE m.material_id = :material_id
              AND ue.usuario_id = :usuario_id
        """),
        {"usuario_id": usuario_id, "material_id": material_id},
    ).scalar_one()

    return count > 0


def insert_interaction(
    db: Session,
    usuario_id: int,
    material_id: int,
    tipo_interaccion: str,
    comentario: str | None = None,
) -> None:
    db.execute(
        text("""
            INSERT INTO InteraccionMaterial (
                usuario_id,
                material_id,
                tipo_interaccion,
                comentario
            )
            VALUES (
                :usuario_id,
                :material_id,
                :tipo_interaccion,
                :comentario
            )
        """),
        {
            "usuario_id": usuario_id,
            "material_id": material_id,
            "tipo_interaccion": tipo_interaccion,
            "comentario": comentario,
        },
    )
    db.commit()


def insert_material(
    db: Session,
    proyecto_id: int,
    nombre: str,
    tipo_material: str,
    version: str,
    container_name: str,
    blob_path: str,
    creado_por: int,
    nivel_confidencialidad: str,
) -> dict:
    row = db.execute(
        text("""
            INSERT INTO Material (
                proyecto_id,
                nombre,
                tipo_material,
                version,
                container_name,
                blob_path,
                creado_por,
                nivel_confidencialidad
            )
            OUTPUT
                INSERTED.material_id,
                INSERTED.proyecto_id,
                INSERTED.nombre,
                INSERTED.tipo_material,
                INSERTED.version,
                INSERTED.container_name,
                INSERTED.blob_path,
                INSERTED.creado_por,
                INSERTED.fecha_creacion,
                INSERTED.nivel_confidencialidad
            VALUES (
                :proyecto_id,
                :nombre,
                :tipo_material,
                :version,
                :container_name,
                :blob_path,
                :creado_por,
                :nivel_confidencialidad
            )
        """),
        {
            "proyecto_id": proyecto_id,
            "nombre": nombre,
            "tipo_material": tipo_material,
            "version": version,
            "container_name": container_name,
            "blob_path": blob_path,
            "creado_por": creado_por,
            "nivel_confidencialidad": nivel_confidencialidad,
        },
    ).mappings().first()

    db.commit()
    return dict(row)


def list_material_history(db: Session, material_id: int) -> list[dict]:
    rows = db.execute(
        text("""
            SELECT
                interaccion_id,
                usuario_id,
                material_id,
                tipo_interaccion,
                fecha_interaccion,
                comentario
            FROM InteraccionMaterial
            WHERE material_id = :material_id
            ORDER BY fecha_interaccion DESC
        """),
        {"material_id": material_id},
    ).mappings().all()

    return [dict(row) for row in rows]
