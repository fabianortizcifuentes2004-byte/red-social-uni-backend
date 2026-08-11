from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app import db
from app.models.mensaje import Mensaje

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("", methods=["POST"])
@jwt_required()
def enviar_mensaje():
    remitente_id = int(get_jwt_identity())
    data = request.get_json() or {}

    destinatario_id = data.get("destinatario_id")
    contenido = data.get("contenido", "").strip()

    if not destinatario_id or not contenido:
        return jsonify({"error": "destinatario_id y contenido son obligatorios"}), 400

    mensaje = Mensaje(
        remitente_id=remitente_id, destinatario_id=destinatario_id, contenido=contenido
    )
    db.session.add(mensaje)
    db.session.commit()

    return jsonify(mensaje.to_dict()), 201


@messages_bp.route("/conversacion/<int:otro_usuario_id>", methods=["GET"])
@jwt_required()
def ver_conversacion(otro_usuario_id):
    usuario_id = int(get_jwt_identity())

    mensajes = (
        Mensaje.query.filter(
            or_(
                and_(Mensaje.remitente_id == usuario_id, Mensaje.destinatario_id == otro_usuario_id),
                and_(Mensaje.remitente_id == otro_usuario_id, Mensaje.destinatario_id == usuario_id),
            )
        )
        .order_by(Mensaje.fecha_creacion.asc())
        .all()
    )

    # Marca como leídos los mensajes recibidos
    for m in mensajes:
        if m.destinatario_id == usuario_id and not m.leido:
            m.leido = True
    db.session.commit()

    return jsonify([m.to_dict() for m in mensajes]), 200
