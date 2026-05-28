from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, materials, projects, diagnostics
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="API mínima para la intranet privada de CineHub",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(materials.router)
app.include_router(diagnostics.router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "data_mode": settings.data_mode,
        "app": settings.app_name,
    }
