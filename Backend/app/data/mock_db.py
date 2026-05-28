from datetime import datetime, timezone

USERS = [
    {
        "usuario_id": 1,
        "nombres": "Ana",
        "apellidos": "Torres",
        "email": "ana.torres@cinehub.com",
        "password": "cinehub123",
    },
    {
        "usuario_id": 2,
        "nombres": "Luis",
        "apellidos": "Ramirez",
        "email": "luis.ramirez@cinehub.com",
        "password": "cinehub123",
    },
]

USER_TEAMS = [
    {"usuario_id": 1, "equipo_id": 1, "rol": "Editora"},
    {"usuario_id": 2, "equipo_id": 2, "rol": "Colorista"},
]

PROJECTS = [
    {"proyecto_id": 1, "nombre": "Cortometraje Aurora", "descripcion": "Proyecto cinematografico interno de prueba", "estatus": "Activo"},
    {"proyecto_id": 2, "nombre": "Comercial Eclipse", "descripcion": "Produccion publicitaria confidencial", "estatus": "Activo"},
]

TEAM_PROJECTS = [
    {"equipo_id": 1, "proyecto_id": 1, "rol_en_proyecto": "Edicion principal"},
    {"equipo_id": 2, "proyecto_id": 1, "rol_en_proyecto": "Correccion de color"},
]

MATERIALS = [
    {
        "material_id": 1,
        "proyecto_id": 1,
        "nombre": "escena_01_preview_v1.mp4",
        "tipo_material": "Video",
        "version": "v1",
        "container_name": "edited-cuts",
        "blob_path": "aurora/escena_01/preview_v1.mp4",
        "creado_por": 1,
        "fecha_creacion": datetime.now(timezone.utc),
        "nivel_confidencialidad": "Confidencial",
    }
]

INTERACTIONS = []


def next_material_id() -> int:
    return max([m["material_id"] for m in MATERIALS], default=0) + 1


def next_interaction_id() -> int:
    return max([i["interaccion_id"] for i in INTERACTIONS], default=0) + 1
