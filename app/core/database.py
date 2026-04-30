"""
core/database.py
----------------
Motor de base de datos, sesiones y clase base de modelos.

TRES RESPONSABILIDADES:
  1. Engine    — la conexión física a la DB (una por aplicación)
  2. Session   — una "conversación" con la DB (una por request HTTP)
  3. Base      — clase padre de todos los modelos SQLAlchemy

POR QUÉ get_db() ES UNA FUNCIÓN GENERADORA (yield):
  FastAPI la usa como Dependency Injection. El flujo es:
    → request entra
    → FastAPI llama get_db(), la sesión se abre
    → se entrega al endpoint (yield)
    → el endpoint hace su trabajo
    → request termina → el bloque finally cierra la sesión SIEMPRE
  El finally garantiza que la sesión se cierra incluso si hay una excepción.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.core.config import settings


# SQLite necesita este argumento extra porque FastAPI corre en múltiples
# threads y SQLite por defecto solo permite un thread por conexión.
# Para otros motores (Postgres, MSSQL) esto no aplica.
_connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=settings.debug,  # echo=True imprime el SQL generado — útil para aprender
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,  # Vos controlás cuándo se confirman los cambios (commit)
    autoflush=False,   # No ejecuta queries pendientes automáticamente
)


class Base(DeclarativeBase):
    """
    Clase base de la que heredan TODOS los modelos del proyecto.

    SQLAlchemy usa esta clase para descubrir todas las tablas
    y poder crearlas con Base.metadata.create_all(engine).
    """
    pass


def get_db():
    """
    Dependency de FastAPI — provee una sesión de DB a cada endpoint.

    Uso en un router:
        @router.get("/")
        def my_endpoint(db: Session = Depends(get_db)):
            repo = MyRepository(db)
            return repo.get_all(...)
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
