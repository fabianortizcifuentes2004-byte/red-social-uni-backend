import pytest

from app import create_app, db as _db


class TestConfig:
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DOMINIO_INSTITUCIONAL = "usanjose.edu.co"
    JWT_ACCESS_TOKEN_EXPIRES_HORAS = 12


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana Torres"):
    """Registra un usuario y devuelve los headers de Authorization con su JWT."""
    client.post(
        "/api/auth/registro",
        json={"nombre_completo": nombre, "correo": correo, "password": "clave123"},
    )
    resp = client.post("/api/auth/login", json={"correo": correo, "password": "clave123"})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
