"""
modules/auth/model.py
---------------------
Tenant  → la organización. No pertenece a ningún tenant — ES el tenant.
User    → pertenece a un tenant. Hereda BaseEntity (tiene tenant_id).

Un usuario siempre pertenece a un tenant.
Un tenant puede tener múltiples usuarios.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base
from app.models.base import BaseEntity


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(String(50), default="starter")
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"


class User(BaseEntity):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member")
