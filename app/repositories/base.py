"""
repositories/base.py
--------------------
CRUD genérico reutilizable para cualquier entidad.

PATRÓN REPOSITORY:
  Tu lógica de negocio nunca escribe SQL ni toca SQLAlchemy directamente.
  Siempre habla con un Repository. El Repository habla con la DB.

  Negocio → Repository → SQLAlchemy → DB

  Beneficios:
    - Cambiar de Postgres a MSSQL: solo cambia el .env
    - Testear sin DB real: reemplazás el repository por uno falso
    - Las operaciones comunes se escriben UNA VEZ y todos las heredan

CÓMO USARLO:
  class ContactRepository(BaseRepository[Contact]):
      def __init__(self, db: Session):
          super().__init__(Contact, db)
      # Solo agregás lo específico de Contacts

SOBRE Generic[T]:
  T es un "tipo genérico" — significa "algún modelo que hereda de BaseEntity".
  Esto activa el autocompletado correcto en tu editor:
  cuando usás ContactRepository, el editor sabe que retorna Contact, no "algo".
"""

from typing import Generic, TypeVar, Type, Optional
from sqlalchemy.orm import Session

from app.models.base import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(Generic[T]):

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db    = db

    # ── READ ──────────────────────────────────────────────────────────────

    def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Lista todos los registros del tenant con paginación.

        El filtro por tenant_id es la garantía de aislamiento:
        un tenant NUNCA puede ver registros de otro, aunque
        compartan la misma base de datos.
        """
        return (
            self.db.query(self.model)
            .filter(self.model.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        """
        Busca un registro por ID, validando que pertenezca al tenant.

        Si el registro existe pero es de otro tenant → retorna None.
        Seguridad por diseño: no necesitás if/else en el router.
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.id        == id,
                self.model.tenant_id == tenant_id,
            )
            .first()
        )

    def count(self, tenant_id: str) -> int:
        """Total de registros del tenant — para paginación y dashboards."""
        return (
            self.db.query(self.model)
            .filter(self.model.tenant_id == tenant_id)
            .count()
        )

    # ── WRITE ─────────────────────────────────────────────────────────────

    def create(self, data: dict) -> T:
        """
        Crea y persiste un nuevo registro.

        Flujo:
          1. Crea el objeto Python con los datos
          2. Lo agrega a la sesión (todavía no está en la DB)
          3. commit() — confirma la transacción → ahora está en la DB
          4. refresh() — recarga el objeto desde la DB para obtener
             los valores generados (created_at, updated_at, etc.)
        """
        record = self.model(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, id: str, data: dict, tenant_id: str) -> Optional[T]:
        """
        Actualiza solo los campos enviados en data.
        Campos no incluidos en data no se modifican (comportamiento PATCH).
        """
        record = self.get_by_id(id, tenant_id)
        if not record:
            return None

        for key, value in data.items():
            setattr(record, key, value)

        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, id: str, tenant_id: str) -> bool:
        """
        Elimina físicamente el registro.
        Retorna True si fue eliminado, False si no existía.

        NOTA FUTURA: cuando implementemos soft delete, este método
        actualizará deleted_at en lugar de borrar.
        El router no cambiará — solo este método.
        """
        record = self.get_by_id(id, tenant_id)
        if not record:
            return False

        self.db.delete(record)
        self.db.commit()
        return True
