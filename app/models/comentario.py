from datetime import datetime, timezone
from app import db


class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.Integer, primary_key=True)
    publicacion_id = db.Column(db.Integer, db.ForeignKey("publicaciones.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    contenido = db.Column(db.String(500), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "publicacion_id": self.publicacion_id,
            "usuario_id": self.usuario_id,
            "autor": self.autor.nombre_completo,
            "contenido": self.contenido,
            "fecha_creacion": self.fecha_creacion.isoformat(),
        }
