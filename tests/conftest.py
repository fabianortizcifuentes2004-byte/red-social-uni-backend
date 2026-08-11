import shutil
import tempfile

import pytest

from app import create_app, db as _db


class TestConfig:
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DOMINIO_INSTITUCIONAL = "usanjose.edu.co"
    JWT_ACCESS_TOKEN_EXPIRES_HORAS = 12
    UPLOAD_FOLDER = None  # se asigna por test a una carpeta temporal
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ORIGENES_PERMITIDOS = "*"
    # Desactivado por defecto: el limiter es un singleton a nivel de módulo y
    # comparte almacenamiento entre apps de test dentro del mismo proceso, así
    # que dejarlo activo rompería tests no relacionados que hacen login varias
    # veces. Se reactiva puntualmente en test_rate_limiting.py.
    RATELIMIT_ENABLED = False


@pytest.fixture
def app():
    carpeta_uploads = tempfile.mkdtemp()
    TestConfig.UPLOAD_FOLDER = carpeta_uploads
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()
    shutil.rmtree(carpeta_uploads, ignore_errors=True)


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


def registrar_admin_y_loguear(client, correo="admin@usanjose.edu.co", nombre="Admin"):
    """Registra un usuario, lo promueve a admin directamente en el modelo (la API
    pública no lo permite) y vuelve a loguear para obtener un token con el claim
    de rol ya actualizado."""
    from app.models.usuario import Usuario, RolUsuario

    registrar_y_loguear(client, correo=correo, nombre=nombre)
    usuario = Usuario.query.filter_by(correo=correo).first()
    usuario.rol = RolUsuario.ADMIN
    _db.session.commit()

    resp = client.post("/api/auth/login", json={"correo": correo, "password": "clave123"})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
