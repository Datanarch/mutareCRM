"""
main.py
-------
Punto de entrada de la aplicación.

TRES COSAS Y SOLO TRES:
  1. Crear la app FastAPI con su configuración
  2. Crear las tablas en DB (solo desarrollo — en prod usamos Alembic)
  3. Registrar los routers de cada módulo

AGREGAR UN MÓDULO NUEVO:
  Solo necesitás dos líneas:
    from app.modules.deals.model  import Deal          # noqa: F401
    from app.modules.deals.router import router as deals_router
    app.include_router(deals_router, prefix="/api/v1")
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.model import Tenant, User  # noqa: F401
from app.modules.auth.router import router as auth_router, get_current_user

from app.core.config import settings
from app.core.database import engine, Base

# Los modelos deben importarse para que Base los registre.
# Sin esta línea, create_all() no sabe que Contact existe.
from app.modules.contacts.model import Contact  # noqa: F401
from app.modules.contacts.router import router as contacts_router

# Crea tablas que no existen — no toca las que ya existen.
# Solo activo cuando DATABASE_URL NO es :memory: (evita conflicto con tests).
import os

if ":memory:" not in os.getenv("DATABASE_URL", "sqlite:///./crm_dev.db"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
![Mutare CRM](./assets/mutare_logo_light.svg)

API REST del CRM Modular.

**Estado actual:** Ciclo 1 — Contacts CRUD
**Próximo ciclo:** Frontend React
**Documentación interactiva:** `/docs`
    """,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: lista de dominios específicos
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts_router, prefix="/api/v1")  # contacts routes
app.include_router(auth_router, prefix="/api/v1")  # auth routes


@app.get("/health", tags=["System"])
def health():
    """Verifica que la API está corriendo. Usado por Railway/Render para healthchecks."""
    return {"status": "ok", "version": settings.app_version}
