"""
modules/contacts/router.py
--------------------------
Endpoints HTTP del módulo Contacts.

RESPONSABILIDAD DE ESTE ARCHIVO:
  Recibir el request → validar con schema → llamar al repository → retornar respuesta.
  Sin lógica de negocio compleja, sin SQL, sin SQLAlchemy directo.

SOBRE EL tenant_id TEMPORAL:
  Por ahora viene como query parameter (?x_tenant_id=...).
  En el Ciclo 3, cuando implementemos Auth con JWT, este parámetro
  desaparecerá y el tenant_id se extraerá del token automáticamente.
  Los endpoints no cambiarán — solo la dependency get_tenant_id().

CONVENCIÓN REST:
  GET    /contacts/          → listar con paginación
  POST   /contacts/          → crear
  GET    /contacts/search    → buscar  (ANTES de /{id} — FastAPI es sensible al orden)
  GET    /contacts/{id}      → obtener por ID
  PUT    /contacts/{id}      → actualizar
  DELETE /contacts/{id}      → eliminar
"""

from calendar import c

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import contacts
from app.modules.contacts.repository import ContactRepository
from app.modules.contacts.schema import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    PaginatedContacts,
)

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def get_tenant_id(x_tenant_id: str = Query(..., description="ID del tenant (temporal — reemplazado por Auth en Ciclo 3)")) -> str:
    return x_tenant_id


@router.get("/", response_model=PaginatedContacts, summary="Listar contacts")
def list_contacts(
    skip:      int     = Query(0,   ge=0),
    limit:     int     = Query(100, ge=1, le=500),
    tenant_id: str     = Depends(get_tenant_id),
    db:        Session = Depends(get_db),
):
    repo  = ContactRepository(db)
    contacts = repo.get_all(tenant_id, skip=skip, limit=limit)
    return PaginatedContacts(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=repo.count(tenant_id),
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, summary="Crear contact")
def create_contact(
    payload:   ContactCreate,
    tenant_id: str     = Depends(get_tenant_id),
    db:        Session = Depends(get_db),
):
    repo = ContactRepository(db)

    if payload.email and repo.get_by_email(payload.email, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un contact con el email '{payload.email}'.",
        )

    data = payload.model_dump()
    data["tenant_id"] = tenant_id
    return repo.create(data)


@router.get("/search", response_model=list[ContactResponse], summary="Buscar contacts")
def search_contacts(
    q:         str     = Query(..., min_length=1, description="Término de búsqueda"),
    tenant_id: str     = Depends(get_tenant_id),
    db:        Session = Depends(get_db),
):
    return ContactRepository(db).search(q, tenant_id)


@router.get("/{contact_id}", response_model=ContactResponse, summary="Obtener contact")
def get_contact(
    contact_id: str,
    tenant_id:  str     = Depends(get_tenant_id),
    db:         Session = Depends(get_db),
):
    contact = ContactRepository(db).get_by_id(contact_id, tenant_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact no encontrado.")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, summary="Actualizar contact")
def update_contact(
    contact_id: str,
    payload:    ContactUpdate,
    tenant_id:  str     = Depends(get_tenant_id),
    db:         Session = Depends(get_db),
):
    data = payload.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se enviaron campos para actualizar.")

    contact = ContactRepository(db).update(contact_id, data, tenant_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact no encontrado.")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar contact")
def delete_contact(
    contact_id: str,
    tenant_id:  str     = Depends(get_tenant_id),
    db:         Session = Depends(get_db),
):
    deleted = ContactRepository(db).delete(contact_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact no encontrado.")
