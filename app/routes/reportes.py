from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.reporte import Reporte, TipoObjetivoReporte

reportes_bp = Blueprint("reportes", __name__)

MOTIVO_MAX = 500


@reportes_bp.route("", methods=["POST"])
@jwt_required()
def crear_reporte():
    reportante_id = int(get_jwt_identity())
    data = request.get_json() or {}

    tipo_objetivo = data.get("tipo_objetivo")
    objetivo_id = data.get("objetivo_id")
    motivo = (data.get("motivo") or "").strip()

    if tipo_objetivo not in (TipoObjetivoReporte.PUBLICACION, TipoObjetivoReporte.COMENTARIO):
        return jsonify({"error": "tipo_objetivo inválido"}), 400
    if not objetivo_id:
        return jsonify({"error": "objetivo_id es obligatorio"}), 400
    if len(motivo) > MOTIVO_MAX:
        return jsonify({"error": f"El motivo no puede superar los {MOTIVO_MAX} caracteres"}), 400

    reporte = Reporte(
        reportante_id=reportante_id,
        tipo_objetivo=tipo_objetivo,
        objetivo_id=objetivo_id,
        motivo=motivo or None,
    )
    db.session.add(reporte)
    db.session.commit()
    return jsonify(reporte.to_dict()), 201
