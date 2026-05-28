from app.data.mock_db import USER_TEAMS, TEAM_PROJECTS, MATERIALS


def user_project_ids(user_id: int) -> set[int]:
    team_ids = {
        row["equipo_id"]
        for row in USER_TEAMS
        if row["usuario_id"] == user_id
    }

    return {
        row["proyecto_id"]
        for row in TEAM_PROJECTS
        if row["equipo_id"] in team_ids
    }


def user_has_project_access(user_id: int, project_id: int) -> bool:
    return project_id in user_project_ids(user_id)


def user_has_material_access(user_id: int, material_id: int) -> bool:
    material = next((m for m in MATERIALS if m["material_id"] == material_id), None)
    if not material:
        return False
    return user_has_project_access(user_id, material["proyecto_id"])
