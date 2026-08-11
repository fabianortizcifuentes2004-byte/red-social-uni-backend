from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario
from app.models.seguidor import Seguidor

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
    solicitante_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)

    datos = usuario.to_dict()
    datos["total_seguidores"] = Seguidor.query.filter_by(seguido_id=usuario_id).count()
    datos["total_siguiendo"] = Seguidor.query.filter_by(seguidor_id=usuario_id).count()
    datos["lo_sigues"] = (
        usuario_id != solicitante_id
        and Seguidor.query.filter_by(seguidor_id=solicitante_id, seguido_id=usuario_id).first()
        is not None
    )
    return jsonify(datos), 200


@users_bp.route("", methods=["GET"])
@jwt_required()
def buscar_usuarios():
    """Búsqueda por nombre y/o filtros: /api/users?q=juan&facultad=...&carrera=..."""
    q = request.args.get("q", "").strip()
    facultad = request.args.get("facultad", "").strip()
    carrera = request.args.get("carrera", "").strip()

    query = Usuario.query.filter_by(activo=True)
    if q:
        query = query.filter(Usuario.nombre_completo.ilike(f"%{q}%"))
    if facultad:
        query = query.filter(Usuario.facultad.ilike(f"%{facultad}%"))
    if carrera:
        query = query.filter(Usuario.carrera.ilike(f"%{carrera}%"))

    usuarios = query.limit(30).all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@users_bp.route("/<int:usuario_id>/seguir", methods=["POST"])
@jwt_required()
def seguir_usuario(usuario_id):
    seguidor_id = int(get_jwt_identity())
    Usuario.query.get_or_404(usuario_id)

    if seguidor_id == usuario_id:
        return jsonify({"error": "No puedes seguirte a ti mismo"}), 400

    existente = Seguidor.query.filter_by(seguidor_id=seguidor_id, seguido_id=usuario_id).first()
    if existente:
        return jsonify({"error": "Ya sigues a este usuario"}), 409

    seguimiento = Seguidor(seguidor_id=seguidor_id, seguido_id=usuario_id)
    db.session.add(seguimiento)
    db.session.commit()
    return jsonify({"mensaje": "Ahora sigues a este usuario"}), 201


@users_bp.route("/<int:usuario_id>/seguir", methods=["DELETE"])
@jwt_required()
def dejar_de_seguir(usuario_id):
    seguidor_id = int(get_jwt_identity())

    existente = Seguidor.query.filter_by(seguidor_id=seguidor_id, seguido_id=usuario_id).first()
    if existente:
        db.session.delete(existente)
        db.session.commit()

    return jsonify({"mensaje": "Dejaste de seguir a este usuario"}), 200


@users_bp.route("/<int:usuario_id>/seguidores", methods=["GET"])
@jwt_required()
def listar_seguidores(usuario_id):
    Usuario.query.get_or_404(usuario_id)
    seguidores = (
        Usuario.query.join(Seguidor, Seguidor.seguidor_id == Usuario.id)
        .filter(Seguidor.seguido_id == usuario_id)
        .all()
    )
    return jsonify([u.to_dict() for u in seguidores]), 200


@users_bp.route("/<int:usuario_id>/siguiendo", methods=["GET"])
@jwt_required()
def listar_siguiendo(usuario_id):
    Usuario.query.get_or_404(usuario_id)
    siguiendo = (
        Usuario.query.join(Seguidor, Seguidor.seguido_id == Usuario.id)
        .filter(Seguidor.seguidor_id == usuario_id)
        .all()
    )
    return jsonify([u.to_dict() for u in siguiendo]), 200
