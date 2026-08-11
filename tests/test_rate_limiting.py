import tempfile
import shutil

from app import create_app, db as _db
from tests.conftest import TestConfig, registrar_y_loguear


def test_login_bloquea_tras_demasiados_intentos():
    """El resto de la suite corre con RATELIMIT_ENABLED=False (ver conftest.py)
    para no interferir entre tests; este test arma su propia app con el
    limiter activo desde el arranque para verificar que el límite corta."""

    class ConfigConLimite(TestConfig):
        RATELIMIT_ENABLED = True

    carpeta_uploads = tempfile.mkdtemp()
    ConfigConLimite.UPLOAD_FOLDER = carpeta_uploads
    app = create_app(ConfigConLimite)

    with app.app_context():
        _db.create_all()
        client = app.test_client()
        try:
            registrar_y_loguear(client)

            credenciales = {"correo": "ana@usanjose.edu.co", "password": "clave-incorrecta"}
            respuestas = [
                client.post("/api/auth/login", json=credenciales).status_code for _ in range(6)
            ]

            assert 401 in respuestas  # intentos fallidos normales
            assert 429 in respuestas  # el límite (5/min) corta antes del sexto intento
        finally:
            _db.session.remove()
            _db.drop_all()

    shutil.rmtree(carpeta_uploads, ignore_errors=True)
