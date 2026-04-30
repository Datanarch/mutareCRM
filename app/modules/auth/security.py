"""
modules/auth/security.py
------------------------
Dos responsabilidades:
  1. Passwords — hashear al guardar, verificar al hacer login
  2. JWT       — crear el token al login, leerlo en cada request

NUNCA guardamos passwords en texto plano.
passlib se encarga de hashear con bcrypt — un algoritmo
diseñado para ser lento y resistente a ataques de fuerza bruta.
"""

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt

# Clave secreta para firmar los tokens.
# En producción esto viene de una variable de entorno.
# Si alguien obtiene esta clave puede generar tokens válidos.
SECRET_KEY = "cambia-esto-en-produccion-con-una-clave-larga-y-random"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas


def hash_password(password: str) -> str:
    """Convierte un password en texto plano a un hash bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica si un password en texto plano coincide con el hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    """
    Genera un JWT firmado con los datos del usuario.

    El payload incluye:
      sub       → user_id (subject — estándar JWT)
      tenant_id → para aislar datos por tenant
      role      → para validar permisos
      exp       → cuándo expira el token
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.

    Lanza JWTError si el token es inválido o expiró.
    Retorna el payload si todo está bien.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
