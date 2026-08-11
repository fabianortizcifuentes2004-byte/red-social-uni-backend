from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app import db, limiter
from app.models.mensaje import Mensaje
from app.models.usuario import Usuario

messages_bp = Blueprint("messages", __name__)

MENSAJE_MAX = 2000


@messages_bp.route("", methods=["POST"])
@jwt_required()
@limiter.limit("30 per minute")
def enviar_mensaje():
    remitente_id = int(get_jwt_identity())
    data = request.get_json() or {}

    destinatario_id = data.get("destinatario_id")
    contenido = data.get("contenido", "").strip()

    if not destinatario_id or not contenido:
        return jsonify({"error": "destinatario_id y contenido son obligatorios"}), 400
    if len(contenido) > MENSAJE_MAX:
        return jsonify({"error": f"El mensaje no puede superar los {MENSAJE_MAX} caracteres"}), 400

    mensaje = Mensaje(
        remitente_id=remitente_id, destinatario_id=destinatario_id, contenido=contenido
    )
    db.session.add(mensaje)
    db.session.commit()

    return jsonify(mensaje.to_dict()), 201


@messages_bp.route("/conversaciones", methods=["GET"])
@jwt_required()
def listar_conversaciones():
    usuario_id = int(get_jwt_identity())

    mensajes = (
        Mensaje.query.filter(
            or_(Mensaje.remitente_id == usuario_id, Mensaje.destinatario_id == usuario_id)
        )
        .order_by(Mensaje.fecha_creacion.desc())
        .all()
    )

    conversaciones = {}
    for m in mensajes:
        otro_id = m.destinatario_id if m.remitente_id == usuario_id else m.remitente_id
        if otro_id not in conversaciones:
            conversaciones[otro_id] = {
                "usuario_id": otro_id,
                "ultimo_mensaje": m.contenido,
                "fecha_ultimo_mensaje": m.fecha_creacion.isoformat(),
                "no_leidos": 0,
            }
        if m.destinatario_id == usuario_id and not m.leido:
            conversaciones[otro_id]["no_leidos"] += 1

    otros_ids = list(conversaciones.keys())
    usuarios_por_id = {
        u.id: u for u in Usuario.query.filter(Usuario.id.in_(otros_ids)).all()
    } if otros_ids else {}

    resultado = [
        {**datos, "usuario": usuarios_por_id[otro_id].to_dict()}
        for otro_id, datos in conversaciones.items()
        if otro_id in usuarios_por_id
    ]

    return jsonify(resultado), 200


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
