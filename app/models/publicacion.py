from datetime import datetime, timezone
from app import db


class Publicacion(db.Model):
    __tablename__ = "publicaciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(255), nullable=True)
    fijado = db.Column(db.Boolean, default=False)  # avisos importantes de docentes
    editado = db.Column(db.Boolean, nullable=False, default=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    comentarios = db.relationship(
        "Comentario", backref="publicacion", lazy="dynamic", cascade="all, delete-orphan"
    )
    likes = db.relationship(
        "Like", backref="publicacion", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "autor": self.autor.nombre_completo,
            "rol_autor": self.autor.rol,
            "foto_autor": self.autor.foto_url,
            "contenido": self.contenido,
            "imagen_url": self.imagen_url,
            "fijado": self.fijado,
            "editado": self.editado,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "total_likes": self.likes.count(),
            "total_comentarios": self.comentarios.count(),
        }
