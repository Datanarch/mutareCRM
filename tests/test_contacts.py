"""
tests/test_contacts.py — Tests del módulo Contacts.

LECCIÓN APRENDIDA - StaticPool:
  SQLite en memoria (:memory:) crea una DB nueva por cada conexión.
  Cuando FastAPI abre una sesión nueva para cada request, obtiene
  una conexión nueva → DB vacía → "no such table".

  StaticPool fuerza que TODAS las conexiones reusen la misma
  conexión subyacente → misma DB → tablas persisten entre requests.

  Esto solo aplica en tests con SQLite en memoria.
  En Postgres/MSSQL (real), cada conexión ve la misma DB — no hay problema.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db

TENANT       = "tenant-1"
OTHER_TENANT = "tenant-2"

@pytest.fixture(scope="module")
def client():
    from app.main import app
    from app.modules.contacts.model import Contact  # noqa — registra en Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,   # ← la clave: una sola conexión compartida
    )
    TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_contact(client):
    r = client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={
        "name": "Henry Test", "email": "henry@test.com", "company": "Datanarch"
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Henry Test"
    assert data["tenant_id"] == TENANT
    assert "id" in data and "created_at" in data

def test_list_contacts(client):
    r = client.get(f"/api/v1/contacts/?x_tenant_id={TENANT}")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and data["total"] >= 1

def test_tenant_isolation(client):
    """Un tenant NO puede ver los datos de otro tenant."""
    r = client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Solo Tenant 1"})
    contact_id = r.json()["id"]
    r = client.get(f"/api/v1/contacts/{contact_id}?x_tenant_id={OTHER_TENANT}")
    assert r.status_code == 404

def test_duplicate_email_rejected(client):
    email = "unico@datanarch.dev"
    client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Primero", "email": email})
    r = client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Segundo", "email": email})
    assert r.status_code == 409

def test_update_only_sent_fields(client):
    r = client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Original", "company": "Corp"})
    cid = r.json()["id"]
    r = client.put(f"/api/v1/contacts/{cid}?x_tenant_id={TENANT}", json={"notes": "Actualizado"})
    assert r.status_code == 200
    assert r.json()["notes"] == "Actualizado"
    assert r.json()["name"] == "Original"   # No cambió

def test_delete_contact(client):
    r = client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Para eliminar"})
    cid = r.json()["id"]
    assert client.delete(f"/api/v1/contacts/{cid}?x_tenant_id={TENANT}").status_code == 204
    assert client.get(f"/api/v1/contacts/{cid}?x_tenant_id={TENANT}").status_code == 404

def test_search(client):
    client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Searchable Name"})
    r = client.get(f"/api/v1/contacts/search?q=searchable&x_tenant_id={TENANT}")
    assert r.status_code == 200
    assert any("Searchable" in c["name"] for c in r.json())

def test_empty_update_rejected(client):
    r = client.post(f"/api/v1/contacts/?x_tenant_id={TENANT}", json={"name": "Test Empty"})
    cid = r.json()["id"]
    r = client.put(f"/api/v1/contacts/{cid}?x_tenant_id={TENANT}", json={})
    assert r.status_code == 400
