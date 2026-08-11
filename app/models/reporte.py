from datetime import datetime, timezone
from app import db


class TipoObjetivoReporte:
    PUBLICACION = "publicacion"
    COMENTARIO = "comentario"


class Reporte(db.Model):
    __tablename__ = "reportes"

    id = db.Column(db.Integer, primary_key=True)
    reportante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    tipo_objetivo = db.Column(db.String(20), nullable=False)
    objetivo_id = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(500), nullable=True)
    resuelto = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reportante = db.relationship("Usuario")

    def to_dict(self):
        return {
            "id": self.id,
            "reportante_id": self.reportante_id,
            "reportante": self.reportante.nombre_completo,
            "tipo_objetivo": self.tipo_objetivo,
            "objetivo_id": self.objetivo_id,
            "motivo": self.motivo,
            "resuelto": self.resuelto,
            "fecha_creacion": self.fecha_creacion.isoformat(),
        }
