"""
modules/contacts/router.py
--------------------------
Endpoints HTTP del módulo Contacts.
tenant_id viene del JWT — no del query parameter.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.router import get_current_user
from app.modules.contacts.repository import ContactRepository
from app.modules.contacts.schema import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    PaginatedContacts,
)

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("/", response_model=PaginatedContacts, summary="Listar contacts")
def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    repo = ContactRepository(db)
    items = repo.get_all(tenant_id, skip=skip, limit=limit)
    return PaginatedContacts(
        items=[ContactResponse.model_validate(c) for c in items],
        total=repo.count(tenant_id),
        skip=skip,
        limit=limit,
    )


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear contact",
)
def create_contact(
    payload: ContactCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
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
    q: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    return ContactRepository(db).search(q, tenant_id)


@router.get("/{contact_id}", response_model=ContactResponse, summary="Obtener contact")
def get_contact(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    contact = ContactRepository(db).get_by_id(contact_id, tenant_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact no encontrado."
        )
    return contact


@router.put(
    "/{contact_id}", response_model=ContactResponse, summary="Actualizar contact"
)
def update_contact(
    contact_id: str,
    payload: ContactUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    data = payload.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar.",
        )

    contact = ContactRepository(db).update(contact_id, data, tenant_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact no encontrado."
        )
    return contact


@router.delete(
    "/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar contact"
)
def delete_contact(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    deleted = ContactRepository(db).delete(contact_id, tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact no encontrado."
        )
