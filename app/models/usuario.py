from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class RolUsuario:
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"
    ADMIN = "admin"


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default=RolUsuario.ESTUDIANTE)
    facultad = db.Column(db.String(100), nullable=True)
    carrera = db.Column(db.String(100), nullable=True)
    foto_url = db.Column(db.String(255), nullable=True)
    biografia = db.Column(db.String(280), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)
    # Distingue una cuenta desactivada por un admin (baneo) de una que el
    # propio usuario cerró — ambas bloquean el login igual, pero el panel de
    # admin necesita poder diferenciarlas.
    eliminado_por_usuario = db.Column(db.Boolean, nullable=False, default=False)
    # Un solo token por usuario (el último dispositivo en loguearse gana) —
    # suficiente para la escala de este proyecto, no soporta multi-dispositivo.
    push_token = db.Column(db.String(255), nullable=True)

    publicaciones = db.relationship("Publicacion", backref="autor", lazy="dynamic")
    comentarios = db.relationship("Comentario", backref="autor", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre_completo": self.nombre_completo,
            "correo": self.correo,
            "rol": self.rol,
            "facultad": self.facultad,
            "carrera": self.carrera,
            "foto_url": self.foto_url,
            "biografia": self.biografia,
            "activo": self.activo,
            "eliminado_por_usuario": self.eliminado_por_usuario,
        }
