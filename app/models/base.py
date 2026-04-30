"""
models/base.py
--------------
Modelo base para todas las entidades del sistema.

PRINCIPIO: los campos comunes a TODAS las entidades se definen
UNA SOLA VEZ aquí. Cada módulo hereda esto y solo define sus
campos propios.

CAMPOS QUE VIENEN GRATIS EN TODA ENTIDAD:
  - id         → UUID único, generado automáticamente
  - tenant_id  → a qué cliente/organización pertenece el registro
  - created_at → cuándo fue creado (UTC, automático)
  - updated_at → cuándo fue modificado (UTC, automático al hacer update)

POR QUÉ __abstract__ = True:
  Le dice a SQLAlchemy que BaseEntity NO genera su propia tabla.
  Es solo una plantilla de herencia. Cada modelo hijo SÍ genera tabla.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional

from app.core.database import Base


def _utc_now() -> datetime:
    """Hora actual en UTC. Siempre UTC — nunca hora local del servidor."""
    return datetime.now(timezone.utc)


class BaseEntity(Base):
    __abstract__ = True  # No crea tabla — solo herencia

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,  # Índice porque CADA query filtra por tenant_id
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,  # SQLAlchemy actualiza esto automáticamente
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id[:8]}...>"
