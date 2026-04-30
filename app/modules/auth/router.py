"""
modules/auth/router.py
----------------------
Tres endpoints:
  POST /auth/register  → crea tenant + usuario Admin
  POST /auth/login     → retorna JWT
  GET  /auth/me        → retorna usuario actual (requiere token)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.database import get_db
from app.modules.auth.schema import UserRegister, UserLogin, TokenResponse, UserResponse
from app.modules.auth.repository import TenantRepository, UserRepository
from app.modules.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

bearer_schema = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_schema),
    db: Session = Depends(get_db),
) -> dict:
    """
    Dependency que reemplaza get_tenant_id().
    Lee el JWT, valida la firma y retorna los datos del usuario.
    Se usa en cualquier endpoint que requiera autenticación.
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        role: str = payload.get("role")
        if not user_id or not tenant_id:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return {"user_id": user_id, "tenant_id": tenant_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Crea un tenant nuevo y su primer usuario como Admin.
    Es el punto de entrada de un cliente nuevo a la plataforma.
    """
    tenant_repo = TenantRepository(db)
    user_repo = UserRepository(db)

    # Verificar que el slug no exista
    if tenant_repo.get_by_slug(payload.tenant_slug):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El slug '{payload.tenant_slug}' ya está en uso.",
        )

    # Crear tenant
    tenant = tenant_repo.create(
        {
            "name": payload.tenant_name,
            "slug": payload.tenant_slug,
        }
    )

    # Crear usuario Admin
    user_repo.create(
        {
            "tenant_id": tenant.id,
            "email": payload.email,
            "password_hash": hash_password(payload.password),
            "role": "admin",
        }
    )

    return {"message": f"Tenant '{tenant.slug}' creado exitosamente."}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Valida credenciales y retorna un JWT.
    El cliente guarda este token y lo envía en cada request.
    """
    tenant_repo = TenantRepository(db)
    user_repo = UserRepository(db)

    # Verificar que el tenant existe
    tenant = tenant_repo.get_by_slug(payload.tenant_slug)
    if not tenant:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    # Verificar que el usuario existe en ese tenant
    user = user_repo.get_by_email(payload.email, tenant.id)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    # Generar JWT
    token = create_access_token(user.id, tenant.id, user.role)

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna los datos del usuario autenticado."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["user_id"], current_user["tenant_id"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return UserResponse.model_validate(user)
