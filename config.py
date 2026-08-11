import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dominio institucional permitido para el registro (ajusta al de tu universidad)
    DOMINIO_INSTITUCIONAL = os.environ.get("DOMINIO_INSTITUCIONAL", "usanjose.edu.co")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "cambia-esta-clave-jwt")
    JWT_ACCESS_TOKEN_EXPIRES_HORAS = 12
