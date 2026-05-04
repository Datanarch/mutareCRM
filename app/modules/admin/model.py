from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


from app.core.database import Base
from app.models.base import BaseEntity


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("roles.id"), primary_key=True
    )
    permission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("permissions.id"), primary_key=True
    )


class Permission(Base):
    pass


class Role(BaseEntity):
    pass


class UserRole:
    __tablename__ = "user_role"

    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user.id"), primary_key=True
    )
    permission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("role.id"), primary_key=True
    )
