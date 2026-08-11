import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _url_base_datos():
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    # Render (y otros hosts) entregan "postgres://", pero SQLAlchemy 2.x exige
    # el dialecto explícito "postgresql://".
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
    SQLALCHEMY_DATABASE_URI = _url_base_datos()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dominio institucional permitido para el registro (ajusta al de tu universidad)
    DOMINIO_INSTITUCIONAL = os.environ.get("DOMINIO_INSTITUCIONAL", "usanjose.edu.co")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "cambia-esta-clave-jwt")
    JWT_ACCESS_TOKEN_EXPIRES_HORAS = 12

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(BASE_DIR, "instance", "uploads")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB por archivo

    # Orígenes permitidos para CORS, separados por coma. "*" (default) permite
    # cualquier origen — ajusta esto antes de desplegar a producción.
    ORIGENES_PERMITIDOS = os.environ.get("ORIGENES_PERMITIDOS", "*")

    # Si está seteada, app/routes/uploads.py sube las imágenes a Cloudinary en
    # vez de guardarlas en disco local (necesario en hosts sin disco
    # persistente, como el plan gratuito de Render). Formato:
    # cloudinary://<api_key>:<api_secret>@<cloud_name>
    CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")

    # Si está seteada al arrancar la app y ese correo ya existe, se promueve
    # automáticamente a admin. Sustituye a `flask crear-admin` en hosts sin
    # acceso a shell (como el plan gratuito de Render).
    ADMIN_BOOTSTRAP_EMAIL = os.environ.get("ADMIN_BOOTSTRAP_EMAIL")
