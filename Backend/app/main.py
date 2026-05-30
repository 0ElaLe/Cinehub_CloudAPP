import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import auth, materials, projects, diagnostics
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="API intranet privada de CineHub — portal de materiales cinematográficos",
    version="0.2.0",
)

# CORS: se configura vía variable de entorno CORS_ORIGINS (lista separada por comas).
# En producción con frontend servido desde el mismo App Service, no se requieren orígenes extra.
_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(materials.router)
app.include_router(diagnostics.router)


@app.get("/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "data_mode": settings.data_mode,
        "app": settings.app_name,
    }


# Sirve el frontend React compilado desde Backend/static/.
# El build de CI corre `npm run build` en Frontend/ y Vite escribe en ../Backend/static/.
# Si el directorio no existe (entorno de desarrollo sin build), se omite silenciosamente.
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
