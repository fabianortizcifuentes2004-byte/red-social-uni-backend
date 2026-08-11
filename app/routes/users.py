from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario

users_bp = Blueprint("users", __name__)


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def mi_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario.to_dict()), 200


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def editar_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json() or {}

    for campo in ("nombre_completo", "facultad", "carrera", "foto_url", "biografia"):
        if campo in data:
            setattr(usuario, campo, data[campo])

    db.session.commit()
    return jsonify(usuario.to_dict()), 200


@users_bp.route("/<int:usuario_id>", methods=["GET"])
@jwt_required()
def ver_perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario.to_dict()), 200


@users_bp.route("", methods=["GET"])
@jwt_required()
def buscar_usuarios():
    """Búsqueda simple por nombre: /api/users?q=juan"""
    q = request.args.get("q", "").strip()
    query = Usuario.query.filter_by(activo=True)
    if q:
        query = query.filter(Usuario.nombre_completo.ilike(f"%{q}%"))
    usuarios = query.limit(30).all()
    return jsonify([u.to_dict() for u in usuarios]), 200
