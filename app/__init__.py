from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class="config.Config"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)  # habilita llamadas desde la app móvil

    # Registro de blueprints (rutas)
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.messages import messages_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Importa los modelos para que Flask-Migrate los detecte
    from app.models import usuario, publicacion, comentario, like, mensaje  # noqa

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app
