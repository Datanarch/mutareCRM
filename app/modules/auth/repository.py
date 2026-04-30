"""
modules/auth/repository.py
--------------------------
Operaciones de DB para Tenant y User.
"""

from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.modules.auth.model import Tenant, User


class TenantRepository:
    """
    Tenant no hereda BaseEntity, entonces no puede usar BaseRepository.
    Tiene su propio repository simple.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self.db.query(Tenant).filter(Tenant.slug == slug).first()

    def create(self, data: dict) -> Tenant:
        tenant = Tenant(**data)
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant


class UserRepository(BaseRepository[User]):

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str, tenant_id: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email, User.tenant_id == tenant_id)
            .first()
        )

    def get_admin_count(self, tenant_id: str) -> int:
        return (
            self.db.query(User)
            .filter(User.tenant_id == tenant_id, User.role == "admin")
            .count()
        )
