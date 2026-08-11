from datetime import datetime, timezone
from app import db


class Bloqueo(db.Model):
    __tablename__ = "bloqueos"

    id = db.Column(db.Integer, primary_key=True)
    bloqueador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    bloqueado_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("bloqueador_id", "bloqueado_id", name="uq_bloqueador_bloqueado"),
    )


def existe_bloqueo(usuario_a_id, usuario_b_id):
    """True si alguno de los dos usuarios bloqueó al otro, en cualquier dirección."""
    return (
        Bloqueo.query.filter_by(bloqueador_id=usuario_a_id, bloqueado_id=usuario_b_id).first()
        is not None
        or Bloqueo.query.filter_by(bloqueador_id=usuario_b_id, bloqueado_id=usuario_a_id).first()
        is not None
    )
