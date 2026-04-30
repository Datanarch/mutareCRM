"""
modules/contacts/repository.py
-------------------------------
Operaciones de DB específicas para Contacts.

Hereda TODO el CRUD de BaseRepository.
Este archivo solo existe para agregar lo que es exclusivo de Contacts.
Si no hubiera nada específico, podríamos usar BaseRepository directamente.
"""

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.modules.contacts.model import Contact


class ContactRepository(BaseRepository[Contact]):

    def __init__(self, db: Session):
        super().__init__(Contact, db)

    def get_by_email(self, email: str, tenant_id: str) -> Contact | None:
        """
        Busca un Contact por email dentro del tenant.
        Usado para detectar duplicados antes de crear.
        """
        return (
            self.db.query(Contact)
            .filter(
                Contact.email     == email,
                Contact.tenant_id == tenant_id,
            )
            .first()
        )

    def search(self, query: str, tenant_id: str, limit: int = 50) -> list[Contact]:
        """
        Búsqueda por nombre, email o empresa (case-insensitive).

        ilike() funciona en Postgres, MySQL y SQLite.
        Para MSSQL usar .like() — MSSQL es case-insensitive por defecto
        según el collation del servidor.
        """
        term = f"%{query}%"
        return (
            self.db.query(Contact)
            .filter(
                Contact.tenant_id == tenant_id,
                Contact.name.ilike(term)
                | Contact.email.ilike(term)
                | Contact.company.ilike(term),
            )
            .limit(limit)
            .all()
        )
