from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario
from app.models.like import Like
from app.models.usuario import RolUsuario

posts_bp = Blueprint("posts", __name__)


@posts_bp.route("", methods=["GET"])
@jwt_required()
def listar_publicaciones():
    """Feed general, con fijadas primero. Filtra por facultad/carrera con ?facultad=... """
    query = Publicacion.query
    facultad = request.args.get("facultad")
    if facultad:
        query = query.join(Publicacion.autor).filter_by(facultad=facultad)

    publicaciones = query.order_by(
        Publicacion.fijado.desc(), Publicacion.fecha_creacion.desc()
    ).all()

    return jsonify([p.to_dict() for p in publicaciones]), 200


@posts_bp.route("", methods=["POST"])
@jwt_required()
def crear_publicacion():
    usuario_id = int(get_jwt_identity())
    claims = get_jwt()
    data = request.get_json() or {}

    contenido = data.get("contenido", "").strip()
    if not contenido:
        return jsonify({"error": "El contenido no puede estar vacío"}), 400

    fijado = bool(data.get("fijado", False))
    # Solo docentes/admin pueden fijar publicaciones
    if fijado and claims.get("rol") not in (RolUsuario.DOCENTE, RolUsuario.ADMIN):
        fijado = False

    publicacion = Publicacion(
        usuario_id=usuario_id,
        contenido=contenido,
        imagen_url=data.get("imagen_url"),
        fijado=fijado,
    )
    db.session.add(publicacion)
    db.session.commit()

    return jsonify(publicacion.to_dict()), 201


@posts_bp.route("/<int:publicacion_id>", methods=["DELETE"])
@jwt_required()
def eliminar_publicacion(publicacion_id):
    usuario_id = int(get_jwt_identity())
    claims = get_jwt()
    publicacion = Publicacion.query.get_or_404(publicacion_id)

    if publicacion.usuario_id != usuario_id and claims.get("rol") != RolUsuario.ADMIN:
        return jsonify({"error": "No tienes permiso para eliminar esta publicación"}), 403

    db.session.delete(publicacion)
    db.session.commit()
    return jsonify({"mensaje": "Publicación eliminada"}), 200


@posts_bp.route("/<int:publicacion_id>/comentarios", methods=["POST"])
@jwt_required()
def comentar(publicacion_id):
    usuario_id = int(get_jwt_identity())
    data = request.get_json() or {}
    contenido = data.get("contenido", "").strip()

    if not contenido:
        return jsonify({"error": "El comentario no puede estar vacío"}), 400

    Publicacion.query.get_or_404(publicacion_id)

    comentario = Comentario(
        publicacion_id=publicacion_id, usuario_id=usuario_id, contenido=contenido
    )
    db.session.add(comentario)
    db.session.commit()

    return jsonify(comentario.to_dict()), 201


@posts_bp.route("/<int:publicacion_id>/comentarios", methods=["GET"])
@jwt_required()
def listar_comentarios(publicacion_id):
    Publicacion.query.get_or_404(publicacion_id)
    comentarios = (
        Comentario.query.filter_by(publicacion_id=publicacion_id)
        .order_by(Comentario.fecha_creacion.asc())
        .all()
    )
    return jsonify([c.to_dict() for c in comentarios]), 200


@posts_bp.route("/<int:publicacion_id>/like", methods=["POST"])
@jwt_required()
def dar_like(publicacion_id):
    usuario_id = int(get_jwt_identity())
    Publicacion.query.get_or_404(publicacion_id)

    existente = Like.query.filter_by(
        publicacion_id=publicacion_id, usuario_id=usuario_id
    ).first()

    if existente:
        db.session.delete(existente)
        db.session.commit()
        return jsonify({"mensaje": "Like retirado", "like": False}), 200

    like = Like(publicacion_id=publicacion_id, usuario_id=usuario_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({"mensaje": "Like agregado", "like": True}), 201
