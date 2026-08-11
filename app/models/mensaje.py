from datetime import datetime, timezone
from app import db


class Mensaje(db.Model):
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    remitente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "remitente_id": self.remitente_id,
            "destinatario_id": self.destinatario_id,
            "contenido": self.contenido,
            "leido": self.leido,
            "fecha_creacion": self.fecha_creacion.isoformat(),
        }
