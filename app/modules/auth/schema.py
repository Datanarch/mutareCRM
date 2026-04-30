"""
modules/auth/schema.py
----------------------
Schemas para registro, login y respuestas de Auth.

TenantCreate  → datos para crear una organización
UserRegister  → datos para registrar el primer usuario (Admin) de un tenant
UserLogin     → credenciales para hacer login
TokenResponse → lo que retorna el login: el JWT y datos básicos del usuario
UserResponse  → datos públicos del usuario (sin password_hash)
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    plan: Optional[str] = "starter"


class UserRegister(BaseModel):
    """
    Registro del primer usuario de un tenant nuevo.
    Este usuario se crea automáticamente como Admin.
    """
    tenant_name: str = Field(..., min_length=2, max_length=200)
    tenant_slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    role: str

    model_config = {"from_attributes": True}
