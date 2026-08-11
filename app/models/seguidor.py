from datetime import datetime, timezone
from app import db


class Seguidor(db.Model):
    __tablename__ = "seguidores"

    id = db.Column(db.Integer, primary_key=True)
    seguidor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    seguido_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("seguidor_id", "seguido_id", name="uq_seguidor_seguido"),
    )
