"""
modules/contacts/model.py
--------------------------
Modelo de DB para la entidad Contact.

Observá lo mínimo que es este archivo.
Todo lo genérico (id, tenant_id, timestamps) viene de BaseEntity.
Aquí solo viven los campos propios de un Contact.

PATRÓN PARA MÓDULOS FUTUROS:
  Cuando crees Deals, Companies, Projects — seguís exactamente esto:
    1. Heredar BaseEntity
    2. Definir __tablename__
    3. Agregar solo los campos específicos de esa entidad
  Tiempo estimado: 15 minutos por modelo.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional

from app.models.base import BaseEntity


class Contact(BaseEntity):
    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(254),  # Máximo técnico de un email según RFC 5321
        nullable=True,
        index=True,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    company: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
