from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])


def create_app(config_class="config.Config"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    origenes = app.config["ORIGENES_PERMITIDOS"]
    origenes = "*" if origenes == "*" else [o.strip() for o in origenes.split(",")]
    CORS(app, origins=origenes)  # habilita llamadas desde la app móvil

    # Registro de blueprints (rutas)
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.messages import messages_bp
    from app.routes.users import users_bp
    from app.routes.uploads import uploads_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Importa los modelos para que Flask-Migrate los detecte
    from app.models import usuario, publicacion, comentario, like, mensaje, seguidor  # noqa

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    from app.cli import registrar_comandos_cli

    registrar_comandos_cli(app)

    return app
