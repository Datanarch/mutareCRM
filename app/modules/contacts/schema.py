"""
modules/contacts/schema.py
--------------------------
Schemas Pydantic para la API de Contacts.

POR QUÉ SCHEMAS SEPARADOS DEL MODELO:
  El modelo define cómo se guarda en DB.
  El schema define qué viaja por la API (request/response).
  No deberían ser lo mismo: la DB puede tener campos internos
  que el cliente de la API no debería ver ni poder modificar.

TRES SCHEMAS ESTÁNDAR (patrón que se repite en cada módulo):
  ContactCreate   → qué puede enviar el cliente para crear
  ContactUpdate   → qué puede enviar el cliente para actualizar (todo opcional)
  ContactResponse → qué retorna la API (incluye id y timestamps)
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ContactCreate(BaseModel):
    """Datos requeridos para crear un Contact. tenant_id lo provee el sistema."""

    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None   # Pydantic valida el formato del email
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    """
    Todos los campos son opcionales — solo se actualizan los que se envían.
    Si no enviás 'email', el email del contacto no cambia.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    """
    Lo que retorna la API. Incluye campos de BaseEntity (id, timestamps).
    from_attributes=True permite leer directamente desde un objeto SQLAlchemy.
    """

    id: str
    tenant_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedContacts(BaseModel):
    """
    Respuesta de lista con metadata de paginación.
    Nunca retornamos un array desnudo — siempre con total, skip, limit.
    Esto permite al frontend construir paginación sin endpoints adicionales.
    """

    items: list[ContactResponse]
    total: int
    skip: int
    limit: int
