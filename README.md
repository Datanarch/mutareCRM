# CRM Modular
![Mutare CRM](./assets/mutare_logo_final.svg)
API REST modular construida con FastAPI + SQLAlchemy + Poetry.

## Filosofía
Ship early. Learn fast. Improve always.

## Setup

```bash
# 1. Instalar Poetry (si no lo tenés)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Instalar dependencias
poetry install

# 3. Configurar entorno
cp .env.example .env

# 4. Correr la API
poetry run uvicorn app.main:app --reload
```

API:           http://localhost:8000
Documentación: http://localhost:8000/docs

## Cambiar base de datos

Solo cambiá `DATABASE_URL` en `.env`. El código no cambia.

```bash
DATABASE_URL=sqlite:///./crm_dev.db          # Desarrollo local
DATABASE_URL=postgresql://user:pass@host/db  # Producción
DATABASE_URL=mssql+pyodbc://...              # Cliente con MS SQL
```

## Correr tests

```bash
poetry run pytest tests/ -v
```

## Agregar un módulo nuevo (ej: Deals)

```
app/modules/deals/
├── __init__.py
├── model.py       → class Deal(BaseEntity): ...
├── schema.py      → DealCreate, DealUpdate, DealResponse
├── repository.py  → class DealRepository(BaseRepository[Deal]): ...
└── router.py      → endpoints CRUD
```

En `main.py`:
```python
from app.modules.deals.model  import Deal          # noqa: F401
from app.modules.deals.router import router as deals_router
app.include_router(deals_router, prefix="/api/v1")
```

Tiempo por módulo nuevo: ~3 horas.

## Ciclos de desarrollo

| Ciclo | Objetivo | Estado |
|-------|----------|--------|
| 1 | Core + Contacts CRUD | ✅ Completo |
| 2 | Frontend React — EntityList + EntityForm | ⬜ Próximo |
| 3 | Auth — JWT + tenant desde token | ⬜ |
| 4 | Plugin Pipeline — Kanban | ⬜ |
| 5 | Plugin Activities — Timeline | ⬜ |
| 6 | Admin panel — feature flags por tenant | ⬜ |
