"""
core/config.py
--------------
Configuración central de la aplicación.

PRINCIPIO: este es el ÚNICO lugar donde viven los valores de configuración.
Nunca escribas strings de conexión, secretos o URLs directamente en el código.
Si algo puede cambiar entre entornos (dev local, producción, cliente A, cliente B)
— vive aquí, leído desde .env.

CÓMO FUNCIONA:
  Pydantic lee automáticamente el archivo .env y mapea cada variable
  a un atributo de Settings. Si la variable no existe en .env, usa
  el valor por defecto definido en la clase.

  Orden de prioridad:
    1. Variable de entorno del sistema operativo (mayor prioridad)
    2. Variable en el archivo .env
    3. Valor por defecto en la clase
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Aplicación ────────────────────────────────────────────────────────
    app_name: str = "Mutare CRM Modular"
    app_version: str = "0.1.0"
    debug: bool = True
    secret_key: str = "dev-secret-key-cambiar-en-produccion"

    # ── Base de datos ─────────────────────────────────────────────────────
    # SQLAlchemy interpreta el prefijo de la URL y usa el driver correcto.
    # Cambiar de motor = cambiar esta línea en .env. El código no cambia.
    #
    # Ejemplos:
    #   sqlite:///./crm_dev.db                          → SQLite (sin instalar nada)
    #   postgresql://user:pass@localhost:5432/crm        → PostgreSQL
    #   mssql+pyodbc://user:pass@host/db?driver=...      → MS SQL Server
    #   mysql+pymysql://user:pass@localhost:3306/crm     → MySQL
    database_url: str = "sqlite:///./crm_dev.db"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Instancia global — se importa desde cualquier parte del proyecto.
# Uso: from app.core.config import settings
settings = Settings()
